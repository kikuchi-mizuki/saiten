from fastapi import FastAPI, HTTPException, Depends, Header
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel
from typing import Dict, List, Optional, Tuple
import json
import pathlib
import re
import os
import requests
import jwt
import base64
import hashlib
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from supabase import create_client, Client

ROOT = pathlib.Path(__file__).resolve().parents[1]
SAMPLE_PATH = ROOT / "data" / "sample_comments.json"
PROMPTS_DIR = ROOT / "prompts"

# --- simple .env loader (no external deps)
def _load_local_env():
	env_path = ROOT / ".env"
	if not env_path.exists():
		return
	for line in env_path.read_text(encoding="utf-8").splitlines():
		line = line.strip()
		if not line or line.startswith("#"):
			continue
		if "=" in line:
			k, v = line.split("=", 1)
			k = k.strip()
			v = v.strip().strip('"').strip("'")
			os.environ.setdefault(k, v)

_load_local_env()

# Supabase client初期化
SUPABASE_URL = os.environ.get("SUPABASE_URL", "")
SUPABASE_ANON_KEY = os.environ.get("SUPABASE_ANON_KEY", "")
SUPABASE_JWT_SECRET = os.environ.get("SUPABASE_JWT_SECRET", "")

supabase: Optional[Client] = None
if SUPABASE_URL and SUPABASE_ANON_KEY:
	supabase = create_client(SUPABASE_URL, SUPABASE_ANON_KEY)

# JWT認証設定
security = HTTPBearer()

# 暗号化キー設定
ENCRYPTION_KEY_STR = os.environ.get("ENCRYPTION_KEY", "")

app = FastAPI(title="教授コメント自動化Bot API (MVP)")

# CORS設定 - Next.jsフロントエンドからのリクエストを許可
# 環境変数で許可ドメインを設定可能（本番環境対応）
ALLOWED_ORIGINS = os.environ.get("ALLOWED_ORIGINS", "").split(",") if os.environ.get("ALLOWED_ORIGINS") else []
default_origins = [
	"http://localhost:3000",
	"http://localhost:3001",
	"http://127.0.0.1:3000",
	"http://127.0.0.1:3001",
]
allowed_origins = default_origins + [origin.strip() for origin in ALLOWED_ORIGINS if origin.strip()]

app.add_middleware(
	CORSMiddleware,
	allow_origins=allowed_origins,
	allow_credentials=True,
	allow_methods=["*"],
	allow_headers=["*"],
)


# ===========================================
# データ暗号化・復号化機能
# ===========================================

class DataEncryption:
	"""AES-256-GCM によるデータ暗号化・復号化クラス"""

	def __init__(self, key_str: str):
		"""
		Args:
			key_str: 暗号化キー文字列（SHA-256でハッシュ化して32バイト鍵を生成）
		"""
		if not key_str:
			raise ValueError("Encryption key is not set")

		# キー文字列をSHA-256でハッシュ化して32バイトの鍵を生成
		self.key = hashlib.sha256(key_str.encode()).digest()
		self.aesgcm = AESGCM(self.key)

	def encrypt(self, plaintext: str) -> str:
		"""
		テキストを暗号化

		Args:
			plaintext: 暗号化する平文

		Returns:
			base64エンコードされた暗号文（nonce + ciphertext形式）
		"""
		if not plaintext:
			return ""

		# 12バイトのnonceを生成（GCMモードの推奨サイズ）
		nonce = os.urandom(12)

		# 暗号化
		plaintext_bytes = plaintext.encode('utf-8')
		ciphertext = self.aesgcm.encrypt(nonce, plaintext_bytes, None)

		# nonce + ciphertext を結合してbase64エンコード
		encrypted_data = nonce + ciphertext
		return base64.b64encode(encrypted_data).decode('utf-8')

	def decrypt(self, encrypted_str: str) -> str:
		"""
		暗号文を復号化

		Args:
			encrypted_str: base64エンコードされた暗号文

		Returns:
			復号化された平文
		"""
		if not encrypted_str:
			return ""

		try:
			# base64デコード
			encrypted_data = base64.b64decode(encrypted_str)

			# nonce（最初の12バイト）とciphertextを分離
			nonce = encrypted_data[:12]
			ciphertext = encrypted_data[12:]

			# 復号化
			plaintext_bytes = self.aesgcm.decrypt(nonce, ciphertext, None)
			return plaintext_bytes.decode('utf-8')

		except Exception as e:
			raise ValueError(f"Decryption failed: {str(e)}")


# 暗号化インスタンスを初期化
encryption: Optional[DataEncryption] = None
if ENCRYPTION_KEY_STR:
	try:
		encryption = DataEncryption(ENCRYPTION_KEY_STR)
	except Exception as e:
		print(f"Warning: Failed to initialize encryption: {e}")


# ===========================================
# JWT認証ミドルウェア
# ===========================================

async def verify_jwt(credentials: Optional[HTTPAuthorizationCredentials] = Depends(HTTPBearer(auto_error=False))) -> dict:
	"""
	JWT検証を行い、ユーザー情報を返す
	検証失敗時は401エラーを返す
	"""
	# JWT検証を無効化する環境変数（開発用）
	if os.environ.get("DISABLE_AUTH", "0") == "1":
		return {"user_id": "00000000-0000-0000-0000-000000000000", "email": "dev@example.com"}

	# 認証が有効な場合、credentialsが必須
	if not credentials:
		raise HTTPException(
			status_code=401,
			detail="Not authenticated"
		)

	token = credentials.credentials

	try:
		# Supabaseが設定されていない場合はエラー
		if not SUPABASE_URL or not SUPABASE_JWT_SECRET:
			raise HTTPException(
				status_code=500,
				detail="Supabase configuration is missing"
			)

		# JWTをデコード・検証
		payload = jwt.decode(
			token,
			SUPABASE_JWT_SECRET,
			algorithms=["HS256"],
			audience="authenticated",
			options={"verify_exp": True}
		)

		# ユーザーIDを取得
		user_id = payload.get("sub")
		email = payload.get("email")

		if not user_id:
			raise HTTPException(
				status_code=401,
				detail="Invalid token: user_id not found"
			)

		return {
			"user_id": user_id,
			"email": email,
			"payload": payload
		}

	except jwt.ExpiredSignatureError:
		raise HTTPException(
			status_code=401,
			detail="Token has expired"
		)
	except jwt.InvalidTokenError as e:
		raise HTTPException(
			status_code=401,
			detail=f"Invalid token: {str(e)}"
		)
	except Exception as e:
		raise HTTPException(
			status_code=401,
			detail=f"Authentication failed: {str(e)}"
		)


class GenerateOptions(BaseModel):
	length: Optional[int] = 400
	tone: Optional[str] = "温かめ"


class GenerateRequest(BaseModel):
	text: str
	type: str  # 'reflection' | 'final'
	rubric: Optional[Dict[str, int]] = None
	options: Optional[GenerateOptions] = None


class GenerateResponse(BaseModel):
	ai_comment: str
	used_refs: List[str] = []
	tokens: Optional[int] = None
	latency_ms: Optional[int] = None


# 追加: 直接テキストを受け取り、ドラフト＋Rubricを返すMVP用
class DirectGenRequest(BaseModel):
	text: str
	type: Optional[str] = "reflection"


# 参照例管理用のモデル
class ReferenceExample(BaseModel):
	id: str
	type: str  # 'reflection' | 'final'
	text: str
	tags: List[str]
	source: str


class ReferenceCreateRequest(BaseModel):
	type: str  # 'reflection' | 'final'
	text: str
	tags: List[str]
	source: Optional[str] = "professor_custom"


class ReferenceUpdateRequest(BaseModel):
	type: Optional[str] = None
	text: Optional[str] = None
	tags: Optional[List[str]] = None
	source: Optional[str] = None


# ===========================================
# PII検出・マスキング機能
# ===========================================

class PIIMatch(BaseModel):
	"""PII検出結果"""
	type: str  # 'name', 'student_id', 'email', 'phone'
	text: str
	start: int
	end: int


class PIIDetector:
	"""個人情報検出・マスキングクラス"""

	def __init__(self):
		# 日本語氏名パターン（姓・名の組み合わせ）
		self.name_pattern = re.compile(
			r'[一-龯ぁ-んァ-ヶ]{1,5}\s*[一-龯ぁ-んァ-ヶ]{1,5}'
		)

		# 学籍番号パターン（数字・英数字の組み合わせ）
		self.student_id_pattern = re.compile(
			r'\b[A-Z]?\d{5,10}\b'
		)

		# メールアドレスパターン
		self.email_pattern = re.compile(
			r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
		)

		# 電話番号パターン（ハイフン有無両対応）
		self.phone_pattern = re.compile(
			r'\b0\d{1,4}[-\s]?\d{1,4}[-\s]?\d{4}\b'
		)

	def detect(self, text: str) -> List[PIIMatch]:
		"""PIIを検出"""
		matches = []

		# メールアドレス検出（優先度高）
		for match in self.email_pattern.finditer(text):
			matches.append(PIIMatch(
				type='email',
				text=match.group(),
				start=match.start(),
				end=match.end()
			))

		# 電話番号検出
		for match in self.phone_pattern.finditer(text):
			matches.append(PIIMatch(
				type='phone',
				text=match.group(),
				start=match.start(),
				end=match.end()
			))

		# 学籍番号検出
		for match in self.student_id_pattern.finditer(text):
			# メールアドレスや電話番号と重複しないかチェック
			overlap = any(
				m.start <= match.start() < m.end or m.start < match.end() <= m.end
				for m in matches
			)
			if not overlap:
				matches.append(PIIMatch(
					type='student_id',
					text=match.group(),
					start=match.start(),
					end=match.end()
				))

		# 氏名検出（優先度低、他と重複しない場合のみ）
		for match in self.name_pattern.finditer(text):
			# 他のPIIと重複しないかチェック
			overlap = any(
				m.start <= match.start() < m.end or m.start < match.end() <= m.end
				for m in matches
			)
			if not overlap:
				# 一般的な単語を除外（簡易版）
				if match.group() not in ['私は', '自分', '学生', '教授', '先生']:
					matches.append(PIIMatch(
						type='name',
						text=match.group(),
						start=match.start(),
						end=match.end()
					))

		# 位置順にソート
		matches.sort(key=lambda m: m.start)
		return matches

	def mask(self, text: str, matches: List[PIIMatch]) -> str:
		"""PIIをマスキング"""
		if not matches:
			return text

		# 後ろから置換（インデックスがずれないように）
		result = text
		for match in reversed(matches):
			mask_text = {
				'name': '[氏名]',
				'student_id': '[学籍番号]',
				'email': '[メールアドレス]',
				'phone': '[電話番号]',
			}.get(match.type, '[個人情報]')

			result = result[:match.start] + mask_text + result[match.end:]

		return result

	def detect_and_mask(self, text: str) -> Tuple[str, List[Dict]]:
		"""PII検出とマスキングを一括実行
		Returns: (masked_text, detected_pii_list)
		"""
		matches = self.detect(text)
		masked_text = self.mask(text, matches)

		# 検出結果をDictに変換
		detected_pii = [
			{
				'type': m.type,
				'text': m.text,
				'start': m.start,
				'end': m.end
			}
			for m in matches
		]

		return masked_text, detected_pii


def load_samples() -> List[Dict]:
	"""
	参照例を読み込む
	優先順位:
	1. Supabaseのknowledge_baseテーブルから読み込み
	2. ローカルのsample_comments.jsonから読み込み
	3. 空のリストを返す
	"""
	# Supabaseから読み込む
	if supabase:
		try:
			response = supabase.table("knowledge_base").select("reference_id, type, text, tags, source").execute()
			if response.data:
				# Supabaseのデータ形式をJSONファイル形式に変換
				samples = []
				for item in response.data:
					samples.append({
						"id": item.get("reference_id"),
						"type": item.get("type"),
						"text": item.get("text"),
						"tags": item.get("tags", []),
						"source": item.get("source", "professor_examples")
					})
				return samples
		except Exception as e:
			print(f"Supabaseからの参照例読み込みに失敗: {e}")
			# フォールバックしてローカルファイルを試す

	# ローカルファイルから読み込む（フォールバック）
	try:
		if SAMPLE_PATH.exists():
			return json.loads(SAMPLE_PATH.read_text(encoding="utf-8"))
	except Exception as e:
		print(f"ローカルファイルからの参照例読み込みに失敗: {e}")

	# 両方失敗した場合は空のリストを返す
	return []


def save_samples(samples: List[Dict]) -> None:
	"""
	参照例を保存（非推奨：後方互換性のため残す）

	注意: Railwayなどのクラウド環境ではファイル書き込みができないため、
	      Supabaseへの直接保存を推奨します。
	"""
	try:
		if SAMPLE_PATH.exists():
			SAMPLE_PATH.write_text(
				json.dumps(samples, ensure_ascii=False, indent=2),
				encoding="utf-8"
			)
	except Exception as e:
		print(f"警告: ローカルファイルへの保存に失敗しました: {e}")
		# ファイル書き込みに失敗してもエラーにしない（クラウド環境対応）


def tokenize(s: str) -> List[str]:
	return [t for t in s.replace("\n", " ").replace("、", " ").replace("。", " ").split() if t]


def jaccard(a: List[str], b: List[str]) -> float:
	set_a, set_b = set(a), set(b)
	if not set_a and not set_b:
		return 0.0
	return len(set_a & set_b) / max(1, len(set_a | set_b))


def retrieve_refs(text: str, doc_type: str, k: int = 2) -> List[str]:
	samples = load_samples()
	toks = tokenize(text)
	candidates = [s for s in samples if s.get("type") == ("reflection" if doc_type == "reflection" else "final")]
	scored = sorted(((jaccard(toks, tokenize(c.get("text", ""))), c.get("text", "")) for c in candidates), reverse=True)
	return [t for _, t in scored[:k]]


def load_prompt(doc_type: str) -> str:
	file = "reflection.txt" if doc_type == "reflection" else "final.txt"
	return (PROMPTS_DIR / file).read_text(encoding="utf-8")


def build_comment(req: GenerateRequest) -> GenerateResponse:
	refs = retrieve_refs(req.text, req.type, k=2)
	prefix = "○ " if req.type == "reflection" else ""
	length = req.options.length if req.options else 400
	tone = req.options.tone if req.options else "温かめ"
	rub = req.rubric or {}
	rub_text = ", ".join([f"{k}:{v}" for k, v in rub.items()]) if rub else ""

	intro = f"{prefix}入力内容を踏まえ、教授の語り口で下書きを提示します。"
	rationale = f"{prefix}参照例により文体の一貫性を担保し、次の一歩を示唆します。"
	cond = f"{prefix}目安文字数:{length}／トーン:{tone}。Rubric:{rub_text}" if rub_text else f"{prefix}目安文字数:{length}／トーン:{tone}。"

	body = "\n".join([intro, rationale, cond])
	if req.type == "final":
		body = "\n".join([
			"全体評価: 学びの接続と仮説の筋が良いと感じます。",
			"強み: 観察と意思決定の一貫性。",
			"改善: 撤退基準と実装順の明確化。",
			"総括: あり方に立脚し、次の一歩を具体化しましょう。",
		])

	return GenerateResponse(ai_comment=body, used_refs=refs, tokens=None, latency_ms=None)


# 追加: 簡易Rubric算出
RUBRIC_CATEGORIES = ["理解度", "論理性", "独自性", "実践性", "表現力"]


def simple_score(text: str) -> Dict[str, any]:
	"""Rubricスコアと理由を生成"""
	length = len(text)
	has_examples = any(k in text for k in ["具体", "事例", "例えば", "現場", "実装", "検証"])
	first_person = any(k in text for k in ["私は", "自分", "経験", "実体験"])
	logical_markers = sum(k in text for k in ["なぜ", "したがって", "一方で", "つまり", "前提", "仮説"])
	clarity = sum(text.count(sym) for sym in ["。", "、", "\n"]) > 3
	
	# スコア計算
	score_values = {
		"理解度": 3 + (1 if logical_markers >= 2 else 0),
		"論理性": 3 + (1 if logical_markers >= 3 else 0),
		"独自性": 3 + (1 if first_person else 0),
		"実践性": 3 + (1 if has_examples else 0),
		"表現力": 3 + (1 if clarity and length >= 200 else 0),
	}
	
	# スコアを1〜5の範囲に調整
	for k in list(score_values.keys()):
		score_values[k] = max(1, min(5, score_values[k]))
	
	# 理由を生成（より詳細で具体的な理由）
	reasons = {}
	
	# 理解度
	if logical_markers >= 3:
		reasons["理解度"] = "講義の重要概念（なぜ、仮説、前提など）を適切に理解し、論理的に整理されています"
	elif logical_markers >= 2:
		reasons["理解度"] = "講義内容の基本的な理解が見られます。論理的な整理をさらに深めると良いでしょう"
	else:
		reasons["理解度"] = "講義内容の理解を示す表現がやや不足しています。重要概念を明確にすると良いでしょう"
	
	# 論理性
	if logical_markers >= 3:
		reasons["論理性"] = "論理的なつながり（したがって、一方で、つまりなど）が明確で、主張と根拠が一貫しています"
	elif logical_markers >= 2:
		reasons["論理性"] = "論理的なつながりが見られます。主張と根拠の関係をより明確にすると良いでしょう"
	else:
		reasons["論理性"] = "論理的なつながりを示す表現が不足しています。主張と根拠の関係を整理すると良いでしょう"
	
	# 独自性
	if first_person:
		reasons["独自性"] = "自身の経験や実体験（私は、自分、経験など）が明確に示されており、独自の視点が見られます"
	else:
		reasons["独自性"] = "自身の経験や視点を示す表現が不足しています。実体験や具体例を追加すると良いでしょう"
	
	# 実践性
	if has_examples:
		reasons["実践性"] = "具体的な事例や実践的な内容（具体、事例、現場、実装など）が豊富に含まれており、実践性が高いです"
	else:
		reasons["実践性"] = "具体的な事例や実践的な内容がやや不足しています。実務への応用を具体的に示すと良いでしょう"
	
	# 表現力
	if clarity and length >= 500:
		reasons["表現力"] = "文章の構造が明確で、十分な分量があり、伝わりやすい表現になっています"
	elif clarity and length >= 200:
		reasons["表現力"] = "文章の構造は明確ですが、もう少し詳しく展開すると良いでしょう"
	else:
		reasons["表現力"] = "文章の構造や明快さを向上させる余地があります。段落分けや具体例を追加すると良いでしょう"
	
	# スコアと理由を結合した辞書を返す
	result = {}
	for category in ["理解度", "論理性", "独自性", "実践性", "表現力"]:
		result[category] = {
			"score": score_values[category],
			"reason": reasons[category]
		}
	
	return result


# 追加: 反射用ドラフト生成（非LLM）
_DEF_NEXT_STEP = [
	("仮説", "仮説→検証のループを週次で回し、撤退基準も一文で定義しましょう。"),
	("KPI", "先にKPIの定義域を合わせ、入力指標と出力指標を分けて議論しましょう。"),
	("顧客", "顧客の具体的な行動観察を一つ追加し、価値仮説の確度を高めましょう。"),
	("価格", "価格受容性の仮説を立て、小さなA/Bで一次検証してみましょう。"),
	("組織", "意思決定の責任境界を明確にし、実行の詰まりを先に外しましょう。"),
]


def summarize_head(text: str, limit: int = 110) -> str:
	clean = re.sub(r"\s+", " ", text)
	clean = clean.replace("\u3000", " ")
	if len(clean) <= limit:
		return clean
	return clean[:limit].rstrip() + "…"


def choose_next_step(text: str) -> str:
	for key, msg in _DEF_NEXT_STEP:
		if key in text:
			return msg
	return "次回は仮説の前提を言語化し、小さく検証できる単位に分解してみましょう。"


def generate_reflection_draft(text: str, refs: List[str], scores: Dict[str, any]) -> str:
	lead = summarize_head(text)
	insight = "哲学としての『あり方』と実務の往復を意識できています。参照例を踏まえ、意思決定の軸を一文で置きましょう。"
	if refs:
		insight = "参照例に近い論点が見られます。" + insight
	next_step = choose_next_step(text)
	return "\n".join([
		f"○ {lead}",
		f"○ {insight}",
		f"○ {next_step}",
	])


# 要約機能: 3形式（エグゼクティブサマリー、箇条書き、構造化）
def call_openai_summary(prompt: str, system_prompt: str = None) -> Tuple[Optional[str], Optional[str]]:
	"""要約生成用のOpenAI API呼び出し"""
	if not OPENAI_API_KEY:
		return None, "APIキーが設定されていません"
	try:
		messages = []
		if system_prompt:
			messages.append({"role": "system", "content": system_prompt})
		messages.append({"role": "user", "content": prompt})
		
		resp = requests.post(
			"https://api.openai.com/v1/chat/completions",
			headers={"Authorization": f"Bearer {OPENAI_API_KEY}", "Content-Type": "application/json"},
			json={
				"model": LLM_MODEL,
				"messages": messages,
				"temperature": 0.3,  # 要約は低いtemperatureで一貫性を保つ
				"max_tokens": 800,
			},
			timeout=30,
		)
		resp.raise_for_status()
		data = resp.json()
		content = data.get("choices", [{}])[0].get("message", {}).get("content")
		return content, None
	except requests.exceptions.Timeout:
		return None, "タイムアウト: API接続がタイムアウトしました"
	except requests.exceptions.RequestException as e:
		return None, f"APIエラー: {str(e)}"
	except Exception as e:
		return None, f"予期しないエラー: {str(e)}"


def generate_summary_llm(text: str) -> Tuple[Dict[str, any], bool]:
	"""LLMを使用してレポートの要約を要点ごとに整理した形式で生成
	Returns: (summary_dict, llm_actually_used)
	"""
	if not USE_LLM or not OPENAI_API_KEY:
		return generate_summary_fallback(text), False
	
	try:
		# 要点ごとに整理された要約を生成するプロンプト
		summary_prompt = f"""以下の学生レポートを読んで、要点がわかりやすく伝わるように要約してください。

【レポート】
{text}

【出力形式】
以下の形式で要約を作成してください:

[レポートの全体要約：レポートの目的、主要なテーマ、論点を分かりやすくまとめてください。読み手が内容をすぐに理解できるように、明確で簡潔な表現を心がけてください。]

[番号付きセクション（1️⃣, 2️⃣, 3️⃣...）で要点を整理：レポートの主要な論点や考察を3-5つのセクションに分けて説明する。
各セクションは以下の形式：
1️⃣ [セクション見出し]

[セクションの内容：重要なポイントを分かりやすく説明。必要に応じて箇条書きも使用可。]

最後に「結論」セクションを追加：
[結論]
[レポートの結論や総括：学生の主張や気づきをまとめる。]

【注意事項】
- 文体は「です・ます」調で統一してください
- 重要なキーワードや概念は**太字**で強調してください
- 各セクションは読みやすく、要点が明確になるように構成してください
- 原文の重要な論点や考察を漏らさず、分かりやすくまとめてください
- 読み手がレポートの内容をすぐに理解できるように、明確で具体的な表現を使ってください
- 見出し「📘要約」は含めないでください

要約を出力してください:"""
		
		summary_text, error = call_openai_summary(
			summary_prompt,
			system_prompt="あなたは学術的な要約を作成する専門家です。文章の本質を捉え、要点が明確で読みやすい要約を作成してください。レポートの主要な論点や考察を構造的に整理し、読者が短時間で内容を理解できるようにしてください。"
		)
		
		if not summary_text or error:
			return generate_summary_fallback(text), False
		
		# 要約テキストをクリーンアップ
		summary_clean = summary_text.strip()
		
		# 「📘要約」という見出しが含まれている場合は削除
		summary_clean = re.sub(r"^📘要約\s*\n\s*\n?", "", summary_clean, flags=re.MULTILINE)
		summary_clean = re.sub(r"📘要約\s*\n\s*\n?", "", summary_clean)
		summary_clean = summary_clean.strip()
		
		# 既存のフォーマットとの互換性のため、executiveフィールドにも全体要約を設定
		# 最初の段落をエグゼクティブサマリーとして抽出（番号付きセクションの前まで）
		executive_match = re.search(r"^(.*?)(?:\n\s*\n1️⃣|$)", summary_clean, re.DOTALL)
		if executive_match:
			executive = executive_match.group(1).strip()
		else:
			# フォールバック: 最初の200文字
			executive = summary_clean[:200].strip()
		
		# 箇条書き要約は、セクション見出しから抽出
		bullets = []
		section_matches = re.finditer(r"(\d+️⃣)\s+([^\n]+)", summary_clean)
		for match in section_matches:
			bullets.append(match.group(2).strip())
		if len(bullets) > 5:
			bullets = bullets[:5]
		
		# 構造化要約は、主要テーマと要点を抽出
		structured = {
			"主要テーマ": executive[:50] if executive else "経営戦略・実践的考察",
			"要点": executive[:100] if executive else summarize_head(text, limit=100),
			"考察の深さ": "中程度" if len(text) > 500 else "簡潔",
			"実践性": "高" if any(k in text for k in ["具体", "事例", "現場", "実装"]) else "中",
		}
		
		# 新しい形式の要約を返す（LLM使用成功）
		return {
			"executive": summary_clean,  # 全体の要約テキスト
			"bullets": bullets,
			"structured": structured,
			"formatted": summary_clean,  # フォーマット済み要約
		}, True  # LLMが正常に使用された
	except Exception as e:
		# エラー時はフォールバックに戻る
		return generate_summary_fallback(text), False


def generate_summary_fallback(text: str) -> Dict[str, any]:
	"""フォールバック: 簡易的な要約生成（LLM不使用）"""
	clean_text = re.sub(r"\s+", " ", text.strip())
	
	# エグゼクティブサマリー（200文字程度）
	executive = summarize_head(text, limit=200)
	if len(clean_text) > 200:
		executive += " 本レポートでは、具体的な事例や考察を通じて、実践的な視点が示されています。"
	
	# 箇条書き要約（主要ポイントを抽出）
	bullets = []
	sentences = re.split(r"[。\n]", clean_text)
	key_sentences = [s.strip() for s in sentences if len(s.strip()) > 20][:5]
	for i, sent in enumerate(key_sentences[:5], 1):
		if sent:
			bullets.append(f"{sent}。")
	
	# 構造化要約
	structured = {
		"主要テーマ": "経営戦略・実践的考察",
		"要点": summarize_head(text, limit=100),
		"考察の深さ": "中程度" if len(text) > 500 else "簡潔",
		"実践性": "高" if any(k in text for k in ["具体", "事例", "現場", "実装"]) else "中",
	}
	
	# フォールバックも新しい形式に合わせる（簡易版）
	summary_formatted = f"""{executive}

1️⃣ 主要な論点

{bullets[0] if bullets else "本レポートでは、経営戦略に関する考察が行われています。"}

2️⃣ 実践的な視点

本レポートでは、具体的な事例や考察を通じて、実践的な視点が示されています。

[結論]

{executive}
"""
	
	return {
		"executive": summary_formatted,  # 新しい形式に対応
		"bullets": bullets,
		"structured": structured,
		"formatted": summary_formatted,
	}


def generate_summary(text: str) -> Tuple[Dict[str, any], bool, Optional[str]]:
	"""レポートの要約を3形式で生成（常にLLM使用）
	Returns: (summary_dict, llm_used_for_summary, error_message)
	"""
	if not OPENAI_API_KEY:
		error_msg = "要約生成にはOpenAI APIキーが必要です。環境変数OPENAI_API_KEYを設定してください。"
		return {
			"executive": error_msg,
			"bullets": [],
			"structured": {},
			"formatted": error_msg,
		}, False, error_msg
	
	if not USE_LLM:
		error_msg = "LLMが無効になっています。環境変数USE_LLM=1を設定してください。"
		return {
			"executive": error_msg,
			"bullets": [],
			"structured": {},
			"formatted": error_msg,
		}, False, error_msg
	
	try:
		summary_result, llm_used = generate_summary_llm(text)
		return summary_result, llm_used, None
	except Exception as e:
		error_msg = f"要約生成中にエラーが発生しました: {str(e)}"
		return {
			"executive": error_msg,
			"bullets": [],
			"structured": {},
			"formatted": error_msg,
		}, False, error_msg


# LLM連携（OpenAI API）: 環境変数で制御
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")
USE_LLM = os.environ.get("USE_LLM", "0") in ("1", "true", "TRUE", "on")
LLM_MODEL = os.environ.get("LLM_MODEL", "gpt-4o-mini")


def build_llm_prompt(text: str, doc_type: str, refs: List[str], scores: Dict[str, any]) -> str:
	base = load_prompt("reflection" if doc_type == "reflection" else "final")

	# 参照例を整形
	refs_text_list = []
	for i, ref in enumerate(refs, 1):
		if ref:
			# JSONのエスケープされた改行文字（\\n）を実際の改行に変換
			ref_normalized = ref.replace("\\n", "\n")
			refs_text_list.append(f"- {ref_normalized}")

	refs_text = "\n".join(refs_text_list) if refs_text_list else "(参照なし)"

	# scoresの形式を確認（新しい形式: {"score": int, "reason": str} または 古い形式: int）
	scores_list = []
	for category in ["理解度", "論理性", "独自性", "実践性", "表現力"]:
		value = scores.get(category, {})
		if isinstance(value, dict):
			score_val = value.get("score", 0)
			scores_list.append(f"{category}:{score_val}")
		else:
			scores_list.append(f"{category}:{value}")
	scores_text = ", ".join(scores_list) if scores_list else ""

	# 参照例がある場合、教授の思考パターンを学習するように促す
	if refs_text_list:
		refs_header = """【教授の過去コメント例（深く学習してください）】
以下は、教授が実際に書いた過去のコメントです。
これらから教授の「評価基準」「指導方針」「思考パターン」を深く理解し、
同じ考え方・同じ視点で今回のレポートにコメントしてください：

"""
		refs_section = f"{refs_header}{refs_text}\n"
	else:
		refs_section = "【参照例】\n（参照例なし：あなたの専門知識と教育経験に基づいてコメントしてください）\n\n"

	return (
		f"{base}\n\n{refs_section}"
		f"【Rubric所感（参考情報）】\n{scores_text}\n\n"
		f"【今回のレポート（これに対してコメントを作成してください）】\n{text}\n"
	)


def call_openai(prompt: str, max_tokens: int = 500, system_message: str = None) -> Tuple[Optional[str], Optional[str]]:
	"""OpenAI APIを呼び出し、結果とエラーを返す
	Args:
		prompt: ユーザープロンプト
		max_tokens: 最大トークン数（デフォルト500、参照例に応じて動的に調整）
		system_message: システムメッセージ（デフォルトは標準のメッセージ）
	"""
	if not OPENAI_API_KEY:
		return None, "APIキーが設定されていません"
	
	if system_message is None:
		system_message = """あなたは経営戦略論の教授です。
学生が提出したレポートに対してコメントを書く立場です。

【絶対に守るべき立場】
✅ あなた（教授）→ 学生へのコメント
❌ 学生 → 教授へのお礼や感謝

【絶対に使ってはいけない表現（NG例）】
❌「レポートをお読みいただき、ありがとうございます」
❌「ご意見ありがとうございます」
❌「お読みいただき」
❌「いただき」「くださり」（学生→教授の表現）

【必ず使うべき表現（OK例）】
✅「レポートを拝読しました」「レポートを読みました」
✅「〜と解釈しました」「〜が見えます」「〜を感じます」
✅「〜をおすすめします」「〜を意識してみてください」
✅「次回も是非議論したいと思います」

【重要な指示】
- 提供される「参照例」は、あなた（教授）が過去に実際に書いたコメントです
- 参照例の「文体」「語り口」「表現パターン」を厳密に学習し、同じスタイルで書いてください
- 参照例で使われている表現を積極的に使用してください
- 参照例で重視していたポイント（例：仮説検証、実践性、あり方と実務の往復）を今回も同じように重視してください
- 敬意と温かさを保ち、1つのまとまった文章ブロックとして出力してください

【文字数制限（絶対厳守）】
- 150文字以上250文字以内で出力してください
- 参照例の平均文字数は157文字です。これを参考にしてください
- 250文字を超えないように特に注意してください"""
	
	try:
		resp = requests.post(
			"https://api.openai.com/v1/chat/completions",
			headers={"Authorization": f"Bearer {OPENAI_API_KEY}", "Content-Type": "application/json"},
			json={
				"model": LLM_MODEL,
				"messages": [
					{"role": "system", "content": system_message},
					{"role": "user", "content": prompt},
				],
				"temperature": 0.3,
				"max_tokens": max_tokens,
			},
			timeout=30,
		)
		resp.raise_for_status()
		data = resp.json()
		content = data.get("choices", [{}])[0].get("message", {}).get("content")
		return content, None
	except requests.exceptions.Timeout:
		return None, "タイムアウト: API接続がタイムアウトしました"
	except requests.exceptions.RequestException as e:
		return None, f"APIエラー: {str(e)}"
	except Exception as e:
		return None, f"予期しないエラー: {str(e)}"


@app.post("/generate", response_model=GenerateResponse)
async def generate(req: GenerateRequest, user: dict = Depends(verify_jwt)) -> GenerateResponse:
	return build_comment(req)


# 直接生成エンドポイント
@app.post("/generate_direct")
async def generate_direct(req: DirectGenRequest, user: dict = Depends(verify_jwt)):
	doc_type = (req.type or "reflection")

	# 1. PII検出・マスキング
	pii_detector = PIIDetector()
	masked_text, detected_pii = pii_detector.detect_and_mask(req.text)

	# 2. マスキング後のテキストで処理を実行
	refs = retrieve_refs(masked_text, doc_type, k=2)
	scores = simple_score(masked_text)
	llm_used = False
	llm_error = None
	draft = None
	
	# max_tokensとsystem_messageを設定（200-300字固定）
	max_tokens = 600  # 200-300字 ≈ 400-600トークン
	system_message = """あなたは経営戦略論の教授です。
あなたの役割は、学生のレポートを深く理解し、教授としての専門知識と教育経験に基づいてコメントを作成することです。

重要な指示：
- 提供される「参照例」は、あなた（教授）が過去に実際に書いたコメントです
- 参照例から、あなた自身の「評価基準」「指導方針」「思考パターン」を思い出してください
- 単に文体を真似るのではなく、同じ考え方・同じ視点でコメントを作成してください
- 参照例で重視していたポイント（例：仮説検証、実践性、あり方と実務の往復）を今回も同じように重視してください
- 敬意と温かさを保ち、1つのまとまった文章ブロックとして出力してください"""
	
	# 3. コメント生成（マスキング後のテキストを使用）
	if USE_LLM and os.environ.get("OPENAI_API_KEY"):
		prompt = build_llm_prompt(masked_text, doc_type, refs, scores)
		draft, llm_error = call_openai(prompt, max_tokens=max_tokens, system_message=system_message)
		llm_used = draft is not None and llm_error is None
	if not draft:
		if doc_type == "reflection":
			draft = generate_reflection_draft(masked_text, refs, scores)
		else:
			draft = "\n".join([
				"全体評価: 学びの接続と仮説の筋が見られます。",
				"強み: 現場観察の具体性。",
				"改善: 指標・撤退基準の明確化。",
				"総括: あり方に立脚し、次の一歩を具体化しましょう。",
			])

	# 4. 要約生成（常にLLM使用、マスキング後のテキストを使用）
	summary, summary_llm_used, summary_error = generate_summary(masked_text)

	return {
		"report_id": None,
		"feedback_id": None,
		"ai_comment": draft,
		"rubric": scores,
		"summary": summary,
		"used_refs": refs,
		"llm_used": llm_used,
		"llm_error": llm_error,
		"summary_llm_used": summary_llm_used,  # 要約生成でLLMが使われたか
		"summary_error": summary_error,  # 要約生成のエラーメッセージ（あれば）
		"masked_text": masked_text,  # マスキング後のテキスト
		"detected_pii": detected_pii,  # 検出されたPII情報
		"pii_count": len(detected_pii),  # 検出されたPII数
	}


@app.get("/")
async def root():
	return {
		"message": "教授コメント自動化Bot API (MVP)",
		"version": "1.0.0",
		"status": "running",
		"endpoints": {
			"health": "/health",
			"generate": "/generate_direct",
			"stats": "/stats",
			"references": "/references"
		}
	}


@app.get("/health")
async def health():
	return {"ok": True}


@app.get("/debug/env")
async def debug_env():
	"""デバッグ用: 環境変数の確認"""
	return {
		"DISABLE_AUTH": os.environ.get("DISABLE_AUTH", "not set"),
		"SUPABASE_URL_set": bool(os.environ.get("SUPABASE_URL")),
		"OPENAI_API_KEY_set": bool(os.environ.get("OPENAI_API_KEY")),
		"supabase_connected": supabase is not None
	}


# ===========================================
# 暗号化・復号化エンドポイント
# ===========================================

class EncryptRequest(BaseModel):
	text: str


class EncryptResponse(BaseModel):
	encrypted_text: str


class DecryptRequest(BaseModel):
	encrypted_text: str


class DecryptResponse(BaseModel):
	text: str


@app.post("/encrypt", response_model=EncryptResponse)
async def encrypt_text(req: EncryptRequest, user: dict = Depends(verify_jwt)) -> EncryptResponse:
	"""テキストを暗号化"""
	if not encryption:
		raise HTTPException(status_code=500, detail="Encryption is not configured")

	try:
		encrypted = encryption.encrypt(req.text)
		return EncryptResponse(encrypted_text=encrypted)
	except Exception as e:
		raise HTTPException(status_code=500, detail=f"Encryption failed: {str(e)}")


@app.post("/decrypt", response_model=DecryptResponse)
async def decrypt_text(req: DecryptRequest, user: dict = Depends(verify_jwt)) -> DecryptResponse:
	"""暗号文を復号化"""
	if not encryption:
		raise HTTPException(status_code=500, detail="Encryption is not configured")

	try:
		decrypted = encryption.decrypt(req.encrypted_text)
		return DecryptResponse(text=decrypted)
	except Exception as e:
		raise HTTPException(status_code=500, detail=f"Decryption failed: {str(e)}")


# ===========================================
# 統計情報エンドポイント
# ===========================================

class StatsResponse(BaseModel):
	total_feedbacks: int
	avg_rubric_scores: Dict[str, float]
	avg_edit_time_seconds: Optional[float]
	avg_satisfaction_score: Optional[float]


@app.get("/stats", response_model=StatsResponse)
async def get_stats(user: dict = Depends(verify_jwt)) -> StatsResponse:
	"""ユーザーの統計情報を取得"""
	if not supabase:
		raise HTTPException(status_code=500, detail="Supabase is not configured")

	user_id = user["user_id"]

	try:
		# feedbacks テーブルから統計情報を取得
		response = supabase.table("feedbacks")\
			.select("rubric, edit_time_seconds, satisfaction_score")\
			.eq("user_id", user_id)\
			.execute()

		feedbacks = response.data

		if not feedbacks or len(feedbacks) == 0:
			# データがない場合はゼロ値を返す
			return StatsResponse(
				total_feedbacks=0,
				avg_rubric_scores={
					"理解度": 0.0,
					"論理性": 0.0,
					"独自性": 0.0,
					"実践性": 0.0,
					"表現力": 0.0,
				},
				avg_edit_time_seconds=None,
				avg_satisfaction_score=None,
			)

		# 総数
		total_feedbacks = len(feedbacks)

		# Rubric平均点数を計算
		rubric_sums = {
			"理解度": 0.0,
			"論理性": 0.0,
			"独自性": 0.0,
			"実践性": 0.0,
			"表現力": 0.0,
		}
		rubric_counts = {
			"理解度": 0,
			"論理性": 0,
			"独自性": 0,
			"実践性": 0,
			"表現力": 0,
		}

		edit_time_sum = 0
		edit_time_count = 0
		satisfaction_sum = 0
		satisfaction_count = 0

		for feedback in feedbacks:
			# Rubricスコアを集計
			rubric = feedback.get("rubric", {})
			for category in ["理解度", "論理性", "独自性", "実践性", "表現力"]:
				if category in rubric:
					rubric_item = rubric[category]
					if isinstance(rubric_item, dict) and "score" in rubric_item:
						score = rubric_item["score"]
						rubric_sums[category] += score
						rubric_counts[category] += 1

			# 手直し時間を集計
			edit_time = feedback.get("edit_time_seconds")
			if edit_time is not None:
				edit_time_sum += edit_time
				edit_time_count += 1

			# 満足度を集計
			satisfaction = feedback.get("satisfaction_score")
			if satisfaction is not None:
				satisfaction_sum += satisfaction
				satisfaction_count += 1

		# 平均を計算
		avg_rubric_scores = {}
		for category in ["理解度", "論理性", "独自性", "実践性", "表現力"]:
			if rubric_counts[category] > 0:
				avg_rubric_scores[category] = round(rubric_sums[category] / rubric_counts[category], 2)
			else:
				avg_rubric_scores[category] = 0.0

		avg_edit_time = round(edit_time_sum / edit_time_count, 2) if edit_time_count > 0 else None
		avg_satisfaction = round(satisfaction_sum / satisfaction_count, 2) if satisfaction_count > 0 else None

		return StatsResponse(
			total_feedbacks=total_feedbacks,
			avg_rubric_scores=avg_rubric_scores,
			avg_edit_time_seconds=avg_edit_time,
			avg_satisfaction_score=avg_satisfaction,
		)

	except Exception as e:
		raise HTTPException(status_code=500, detail=f"Failed to fetch stats: {str(e)}")


# ===========================================
# 参照例管理エンドポイント
# ===========================================

@app.get("/references")
async def get_references(user: dict = Depends(verify_jwt)):
	"""全ての参照例を取得"""
	samples = load_samples()
	return {"references": samples, "count": len(samples)}


@app.get("/references/{reference_id}")
async def get_reference(reference_id: str, user: dict = Depends(verify_jwt)):
	"""特定の参照例を取得"""
	samples = load_samples()
	reference = next((s for s in samples if s.get("id") == reference_id), None)
	if not reference:
		return {"error": "参照例が見つかりません"}, 404
	return reference


@app.post("/references")
async def create_reference(req: ReferenceCreateRequest, user: dict = Depends(verify_jwt)):
	"""新しい参照例を作成"""
	if not supabase:
		raise HTTPException(status_code=500, detail="Supabaseが設定されていません")

	try:
		# 新しいIDを生成（prof_custom_XXXX形式）
		response = supabase.table("knowledge_base").select("reference_id").like("reference_id", "prof_custom_%").execute()
		custom_ids = [item["reference_id"] for item in response.data]

		if custom_ids:
			# 既存のカスタムIDから最大の番号を取得
			max_num = max([int(id.split("_")[-1]) for id in custom_ids if id.split("_")[-1].isdigit()], default=0)
			new_id = f"prof_custom_{max_num + 1:04d}"
		else:
			new_id = "prof_custom_0001"

		# Supabaseに新しい参照例を挿入
		data = {
			"reference_id": new_id,
			"type": req.type,
			"text": req.text,
			"tags": req.tags,
			"source": req.source or "professor_custom"
		}

		insert_response = supabase.table("knowledge_base").insert(data).execute()

		# レスポンス形式を統一
		new_reference = {
			"id": new_id,
			"type": req.type,
			"text": req.text,
			"tags": req.tags,
			"source": req.source or "professor_custom"
		}

		return {"success": True, "reference": new_reference}

	except Exception as e:
		raise HTTPException(status_code=500, detail=f"参照例の作成に失敗しました: {str(e)}")


@app.put("/references/{reference_id}")
async def update_reference(reference_id: str, req: ReferenceUpdateRequest, user: dict = Depends(verify_jwt)):
	"""参照例を更新"""
	if not supabase:
		raise HTTPException(status_code=500, detail="Supabaseが設定されていません")

	try:
		# 更新データを準備（指定されたフィールドのみ）
		update_data = {}
		if req.type is not None:
			update_data["type"] = req.type
		if req.text is not None:
			update_data["text"] = req.text
		if req.tags is not None:
			update_data["tags"] = req.tags
		if req.source is not None:
			update_data["source"] = req.source

		if not update_data:
			raise HTTPException(status_code=400, detail="更新するデータがありません")

		# Supabaseで更新
		response = supabase.table("knowledge_base").update(update_data).eq("reference_id", reference_id).execute()

		if not response.data:
			raise HTTPException(status_code=404, detail="参照例が見つかりません")

		# 更新後のデータを取得
		updated = response.data[0]
		reference = {
			"id": updated["reference_id"],
			"type": updated["type"],
			"text": updated["text"],
			"tags": updated.get("tags", []),
			"source": updated.get("source", "")
		}

		return {"success": True, "reference": reference}

	except HTTPException:
		raise
	except Exception as e:
		raise HTTPException(status_code=500, detail=f"参照例の更新に失敗しました: {str(e)}")


@app.delete("/references/{reference_id}")
async def delete_reference(reference_id: str, user: dict = Depends(verify_jwt)):
	"""参照例を削除"""
	if not supabase:
		raise HTTPException(status_code=500, detail="Supabaseが設定されていません")

	try:
		# Supabaseから削除
		response = supabase.table("knowledge_base").delete().eq("reference_id", reference_id).execute()

		if not response.data:
			raise HTTPException(status_code=404, detail="参照例が見つかりません")

		return {"success": True, "message": "参照例を削除しました"}

	except HTTPException:
		raise
	except Exception as e:
		raise HTTPException(status_code=500, detail=f"参照例の削除に失敗しました: {str(e)}")


@app.post("/references/from-feedback")
async def create_reference_from_feedback(
	feedback_id: str,
	edited_comment: str,
	report_type: str,
	user: dict = Depends(verify_jwt)
):
	"""修正したコメントを参照例として自動的にknowledge_baseに追加

	これにより、教授が修正すればするほど、AIが教授の思考を学習します
	"""
	if not supabase:
		raise HTTPException(status_code=500, detail="Supabaseが設定されていません")

	try:
		# 新しいIDを生成（learned_YYYYMMDD_XXXX形式）
		from datetime import datetime
		date_str = datetime.now().strftime("%Y%m%d")

		response = supabase.table("knowledge_base").select("reference_id").like("reference_id", f"learned_{date_str}_%").execute()
		learned_ids = [item["reference_id"] for item in response.data]

		if learned_ids:
			# 今日の最大番号を取得
			max_num = max([int(id.split("_")[-1]) for id in learned_ids if id.split("_")[-1].isdigit()], default=0)
			new_id = f"learned_{date_str}_{max_num + 1:04d}"
		else:
			new_id = f"learned_{date_str}_0001"

		# Supabaseに新しい参照例を挿入
		data = {
			"reference_id": new_id,
			"type": report_type,
			"text": edited_comment,
			"tags": ["自動学習", "教授修正"],
			"source": "professor_edited"
		}

		insert_response = supabase.table("knowledge_base").insert(data).execute()

		return {
			"success": True,
			"message": "修正したコメントを参照例として保存しました。次回から学習に使用されます。",
			"reference_id": new_id
		}

	except Exception as e:
		raise HTTPException(status_code=500, detail=f"参照例の作成に失敗しました: {str(e)}")


