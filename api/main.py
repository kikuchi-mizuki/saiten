from fastapi import FastAPI
from pydantic import BaseModel
from typing import Dict, List, Optional, Tuple
import json
import pathlib
import re
import os
import requests

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

app = FastAPI(title="教授コメント自動化Bot API (MVP)")


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


def load_samples() -> List[Dict]:
	try:
		return json.loads(SAMPLE_PATH.read_text(encoding="utf-8"))
	except Exception:
		return []


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
		summary_prompt = f"""以下の学生レポートを読んで、要点がわかるように要約してください。

【レポート】
{text}

【出力形式】
以下の形式で要約を作成してください:

[レポートの全体要約：1-2段落で、レポートの目的、主要なテーマ、論点を簡潔にまとめる。約200-300文字程度。]

[番号付きセクション（1️⃣, 2️⃣, 3️⃣...）で要点を整理：レポートの主要な論点や考察を3-5つのセクションに分けて説明する。
各セクションは以下の形式：
1️⃣ [セクション見出し]

[セクションの内容：2-3文で説明。必要に応じて箇条書きも使用可。]

最後に「結論」セクションを追加：
[結論]
[レポートの結論や総括：1-2段落でまとめる。]

【注意事項】
- 文体は「です・ます」調で統一してください
- 重要なキーワードや概念は**太字**で強調してください
- 各セクションは読みやすく、要点が明確になるように構成してください
- 原文の重要な論点や考察を漏らさず、簡潔にまとめてください
- 文字数は原文の約1/5から1/8程度に圧縮してください
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
	
	# 参照例の文字数を分析して、平均文字数を計算
	ref_lengths = []
	refs_text_list = []
	ref_details = []  # 各参照例の詳細情報（文字数を含む）
	
	for i, ref in enumerate(refs, 1):
		if ref:
			# JSONのエスケープされた改行文字（\\n）を実際の改行に変換
			ref_normalized = ref.replace("\\n", "\n")
			# 改行と空白を除いた実際の文字数をカウント（日本語文字数を正確に測定）
			ref_clean = ref_normalized.replace("\n", "").replace(" ", "").replace("\t", "").replace("\\n", "")
			ref_length = len(ref_clean)
			ref_lengths.append(ref_length)
			refs_text_list.append(f"- {ref_normalized}")
			ref_details.append(f"参照例{i}: {ref_length}文字")
	
	# 参照例の平均文字数を計算（参照例がある場合）
	target_length = None
	length_instruction = ""
	avg_length = None
	if ref_lengths:
		avg_length = sum(ref_lengths) / len(ref_lengths)
		# 平均文字数の±10%の範囲を目標文字数とする（より厳密に）
		min_length = max(200, int(avg_length * 0.9))  # 最小200文字
		max_length = int(avg_length * 1.1)
		target_length = f"{min_length}〜{max_length}文字"
		
		# 各参照例の文字数を明示
		ref_lengths_text = "、".join(ref_details)
		length_instruction = f"""
【重要：文字数指定（厳守）】
参照例の文字数: {ref_lengths_text}
参照例の平均文字数: 約{int(avg_length)}文字
目標文字数: {target_length}（平均の±10%以内）

⚠️ 絶対に守ってください：
- 必ず参照例と同じくらいの分量で生成してください
- 参照例の文字数を参考に、{int(avg_length)}文字前後（{target_length}の範囲内）で生成することが最重要です
- 参照例と同じ文体・同じ分量感・同じ詳細度で生成してください
- 短すぎても長すぎてもいけません。参照例の平均文字数（{int(avg_length)}文字）にできるだけ近い分量で生成してください
"""
	
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
	
	# プロンプトの文字数指定部分を動的に置換
	if target_length:
		# プロンプト内の「文字数: 300〜400文字」などのパターンを置換
		# より柔軟なパターンマッチング（全角・半角コロン、波線・ハイフンに対応）
		base = re.sub(r"文字数[：:]\s*参照例.*?文字", f"文字数: {target_length}", base, flags=re.DOTALL)
		base = re.sub(r"文字数[：:]\s*\d+[〜~-]\d+文字[（(].*?[）)]?", f"文字数: {target_length}（参照例の分量に合わせる）", base)
		base = re.sub(r"文字数[：:]\s*\d+[〜~-]\d+文字", f"文字数: {target_length}（参照例の分量に合わせる）", base)
		base = re.sub(r"- 文字数[：:]\s*\d+[〜~-]\d+文字", f"- 文字数: {target_length}（参照例の分量に合わせる）", base)
	
	return (
		f"{base}\n\n【参照例（文体のヒント・分量の目安）】\n{refs_text}{length_instruction}\n"
		f"【Rubric所感（目安）】\n{scores_text}\n\n"
		f"【入力レポート】\n{text}\n"
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
		system_message = "あなたは経営戦略論の教授です。敬意と温かさを保ち、1つのまとまった文章ブロックとして出力してください。"
	
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
				"temperature": 0.6,
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
async def generate(req: GenerateRequest) -> GenerateResponse:
	return build_comment(req)


# 直接生成エンドポイント
@app.post("/generate_direct")
async def generate_direct(req: DirectGenRequest):
	doc_type = (req.type or "reflection")
	refs = retrieve_refs(req.text, doc_type, k=2)
	scores = simple_score(req.text)
	llm_used = False
	llm_error = None
	draft = None
	
	# 参照例の平均文字数を計算して、max_tokensを動的に設定
	avg_length = None
	max_tokens = 500  # デフォルト値
	system_message = "あなたは経営戦略論の教授です。敬意と温かさを保ち、1つのまとまった文章ブロックとして出力してください。"
	
	if refs:
		ref_lengths = []
		for ref in refs:
			if ref:
				ref_normalized = ref.replace("\\n", "\n")
				ref_clean = ref_normalized.replace("\n", "").replace(" ", "").replace("\t", "").replace("\\n", "")
				ref_length = len(ref_clean)
				ref_lengths.append(ref_length)
		
		if ref_lengths:
			avg_length = sum(ref_lengths) / len(ref_lengths)
			# 日本語の場合、1文字≈2トークン程度。安全のため平均文字数の2.5倍を設定
			# 最小500、最大2000に制限
			calculated_tokens = int(avg_length * 2.5)
			max_tokens = max(500, min(calculated_tokens, 2000))
			
			# system_messageに文字数に関する指示を追加
			system_message = f"""あなたは経営戦略論の教授です。敬意と温かさを保ち、1つのまとまった文章ブロックとして出力してください。

重要：参照例の平均文字数は約{int(avg_length)}文字です。必ずこの分量に合わせて、同じくらいの文量で生成してください。"""
	
	if USE_LLM and os.environ.get("OPENAI_API_KEY"):
		prompt = build_llm_prompt(req.text, doc_type, refs, scores)
		draft, llm_error = call_openai(prompt, max_tokens=max_tokens, system_message=system_message)
		llm_used = draft is not None and llm_error is None
	if not draft:
		if doc_type == "reflection":
			draft = generate_reflection_draft(req.text, refs, scores)
		else:
			draft = "\n".join([
				"全体評価: 学びの接続と仮説の筋が見られます。",
				"強み: 現場観察の具体性。",
				"改善: 指標・撤退基準の明確化。",
				"総括: あり方に立脚し、次の一歩を具体化しましょう。",
			])
	
	# 要約生成（常にLLM使用）
	summary, summary_llm_used, summary_error = generate_summary(req.text)
	
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
	}


@app.get("/health")
async def health():
	return {"ok": True}
