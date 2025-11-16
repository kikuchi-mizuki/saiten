# Week 2-11 実装内容詳細サマリー

**実装期間**: 2025-11-14
**対象フェーズ**: Week 2-11（Phase 1 MVP）
**進捗率**: 85%完了

---

## 📋 目次

1. [実装概要](#実装概要)
2. [Week 2: 認証実装](#week-2-認証実装)
3. [Week 3-4: UI実装](#week-3-4-ui実装)
4. [Week 5-6: バックエンド強化](#week-5-6-バックエンド強化)
5. [Week 7-9: DB連携](#week-7-9-db連携)
6. [Week 10-11: 品質評価](#week-10-11-品質評価)
7. [変更ファイル一覧](#変更ファイル一覧)
8. [動作確認項目](#動作確認項目)

---

## 実装概要

Phase 1 MVPの主要機能（Week 2-11）を一括実装しました。

### 主要成果物

- **認証機能**: FastAPI JWT認証ミドルウェア、フロントエンド認証ヘッダー
- **PII検出**: 正規表現ベースの個人情報検出・マスキング
- **データ暗号化**: AES-256-GCMによるレポート本文暗号化
- **品質評価**: 手直し時間測定、満足度アンケート、統計表示
- **ドキュメント**: 認証セットアップガイド、進捗状況更新

---

## Week 2: 認証実装

### 実装内容

#### 1. FastAPI JWT認証ミドルウェア

**ファイル**: `api/main.py`

**追加コード**:

```python
import jwt
from supabase import create_client, Client
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

# Supabase設定
SUPABASE_URL = os.environ.get("SUPABASE_URL", "")
SUPABASE_ANON_KEY = os.environ.get("SUPABASE_ANON_KEY", "")
SUPABASE_JWT_SECRET = os.environ.get("SUPABASE_JWT_SECRET", "")

supabase: Client = create_client(SUPABASE_URL, SUPABASE_ANON_KEY)
security = HTTPBearer()

async def verify_jwt(credentials: HTTPAuthorizationCredentials = Depends(security)) -> dict:
    """
    Supabase JWTを検証し、ユーザー情報を返す
    開発環境ではDISABLE_AUTH=1で検証をスキップ可能
    """
    token = credentials.credentials

    # 開発モード
    if os.environ.get("DISABLE_AUTH", "0") == "1":
        logger.info("Auth disabled (development mode)")
        return {"user_id": "dev-user", "email": "dev@example.com"}

    try:
        payload = jwt.decode(
            token,
            SUPABASE_JWT_SECRET,
            algorithms=["HS256"],
            audience="authenticated",
            options={"verify_exp": True}
        )

        return {
            "user_id": payload.get("sub"),
            "email": payload.get("email"),
            "payload": payload
        }
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token has expired")
    except jwt.InvalidTokenError as e:
        raise HTTPException(status_code=401, detail=f"Invalid token: {str(e)}")
```

**適用箇所**:
- `/generate_direct` エンドポイント
- `/encrypt` エンドポイント
- `/decrypt` エンドポイント
- `/stats` エンドポイント
- `/references/*` エンドポイント

#### 2. フロントエンド認証ヘッダー実装

**ファイル**: `frontend/lib/auth.ts`

**追加関数**:

```typescript
export async function getAccessToken(): Promise<string | null> {
  const session = await getSession()
  return session?.access_token ?? null
}
```

**ファイル**: `frontend/lib/api.ts`

**追加関数**:

```typescript
async function getAuthHeaders(): Promise<HeadersInit> {
  const headers: HeadersInit = {
    'Content-Type': 'application/json',
  }

  const token = await getAccessToken()
  if (token) {
    headers['Authorization'] = `Bearer ${token}`
  }

  return headers
}
```

**更新関数**:
- `generateComment()`: 認証ヘッダー追加
- `encryptText()`: 認証ヘッダー追加
- `decryptText()`: 認証ヘッダー追加
- `getStats()`: 認証ヘッダー追加

#### 3. 環境変数設定

**ファイル**: `.env`

```bash
# Supabase
SUPABASE_URL=https://ovuseokcgawzqklushyj.supabase.co
SUPABASE_ANON_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
SUPABASE_JWT_SECRET=your-jwt-secret-here

# Authentication (開発時は1に設定してJWT検証を無効化、本番では0または削除)
DISABLE_AUTH=1
```

#### 4. ドキュメント作成

**ファイル**: `docs/authentication_setup.md`

**内容**:
- JWT検証の仕組み
- 環境変数設定方法
- 開発モードの使い方
- トラブルシューティング

---

## Week 3-4: UI実装

### 実装内容

#### 1. メイン画面実装

**ファイル**: `frontend/app/dashboard/page.tsx`

**レイアウト**:
- 2カラムレイアウト（7:5比率）
- 左カラム: レポート入力エリア
- 右カラム: 結果表示エリア（タブ切り替え）

**主要State**:

```typescript
const [reportText, setReportText] = useState('')
const [reportType, setReportType] = useState<'reflection' | 'final'>('reflection')
const [loading, setLoading] = useState(false)
const [result, setResult] = useState<GenerateResponse | null>(null)
const [activeTab, setActiveTab] = useState<'rubric' | 'summary' | 'comment'>('rubric')
const [editedComment, setEditedComment] = useState('')
```

#### 2. タブ表示実装

**タブ構成**:

1. **Rubricタブ**: 5項目の採点結果 + 理由
   - 理解度（1-5点）
   - 論理性（1-5点）
   - 独自性（1-5点）
   - 実践性（1-5点）
   - 表現力（1-5点）

2. **要約タブ**: 学生の主張を100文字程度で要約
   - executive summary
   - bullet points
   - structured summary

3. **コメントタブ**: 生成されたコメント（編集可能）
   - テキストエリアで編集可能
   - コピーボタン
   - 保存ボタン

#### 3. ローディングUX実装

段階的な進捗表示:

```typescript
const [loadingStage, setLoadingStage] = useState<string>('')

// 生成中の段階表示
setLoadingStage('PII検出中...')
setLoadingStage('Rubric採点中...')
setLoadingStage('要約生成中...')
setLoadingStage('過去コメント検索中...')
setLoadingStage('コメント生成中...')
```

---

## Week 5-6: バックエンド強化

### 実装内容

#### 1. PII検出・マスキング機能

**ファイル**: `api/main.py`

**クラス実装**:

```python
class PIIMatch(BaseModel):
    """個人情報検出結果"""
    type: str
    text: str
    start: int
    end: int
    priority: int

class PIIDetector:
    """個人情報検出・マスキングクラス"""

    def __init__(self):
        # 氏名パターン（姓・名の組み合わせ）
        self.name_pattern = re.compile(r'[一-龯ぁ-んァ-ヶ]{1,5}\s*[一-龯ぁ-んァ-ヶ]{1,5}')

        # 学籍番号パターン（数字・英数字）
        self.student_id_pattern = re.compile(r'\b[A-Z]?\d{5,10}\b')

        # メールアドレスパターン
        self.email_pattern = re.compile(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b')

        # 電話番号パターン
        self.phone_pattern = re.compile(r'\b0\d{1,4}[-\s]?\d{1,4}[-\s]?\d{4}\b')

    def detect(self, text: str) -> List[PIIMatch]:
        """個人情報を検出"""
        matches = []

        # 優先度順に検出（重複回避）
        # 1. メールアドレス（優先度: 4）
        for match in self.email_pattern.finditer(text):
            matches.append(PIIMatch(
                type="email",
                text=match.group(),
                start=match.start(),
                end=match.end(),
                priority=4
            ))

        # 2. 電話番号（優先度: 3）
        for match in self.phone_pattern.finditer(text):
            matches.append(PIIMatch(
                type="phone",
                text=match.group(),
                start=match.start(),
                end=match.end(),
                priority=3
            ))

        # 3. 学籍番号（優先度: 2）
        for match in self.student_id_pattern.finditer(text):
            if not self._overlaps(match.start(), match.end(), matches):
                matches.append(PIIMatch(
                    type="student_id",
                    text=match.group(),
                    start=match.start(),
                    end=match.end(),
                    priority=2
                ))

        # 4. 氏名（優先度: 1）
        for match in self.name_pattern.finditer(text):
            if not self._overlaps(match.start(), match.end(), matches):
                matches.append(PIIMatch(
                    type="name",
                    text=match.group(),
                    start=match.start(),
                    end=match.end(),
                    priority=1
                ))

        return sorted(matches, key=lambda x: x.start)

    def mask(self, text: str, matches: List[PIIMatch]) -> str:
        """個人情報をマスキング"""
        masked_text = text
        offset = 0

        for match in sorted(matches, key=lambda x: x.start):
            mask_label = {
                "name": "[氏名]",
                "student_id": "[学籍番号]",
                "email": "[メールアドレス]",
                "phone": "[電話番号]"
            }.get(match.type, "[PII]")

            start = match.start + offset
            end = match.end + offset

            masked_text = masked_text[:start] + mask_label + masked_text[end:]
            offset += len(mask_label) - (match.end - match.start)

        return masked_text
```

**統合箇所**:

```python
@app.post("/generate_direct", response_model=GenerateResponse)
async def generate_direct(request: GenerateRequest, user: dict = Depends(verify_jwt)) -> GenerateResponse:
    # PII検出
    pii_detector = PIIDetector()
    pii_matches = pii_detector.detect(report_text)
    masked_text = pii_detector.mask(report_text, pii_matches)

    # マスキング後のテキストをOpenAI APIに送信
    # ...
```

#### 2. final レポート対応

**ファイル**: `prompts/final.txt`（要作成）

`reflection.txt` をベースに、final レポート特有の指示を追加:
- 全体の成長を評価
- より深い示唆を提供
- 次のステップ（卒業後のキャリア等）への示唆

---

## Week 7-9: DB連携

### 実装内容

#### 1. データ暗号化機能

**ファイル**: `api/main.py`

**クラス実装**:

```python
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
import base64

class DataEncryption:
    """データ暗号化クラス（AES-256-GCM）"""

    def __init__(self):
        key_str = os.environ.get("ENCRYPTION_KEY", "dev-encryption-key-change-in-production-32bytes")
        self.key = key_str.encode('utf-8')[:32].ljust(32, b'\0')
        self.aesgcm = AESGCM(self.key)

    def encrypt(self, plaintext: str) -> str:
        """テキストを暗号化"""
        nonce = os.urandom(12)
        ciphertext = self.aesgcm.encrypt(nonce, plaintext.encode('utf-8'), None)
        encrypted = nonce + ciphertext
        return base64.b64encode(encrypted).decode('utf-8')

    def decrypt(self, encrypted_text: str) -> str:
        """暗号文を復号化"""
        encrypted = base64.b64decode(encrypted_text.encode('utf-8'))
        nonce = encrypted[:12]
        ciphertext = encrypted[12:]
        plaintext = self.aesgcm.decrypt(nonce, ciphertext, None)
        return plaintext.decode('utf-8')
```

**エンドポイント追加**:

```python
@app.post("/encrypt")
async def encrypt_text(request: EncryptRequest, user: dict = Depends(verify_jwt)) -> EncryptResponse:
    """テキストを暗号化"""
    encryptor = DataEncryption()
    encrypted_text = encryptor.encrypt(request.text)
    return EncryptResponse(encrypted_text=encrypted_text)

@app.post("/decrypt")
async def decrypt_text(request: DecryptRequest, user: dict = Depends(verify_jwt)) -> DecryptResponse:
    """暗号文を復号化"""
    encryptor = DataEncryption()
    text = encryptor.decrypt(request.encrypted_text)
    return DecryptResponse(text=text)
```

#### 2. フロントエンド暗号化統合

**ファイル**: `frontend/lib/api.ts`

**追加関数**:

```typescript
export async function encryptText(text: string): Promise<string> {
  const headers = await getAuthHeaders()

  const response = await fetch(`${API_BASE_URL}/encrypt`, {
    method: 'POST',
    headers,
    body: JSON.stringify({ text }),
  })

  if (!response.ok) {
    throw new Error(`Encryption failed: ${response.status} ${response.statusText}`)
  }

  const data = await response.json()
  return data.encrypted_text
}

export async function decryptText(encryptedText: string): Promise<string> {
  const headers = await getAuthHeaders()

  const response = await fetch(`${API_BASE_URL}/decrypt`, {
    method: 'POST',
    headers,
    body: JSON.stringify({ encrypted_text: encryptedText }),
  })

  if (!response.ok) {
    throw new Error(`Decryption failed: ${response.status} ${response.statusText}`)
  }

  const data = await response.json()
  return data.text
}
```

**ファイル**: `frontend/lib/database.ts`

**更新関数**:

```typescript
export async function saveReport(
  studentId: string,
  reportText: string
): Promise<Report | null> {
  const {
    data: { user },
  } = await supabase.auth.getUser()

  if (!user) {
    throw new Error('ユーザーが認証されていません')
  }

  // レポートテキストを暗号化
  let encryptedText: string | null = null
  try {
    encryptedText = await encryptText(reportText)
  } catch (error) {
    console.error('Encryption error:', error)
    // 暗号化に失敗してもレポートは保存する（Phase 1では暗号化は任意）
  }

  const { data, error } = await supabase
    .from('reports')
    .insert({
      user_id: user.id,
      student_id: studentId || null,
      report_text: reportText,
      encrypted_text: encryptedText,
    })
    .select()
    .single()

  if (error) {
    console.error('Report save error:', error)
    throw error
  }

  return data
}
```

---

## Week 10-11: 品質評価

### 実装内容

#### 1. 手直し時間測定機能

**ファイル**: `frontend/app/dashboard/page.tsx`

**追加State**:

```typescript
const [generateTime, setGenerateTime] = useState<number | null>(null)
const [feedbackId, setFeedbackId] = useState<string | null>(null)
```

**実装**:

```typescript
async function handleGenerate() {
  // ...コメント生成処理...

  // 生成完了時刻を記録
  setGenerateTime(Date.now())
  setFeedbackId(response.feedback_id)
}

async function handleSaveComment() {
  if (!feedbackId || !generateTime) {
    alert('コメントを保存できません')
    return
  }

  // 経過時間を計算（秒単位）
  const editTimeSeconds = Math.floor((Date.now() - generateTime) / 1000)

  // アンケートモーダルを表示
  setShowSurvey(true)

  // 編集時間を先に保存（満足度は0で初期化）
  try {
    await saveQualityRating(feedbackId, editTimeSeconds, 0, '')
  } catch (error) {
    console.error('Save edit time error:', error)
  }
}
```

#### 2. 満足度アンケート機能

**追加State**:

```typescript
const [showSurvey, setShowSurvey] = useState(false)
const [satisfactionScore, setSatisfactionScore] = useState<number>(0)
const [feedbackText, setFeedbackText] = useState<string>('')
```

**実装**:

```typescript
async function handleSubmitSurvey() {
  if (!feedbackId) {
    alert('アンケートを送信できません')
    return
  }

  if (satisfactionScore === 0) {
    alert('満足度を選択してください')
    return
  }

  try {
    // 満足度とフィードバックを更新
    await saveQualityRating(
      feedbackId,
      0, // 編集時間は既に保存済み
      satisfactionScore,
      feedbackText
    )

    alert('アンケートを送信しました')
    setShowSurvey(false)
    setSatisfactionScore(0)
    setFeedbackText('')
  } catch (error) {
    console.error('Submit survey error:', error)
    alert('アンケートの送信に失敗しました')
  }
}
```

**UI実装**:

```tsx
{showSurvey && (
  <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
    <div className="bg-white rounded-lg p-8 max-w-md w-full">
      <h2 className="text-xl font-bold mb-4">満足度アンケート</h2>

      <p className="mb-4">生成されたコメントの満足度を教えてください（1-5点）</p>

      <div className="flex gap-2 mb-6">
        {[1, 2, 3, 4, 5].map((score) => (
          <button
            key={score}
            onClick={() => setSatisfactionScore(score)}
            className={`flex-1 py-3 rounded ${
              satisfactionScore === score
                ? 'bg-[var(--accent)] text-white'
                : 'bg-gray-200 text-gray-700 hover:bg-gray-300'
            }`}
          >
            {score}
          </button>
        ))}
      </div>

      <p className="mb-2">フィードバック（任意）</p>
      <textarea
        value={feedbackText}
        onChange={(e) => setFeedbackText(e.target.value)}
        className="w-full p-3 border rounded mb-4"
        rows={3}
        placeholder="改善点などがあればお聞かせください"
      />

      <div className="flex gap-2">
        <button
          onClick={handleSubmitSurvey}
          className="flex-1 bg-[var(--accent)] text-white py-2 rounded hover:opacity-90"
        >
          送信
        </button>
        <button
          onClick={() => {
            setShowSurvey(false)
            setSatisfactionScore(0)
            setFeedbackText('')
          }}
          className="flex-1 bg-gray-200 text-gray-700 py-2 rounded hover:bg-gray-300"
        >
          キャンセル
        </button>
      </div>
    </div>
  </div>
)}
```

#### 3. 統計表示機能

**ファイル**: `api/main.py`

**エンドポイント追加**:

```python
class StatsResponse(BaseModel):
    """統計情報レスポンス"""
    total_feedbacks: int
    avg_rubric_scores: Dict[str, float]
    avg_edit_time_seconds: Optional[float]
    avg_satisfaction_score: Optional[float]

@app.get("/stats", response_model=StatsResponse)
async def get_stats(user: dict = Depends(verify_jwt)) -> StatsResponse:
    """統計情報を取得"""
    user_id = user.get("user_id")

    # feedbacksテーブルから統計情報を取得
    response = supabase.table("feedbacks")\
        .select("rubric, edit_time_seconds, satisfaction_score")\
        .eq("user_id", user_id)\
        .execute()

    feedbacks = response.data
    total = len(feedbacks)

    if total == 0:
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

    # 平均Rubric点数を計算
    rubric_sums = {
        "理解度": 0.0,
        "論理性": 0.0,
        "独自性": 0.0,
        "実践性": 0.0,
        "表現力": 0.0,
    }

    for fb in feedbacks:
        rubric = fb.get("rubric", {})
        for key in rubric_sums.keys():
            rubric_sums[key] += rubric.get(key, {}).get("score", 0)

    avg_rubric_scores = {key: value / total for key, value in rubric_sums.items()}

    # 平均編集時間を計算
    edit_times = [fb.get("edit_time_seconds") for fb in feedbacks if fb.get("edit_time_seconds") is not None]
    avg_edit_time = sum(edit_times) / len(edit_times) if edit_times else None

    # 平均満足度を計算
    satisfaction_scores = [fb.get("satisfaction_score") for fb in feedbacks if fb.get("satisfaction_score") is not None and fb.get("satisfaction_score") > 0]
    avg_satisfaction = sum(satisfaction_scores) / len(satisfaction_scores) if satisfaction_scores else None

    return StatsResponse(
        total_feedbacks=total,
        avg_rubric_scores=avg_rubric_scores,
        avg_edit_time_seconds=avg_edit_time,
        avg_satisfaction_score=avg_satisfaction,
    )
```

**ファイル**: `frontend/lib/api.ts`

**追加関数**:

```typescript
export interface StatsResponse {
  total_feedbacks: number
  avg_rubric_scores: {
    理解度: number
    論理性: number
    独自性: number
    実践性: number
    表現力: number
  }
  avg_edit_time_seconds: number | null
  avg_satisfaction_score: number | null
}

export async function getStats(): Promise<StatsResponse> {
  const headers = await getAuthHeaders()

  const response = await fetch(`${API_BASE_URL}/stats`, {
    method: 'GET',
    headers,
  })

  if (!response.ok) {
    throw new Error(`Stats fetch failed: ${response.status} ${response.statusText}`)
  }

  return response.json()
}
```

**ファイル**: `frontend/app/dashboard/page.tsx`

**UI実装**:

```tsx
const [stats, setStats] = useState<StatsResponse | null>(null)
const [showStats, setShowStats] = useState(false)

async function loadStats() {
  try {
    const data = await getStats()
    setStats(data)
  } catch (error) {
    console.error('Load stats error:', error)
  }
}

useEffect(() => {
  loadStats()
}, [])

// 統計カードUI
{stats && (
  <div className="max-w-[1400px] mx-auto px-6 py-4">
    <div className="p-4 rounded-[var(--radius)]" style={{
      backgroundColor: 'var(--surface)',
      border: '1px solid var(--border)',
    }}>
      <div className="flex items-center justify-between mb-3">
        <h2 className="text-lg font-bold">統計情報</h2>
        <button
          onClick={() => setShowStats(!showStats)}
          className="text-sm px-3 py-1 rounded"
          style={{
            backgroundColor: 'var(--accent)',
            color: 'white',
          }}
        >
          {showStats ? '非表示' : '表示'}
        </button>
      </div>

      {showStats && (
        <div className="grid grid-cols-4 gap-4">
          {/* 総コメント生成数 */}
          <div className="p-3 rounded bg-gray-50">
            <p className="text-sm text-gray-600">総コメント生成数</p>
            <p className="text-2xl font-bold">{stats.total_feedbacks}</p>
          </div>

          {/* 平均Rubric点数 */}
          <div className="p-3 rounded bg-gray-50">
            <p className="text-sm text-gray-600">平均Rubric点数</p>
            <p className="text-2xl font-bold">
              {Object.values(stats.avg_rubric_scores).reduce((a, b) => a + b, 0).toFixed(1)}/25
            </p>
          </div>

          {/* 平均編集時間 */}
          <div className="p-3 rounded bg-gray-50">
            <p className="text-sm text-gray-600">平均編集時間</p>
            <p className="text-2xl font-bold">
              {stats.avg_edit_time_seconds
                ? `${Math.floor(stats.avg_edit_time_seconds / 60)}分${stats.avg_edit_time_seconds % 60}秒`
                : '-'}
            </p>
          </div>

          {/* 平均満足度 */}
          <div className="p-3 rounded bg-gray-50">
            <p className="text-sm text-gray-600">平均満足度</p>
            <p className="text-2xl font-bold">
              {stats.avg_satisfaction_score
                ? `${stats.avg_satisfaction_score.toFixed(1)}/5.0`
                : '-'}
            </p>
          </div>
        </div>
      )}
    </div>
  </div>
)}
```

---

## 変更ファイル一覧

### バックエンド

| ファイル | 変更内容 |
|---------|---------|
| `api/main.py` | JWT認証、PII検出、データ暗号化、統計エンドポイント追加 |
| `requirements.txt` | `supabase`, `pyjwt`, `cryptography` 追加 |
| `.env` | Supabase認証情報、暗号化キー追加 |

### フロントエンド

| ファイル | 変更内容 |
|---------|---------|
| `frontend/lib/auth.ts` | `getAccessToken()` 関数追加 |
| `frontend/lib/api.ts` | 認証ヘッダー、暗号化関数、統計関数追加 |
| `frontend/lib/references.ts` | 認証ヘッダー追加 |
| `frontend/lib/database.ts` | レポート暗号化統合 |
| `frontend/app/dashboard/page.tsx` | 手直し時間測定、満足度アンケート、統計表示追加 |

### ドキュメント

| ファイル | 変更内容 |
|---------|---------|
| `docs/progress.md` | Week 2-11の実装内容、進捗率更新 |
| `docs/authentication_setup.md` | 新規作成（認証セットアップガイド） |
| `docs/implementation_summary_week2-11.md` | 新規作成（本ドキュメント） |

---

## 動作確認項目

### 認証機能

- [ ] 開発モード（`DISABLE_AUTH=1`）でAPI呼び出しが成功する
- [ ] 本番モード（`DISABLE_AUTH=0`）でJWT検証が動作する
- [ ] 無効なトークンで401エラーが返る
- [ ] 期限切れトークンで401エラーが返る

### PII検出

- [ ] 氏名が検出され、`[氏名]` にマスキングされる
- [ ] 学籍番号が検出され、`[学籍番号]` にマスキングされる
- [ ] メールアドレスが検出され、`[メールアドレス]` にマスキングされる
- [ ] 電話番号が検出され、`[電話番号]` にマスキングされる
- [ ] 誤検出が少ない（目視確認）

### データ暗号化

- [ ] `/encrypt` エンドポイントでテキストが暗号化される
- [ ] `/decrypt` エンドポイントで暗号文が復号化される
- [ ] レポート保存時に自動暗号化される
- [ ] 暗号化失敗時もレポートが保存される（グレースフル）

### 品質評価

- [ ] コメント生成完了時に `generateTime` が記録される
- [ ] 保存ボタン押下時に編集時間が計算される
- [ ] アンケートモーダルが表示される
- [ ] 満足度（1-5点）が選択できる
- [ ] フィードバックテキストが入力できる
- [ ] アンケート送信が成功する

### 統計表示

- [ ] `/stats` エンドポイントで統計情報が取得できる
- [ ] 総コメント生成数が正しく表示される
- [ ] 平均Rubric点数が正しく計算される
- [ ] 平均編集時間が分/秒形式で表示される
- [ ] 平均満足度が正しく計算される
- [ ] 統計カードの表示/非表示が切り替わる

---

## 次のステップ

### Week 12: UAT実施

1. **UAT計画書作成**
   - テストシナリオ定義
   - KPI測定方法確定
   - ベースライン測定計画

2. **教授による実運用テスト**
   - 20件のレポートでコメント生成
   - Rubric採点精度の確認
   - 手直し時間の測定
   - 満足度アンケート回答

3. **フィードバック収集**
   - 改善点の洗い出し
   - バグ修正
   - 微調整

### Week 13-14: 最終調整・デプロイ

1. **ドキュメント作成**
   - ユーザーマニュアル
   - 管理者マニュアル
   - 緊急対応手順書

2. **本番環境デプロイ**
   - Vercelにフロントエンドデプロイ
   - バックエンドデプロイ（Railway/Render）
   - 環境変数設定（`DISABLE_AUTH=0`, JWT Secret, Encryption Key）

3. **Phase 2-Aキックオフ**
   - データ移行計画確認
   - Phase 2-A要件確認
   - スケジュール調整

---

**以上**
