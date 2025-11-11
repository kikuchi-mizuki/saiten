# 教授コメント自動化ボット 技術仕様書

**最終更新**: 2025-11-11
**バージョン**: 1.0
**対象フェーズ**: Phase 1 MVP

---

## 目次

1. [システムアーキテクチャ](#システムアーキテクチャ)
2. [データベース設計](#データベース設計)
3. [API仕様](#api仕様)
4. [認証フロー](#認証フロー)
5. [PII検出ロジック](#pii検出ロジック)
6. [コンポーネント構成](#コンポーネント構成)
7. [デプロイメント](#デプロイメント)
8. [セキュリティ](#セキュリティ)

---

## システムアーキテクチャ

### 全体構成図

```
┌─────────────────────────────────────────────────────────────┐
│                         ユーザー                              │
│                        (教授)                                │
└────────────────────────┬────────────────────────────────────┘
                         │ HTTPS
                         ▼
┌─────────────────────────────────────────────────────────────┐
│                    Vercel (Frontend)                         │
│  ┌──────────────────────────────────────────────────────┐   │
│  │          Next.js 14 (App Router)                     │   │
│  │  ┌──────────────┐  ┌──────────────┐                 │   │
│  │  │ Login Page   │  │  Main Page   │                 │   │
│  │  │ (OAuth)      │  │  (Comment    │                 │   │
│  │  │              │  │   Generator) │                 │   │
│  │  └──────────────┘  └──────────────┘                 │   │
│  │  ┌──────────────┐  ┌──────────────┐                 │   │
│  │  │ History Page │  │  Stats Page  │                 │   │
│  │  └──────────────┘  └──────────────┘                 │   │
│  └──────────────────────────────────────────────────────┘   │
└─────────────────────────┬───────────────────────────────────┘
                          │ REST API (HTTPS)
                          ▼
┌─────────────────────────────────────────────────────────────┐
│                   FastAPI Backend                            │
│  ┌──────────────────────────────────────────────────────┐   │
│  │           認証ミドルウェア (JWT検証)                  │   │
│  └──────────────────────┬───────────────────────────────┘   │
│                         ▼                                    │
│  ┌──────────────────────────────────────────────────────┐   │
│  │                  API Endpoints                       │   │
│  │  • POST /generate    • GET /history                  │   │
│  │  • DELETE /history   • GET /export                   │   │
│  │  • GET /stats        • GET /health                   │   │
│  └──────────────┬───────────────────┬───────────────────┘   │
│                 │                   │                        │
│                 ▼                   ▼                        │
│  ┌──────────────────┐  ┌───────────────────────────┐       │
│  │  PIIDetector     │  │  CommentGenerator         │       │
│  │  (正規表現)       │  │  (LLM + RAG)              │       │
│  └──────────────────┘  └───────────────────────────┘       │
└─────────────────────────┬──────────────┬────────────────────┘
                          │              │
           ┌──────────────┘              └──────────────┐
           ▼                                            ▼
┌──────────────────────┐                    ┌──────────────────────┐
│   Supabase           │                    │   OpenAI API         │
│                      │                    │                      │
│  ┌────────────────┐  │                    │  ┌────────────────┐  │
│  │ PostgreSQL     │  │                    │  │ gpt-4o-mini    │  │
│  │ (RLS有効)      │  │                    │  └────────────────┘  │
│  │                │  │                    │                      │
│  │ • histories    │  │                    └──────────────────────┘
│  │ • knowledge_   │  │
│  │   base         │  │
│  └────────────────┘  │
│                      │
│  ┌────────────────┐  │
│  │ Supabase Auth  │  │
│  │ (Google OAuth) │  │
│  └────────────────┘  │
└──────────────────────┘
```

### 技術スタック一覧

| レイヤー | 技術 | バージョン | 用途 |
|---------|------|-----------|------|
| **Frontend** | Next.js | 14.x | Reactフレームワーク (App Router) |
| | TypeScript | 5.x | 型安全性 |
| | TailwindCSS | 3.x | スタイリング |
| | React | 18.x | UIライブラリ |
| **Backend** | FastAPI | 0.109+ | Python WebフレームワークAPI |
| | Python | 3.11+ | プログラミング言語 |
| | Pydantic | 2.x | データバリデーション |
| | cryptography | 42.x | データ暗号化 |
| **Database** | Supabase | - | PostgreSQL + Auth + RLS |
| | PostgreSQL | 15.x | リレーショナルDB |
| **LLM** | OpenAI API | - | gpt-4o-mini |
| **認証** | Supabase Auth | - | Google OAuth |
| **デプロイ** | Vercel | - | Frontend hosting |
| | (未定) | - | Backend hosting (Phase 1は開発環境のみ) |

---

## データベース設計

### ER図

```
┌─────────────────────────┐
│      auth.users         │  (Supabase Auth標準テーブル)
│─────────────────────────│
│ id (UUID) PK            │
│ email                   │
│ created_at              │
│ ...                     │
└───────────┬─────────────┘
            │ 1
            │
            │ N
            ▼
┌─────────────────────────┐
│      histories          │
│─────────────────────────│
│ id (UUID) PK            │
│ user_id (UUID) FK       │◄──────── RLS: auth.uid() = user_id
│ report_type (TEXT)      │
│ report_text_encrypted   │
│ masked_text (TEXT)      │
│ rubric_scores (JSONB)   │
│ rubric_reasons (JSONB)  │
│ summary (TEXT)          │
│ comment (TEXT)          │
│ edit_time_seconds (INT) │
│ satisfaction (INT)      │
│ created_at (TIMESTAMP)  │
│ updated_at (TIMESTAMP)  │
└─────────────────────────┘

┌─────────────────────────┐
│    knowledge_base       │
│─────────────────────────│
│ id (UUID) PK            │
│ comment_text (TEXT)     │
│ report_type (TEXT)      │
│ created_at (TIMESTAMP)  │
└─────────────────────────┘
```

### テーブル定義

#### 1. histories テーブル

**用途**: コメント生成履歴を保存

```sql
CREATE TABLE histories (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
    report_type TEXT NOT NULL CHECK (report_type IN ('reflection', 'final')),
    report_text_encrypted TEXT NOT NULL,
    masked_text TEXT NOT NULL,
    rubric_scores JSONB NOT NULL,
    rubric_reasons JSONB NOT NULL,
    summary TEXT NOT NULL,
    comment TEXT NOT NULL,
    edit_time_seconds INTEGER,
    satisfaction INTEGER CHECK (satisfaction BETWEEN 1 AND 5),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- インデックス
CREATE INDEX idx_histories_user_created ON histories(user_id, created_at DESC);

-- RLS (Row Level Security)
ALTER TABLE histories ENABLE ROW LEVEL SECURITY;

-- ポリシー: ユーザーは自分のデータのみ参照可能
CREATE POLICY "Users can view their own histories"
    ON histories FOR SELECT
    USING (auth.uid() = user_id);

-- ポリシー: ユーザーは自分のデータのみ挿入可能
CREATE POLICY "Users can insert their own histories"
    ON histories FOR INSERT
    WITH CHECK (auth.uid() = user_id);

-- ポリシー: ユーザーは自分のデータのみ更新可能
CREATE POLICY "Users can update their own histories"
    ON histories FOR UPDATE
    USING (auth.uid() = user_id);

-- ポリシー: ユーザーは自分のデータのみ削除可能
CREATE POLICY "Users can delete their own histories"
    ON histories FOR DELETE
    USING (auth.uid() = user_id);

-- 自動更新トリガー
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

CREATE TRIGGER update_histories_updated_at BEFORE UPDATE
    ON histories FOR EACH ROW
    EXECUTE PROCEDURE update_updated_at_column();
```

**JSONB構造**:

```json
// rubric_scores
{
    "理解度": 4,
    "論理性": 3,
    "独自性": 4,
    "実践性": 5,
    "表現力": 4
}

// rubric_reasons
{
    "理解度": "課題の本質を的確に捉えており、理論的背景も踏まえています。",
    "論理性": "主張は明確ですが、根拠の提示がやや不足しています。",
    "独自性": "自身の経験を交えた独自の視点が見られます。",
    "実践性": "具体的な実践計画が示されており、実現可能性が高いです。",
    "表現力": "文章は明瞭で読みやすいですが、専門用語の使用がやや不足しています。"
}
```

#### 2. knowledge_base テーブル

**用途**: 過去の教授コメント例を保存（RAG検索用）

```sql
CREATE TABLE knowledge_base (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    comment_text TEXT NOT NULL,
    report_type TEXT NOT NULL CHECK (report_type IN ('reflection', 'final')),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- インデックス
CREATE INDEX idx_knowledge_base_report_type ON knowledge_base(report_type);

-- RLS (Phase 1は全ユーザー読み取り可能)
ALTER TABLE knowledge_base ENABLE ROW LEVEL SECURITY;

-- ポリシー: 全ユーザーが参照可能
CREATE POLICY "Anyone can view knowledge base"
    ON knowledge_base FOR SELECT
    USING (true);

-- ポリシー: 挿入・更新・削除はPhase 2-Aで実装
```

**初期データ投入**:

```sql
-- data/sample_comments.json から50件を投入
INSERT INTO knowledge_base (comment_text, report_type) VALUES
('【学生の振り返りの概要】を読みました。...', 'reflection'),
('【具体的な課題認識】が見えます。...', 'reflection'),
-- ... 50件
```

#### 3. auth.users テーブル

Supabase Authが自動管理するテーブル。Phase 1では追加カラム不要。

---

## API仕様

### ベースURL

- **開発環境**: `http://127.0.0.1:8010`
- **本番環境**: `https://api.yourdomain.com` (Phase 1では未定義)

### 認証

すべてのエンドポイント（`/health` を除く）で JWT 認証が必要。

**ヘッダー**:
```
Authorization: Bearer <JWT_TOKEN>
```

### エンドポイント一覧

| メソッド | エンドポイント | 説明 | 認証 |
|---------|--------------|------|------|
| POST | `/generate` | コメント生成 | 必須 |
| GET | `/history` | 履歴一覧取得 | 必須 |
| GET | `/history/{id}` | 履歴詳細取得 | 必須 |
| DELETE | `/history/{id}` | 履歴削除 | 必須 |
| PUT | `/history/{id}` | 履歴更新（手直し時間・満足度） | 必須 |
| GET | `/export` | 履歴エクスポート | 必須 |
| GET | `/stats` | 統計情報取得 | 必須 |
| GET | `/health` | ヘルスチェック | 不要 |

---

### POST /generate

**説明**: レポートからコメントを生成

**リクエスト**:
```json
{
    "report_text": "今週の経営戦略論の講義では...",
    "report_type": "reflection"  // "reflection" or "final"
}
```

**レスポンス**:
```json
{
    "history_id": "550e8400-e29b-41d4-a716-446655440000",
    "masked_text": "今週の経営戦略論の講義では[氏名]氏の理論を学びました...",
    "pii_detected": [
        {"type": "name", "value": "[氏名]", "position": [15, 18]}
    ],
    "rubric": {
        "理解度": 4,
        "論理性": 3,
        "独自性": 4,
        "実践性": 5,
        "表現力": 4,
        "total": 20
    },
    "rubric_reasons": {
        "理解度": "課題の本質を的確に捉えており...",
        "論理性": "主張は明確ですが...",
        "独自性": "自身の経験を交えた...",
        "実践性": "具体的な実践計画が...",
        "表現力": "文章は明瞭で読みやすいですが..."
    },
    "summary": "【学生の振り返りの概要】戦略論の基礎を理解し、自社の事例に適用を試みている。理論と実践の往復を意識している。",
    "comment": "【学生の振り返りの概要】を読みました。戦略論の基礎概念を丁寧に理解しようとする姿勢が見えます。次回は、理論を自社の具体的な状況にどう適用できるか、仮説を立てて検証してみることをおすすめします。",
    "rag_results": [
        {
            "comment_text": "【学生の振り返りの概要】を読みました...",
            "similarity": 0.85
        }
    ]
}
```

**エラーレスポンス**:
```json
{
    "detail": "OpenAI API error: Rate limit exceeded",
    "fallback_used": true,
    "comment": "【ヒューリスティック生成】レポートを拝読しました。次回はより具体的な考察を期待します。"
}
```

---

### GET /history

**説明**: 履歴一覧を取得（ページネーション対応）

**クエリパラメータ**:
- `page`: ページ番号（デフォルト: 1）
- `limit`: 1ページあたりの件数（デフォルト: 10、最大: 100）

**リクエスト例**:
```
GET /history?page=1&limit=10
```

**レスポンス**:
```json
{
    "total": 45,
    "page": 1,
    "limit": 10,
    "histories": [
        {
            "id": "550e8400-e29b-41d4-a716-446655440000",
            "report_type": "reflection",
            "masked_text_preview": "今週の経営戦略論の講義では...",
            "rubric_total": 20,
            "created_at": "2025-11-11T10:30:00Z"
        }
    ]
}
```

---

### GET /history/{id}

**説明**: 履歴詳細を取得

**レスポンス**:
```json
{
    "id": "550e8400-e29b-41d4-a716-446655440000",
    "report_type": "reflection",
    "masked_text": "今週の経営戦略論の講義では[氏名]氏の理論を学びました...",
    "rubric_scores": {
        "理解度": 4,
        "論理性": 3,
        "独自性": 4,
        "実践性": 5,
        "表現力": 4
    },
    "rubric_reasons": { /* ... */ },
    "summary": "【学生の振り返りの概要】...",
    "comment": "【学生の振り返りの概要】を読みました...",
    "edit_time_seconds": 120,
    "satisfaction": 5,
    "created_at": "2025-11-11T10:30:00Z",
    "updated_at": "2025-11-11T10:35:00Z"
}
```

---

### DELETE /history/{id}

**説明**: 履歴を削除

**レスポンス**:
```json
{
    "message": "History deleted successfully",
    "id": "550e8400-e29b-41d4-a716-446655440000"
}
```

---

### PUT /history/{id}

**説明**: 履歴を更新（手直し時間・満足度のみ）

**リクエスト**:
```json
{
    "edit_time_seconds": 120,
    "satisfaction": 5
}
```

**レスポンス**:
```json
{
    "message": "History updated successfully",
    "id": "550e8400-e29b-41d4-a716-446655440000"
}
```

---

### GET /export

**説明**: 履歴をエクスポート

**クエリパラメータ**:
- `format`: "json" または "csv"（デフォルト: "json"）

**リクエスト例**:
```
GET /export?format=csv
```

**レスポンス**:
- **JSON形式**: 履歴の配列
- **CSV形式**: CSV文字列（Content-Type: text/csv）

---

### GET /stats

**説明**: 統計情報を取得

**レスポンス**:
```json
{
    "total_comments": 45,
    "avg_rubric_scores": {
        "理解度": 3.8,
        "論理性": 3.5,
        "独自性": 4.1,
        "実践性": 4.3,
        "表現力": 3.9
    },
    "avg_edit_time_seconds": 95,
    "avg_satisfaction": 4.2
}
```

---

### GET /health

**説明**: ヘルスチェック（認証不要）

**レスポンス**:
```json
{
    "status": "ok",
    "timestamp": "2025-11-11T10:30:00Z"
}
```

---

## 認証フロー

### 認証シーケンス図

```
┌──────┐          ┌──────────┐          ┌──────────────┐          ┌─────────┐
│ User │          │ Next.js  │          │ Supabase Auth│          │ FastAPI │
└───┬──┘          └────┬─────┘          └──────┬───────┘          └────┬────┘
    │                  │                        │                       │
    │ 1. Click "Login" │                        │                       │
    │─────────────────>│                        │                       │
    │                  │ 2. signInWithOAuth()   │                       │
    │                  │───────────────────────>│                       │
    │                  │                        │ 3. Redirect to Google │
    │                  │<───────────────────────│                       │
    │ 4. Google OAuth  │                        │                       │
    │<─────────────────────────────────────────>│                       │
    │                  │                        │                       │
    │                  │ 5. Return with JWT     │                       │
    │                  │<───────────────────────│                       │
    │                  │                        │                       │
    │                  │ 6. Store JWT in state  │                       │
    │                  │                        │                       │
    │ 7. API Request   │                        │                       │
    │─────────────────>│ 8. Add Authorization   │                       │
    │                  │    Bearer <JWT>        │                       │
    │                  │────────────────────────────────────────────────>│
    │                  │                        │                       │
    │                  │                        │ 9. Verify JWT         │
    │                  │                        │<──────────────────────│
    │                  │                        │                       │
    │                  │                        │ 10. JWT valid         │
    │                  │                        │──────────────────────>│
    │                  │                        │                       │
    │                  │ 11. Response           │                       │
    │                  │<────────────────────────────────────────────────│
    │ 12. Display      │                        │                       │
    │<─────────────────│                        │                       │
```

### 実装詳細

#### Next.js側（フロントエンド）

**Supabase クライアント初期化**:
```typescript
// lib/supabase.ts
import { createClient } from '@supabase/supabase-js'

const supabaseUrl = process.env.NEXT_PUBLIC_SUPABASE_URL!
const supabaseAnonKey = process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY!

export const supabase = createClient(supabaseUrl, supabaseAnonKey)
```

**ログイン処理**:
```typescript
// app/login/page.tsx
import { supabase } from '@/lib/supabase'

async function handleGoogleLogin() {
    const { data, error } = await supabase.auth.signInWithOAuth({
        provider: 'google',
        options: {
            redirectTo: `${window.location.origin}/auth/callback`
        }
    })
    if (error) console.error('Login error:', error)
}
```

**コールバック処理**:
```typescript
// app/auth/callback/route.ts
import { NextResponse } from 'next/server'
import { supabase } from '@/lib/supabase'

export async function GET(request: Request) {
    const { searchParams } = new URL(request.url)
    const code = searchParams.get('code')

    if (code) {
        await supabase.auth.exchangeCodeForSession(code)
    }

    return NextResponse.redirect('/dashboard')
}
```

**API呼び出し時のJWT送信**:
```typescript
// lib/api.ts
import { supabase } from '@/lib/supabase'

export async function generateComment(reportText: string, reportType: string) {
    const { data: { session } } = await supabase.auth.getSession()

    const response = await fetch('http://127.0.0.1:8010/generate', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${session?.access_token}`
        },
        body: JSON.stringify({
            report_text: reportText,
            report_type: reportType
        })
    })

    return response.json()
}
```

#### FastAPI側（バックエンド）

**認証ミドルウェア**:
```python
# api/auth.py
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import httpx

security = HTTPBearer()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_JWT_SECRET = os.getenv("SUPABASE_JWT_SECRET")

async def verify_token(credentials: HTTPAuthorizationCredentials = Depends(security)) -> str:
    """JWTを検証してユーザーIDを返す"""
    token = credentials.credentials

    # Supabase Auth APIでトークンを検証
    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"{SUPABASE_URL}/auth/v1/user",
            headers={"Authorization": f"Bearer {token}"}
        )

    if response.status_code != 200:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials"
        )

    user_data = response.json()
    return user_data["id"]
```

**エンドポイントでの使用**:
```python
# api/main.py
from api.auth import verify_token

@app.post("/generate")
async def generate_comment(
    req: GenerateRequest,
    user_id: str = Depends(verify_token)
):
    # user_id を使用して処理
    pass
```

---

## PII検出ロジック

### PIIDetectorクラス

**ファイル**: `api/pii_detector.py`

```python
import re
from typing import List, Dict
from dataclasses import dataclass

@dataclass
class PIIMatch:
    """PII検出結果"""
    type: str  # "name", "student_id", "email", "phone"
    value: str  # マッチした文字列
    start: int  # 開始位置
    end: int  # 終了位置

class PIIDetector:
    """個人情報検出クラス"""

    def __init__(self):
        # 正規表現パターン
        self.patterns = {
            "name": [
                # 日本語フルネーム（姓・名）
                r'[一-龯]{1,4}\s*[一-龯]{1,4}(?:さん|氏|様)?',
                # ひらがな・カタカナフルネーム
                r'[ぁ-ん]{2,4}\s*[ぁ-ん]{2,4}',
                r'[ァ-ヴー]{2,4}\s*[ァ-ヴー]{2,4}'
            ],
            "student_id": [
                # 学籍番号パターン（例: 2023A1234, A12345678）
                r'\d{4}[A-Z]\d{4,}',
                r'[A-Z]\d{8,}'
            ],
            "email": [
                # メールアドレス
                r'[\w\.-]+@[\w\.-]+\.\w+'
            ],
            "phone": [
                # 電話番号（ハイフン有無両対応）
                r'0\d{1,4}-?\d{1,4}-?\d{4}',
                r'\+81-?\d{1,4}-?\d{1,4}-?\d{4}'
            ]
        }

    def detect(self, text: str) -> List[PIIMatch]:
        """テキストからPIIを検出"""
        matches = []

        for pii_type, patterns in self.patterns.items():
            for pattern in patterns:
                for match in re.finditer(pattern, text):
                    matches.append(PIIMatch(
                        type=pii_type,
                        value=match.group(),
                        start=match.start(),
                        end=match.end()
                    ))

        # 重複を削除（開始位置でソート）
        matches.sort(key=lambda x: x.start)
        return self._remove_overlaps(matches)

    def _remove_overlaps(self, matches: List[PIIMatch]) -> List[PIIMatch]:
        """重複するマッチを削除"""
        if not matches:
            return []

        result = [matches[0]]
        for match in matches[1:]:
            if match.start >= result[-1].end:
                result.append(match)

        return result

    def mask(self, text: str, matches: List[PIIMatch]) -> str:
        """PIIをマスキング"""
        if not matches:
            return text

        # 後ろから置換（インデックスがずれないように）
        result = text
        for match in reversed(matches):
            mask_text = f"[{self._get_mask_label(match.type)}]"
            result = result[:match.start] + mask_text + result[match.end:]

        return result

    def _get_mask_label(self, pii_type: str) -> str:
        """PIIタイプに応じたマスクラベルを返す"""
        labels = {
            "name": "氏名",
            "student_id": "学籍番号",
            "email": "メールアドレス",
            "phone": "電話番号"
        }
        return labels.get(pii_type, "個人情報")
```

### 使用例

```python
# api/main.py
from api.pii_detector import PIIDetector

detector = PIIDetector()

@app.post("/generate")
async def generate_comment(req: GenerateRequest, user_id: str = Depends(verify_token)):
    # 1. PII検出
    pii_matches = detector.detect(req.report_text)

    # 2. マスキング
    masked_text = detector.mask(req.report_text, pii_matches)

    # 3. マスキング後のテキストをLLMに送信
    comment = await generate_comment_with_llm(masked_text, req.report_type)

    # 4. 元のテキストは暗号化して保存
    encrypted_text = encrypt(req.report_text)

    # 5. DBに保存
    history = await save_history(
        user_id=user_id,
        report_text_encrypted=encrypted_text,
        masked_text=masked_text,
        # ...
    )

    return {
        "history_id": history.id,
        "masked_text": masked_text,
        "pii_detected": [{"type": m.type, "value": "[マスク済み]"} for m in pii_matches],
        # ...
    }
```

---

## コンポーネント構成

### Next.js ディレクトリ構造

```
app/
├── (auth)/
│   ├── login/
│   │   └── page.tsx              # ログイン画面
│   └── auth/
│       └── callback/
│           └── route.ts          # OAuth コールバック
├── (dashboard)/
│   ├── layout.tsx                # 共通レイアウト
│   ├── page.tsx                  # メイン画面（コメント生成）
│   ├── history/
│   │   ├── page.tsx              # 履歴一覧
│   │   └── [id]/
│   │       └── page.tsx          # 履歴詳細
│   └── stats/
│       └── page.tsx              # 統計画面
├── api/
│   └── [...]/                    # API Routes（必要に応じて）
├── layout.tsx                    # ルートレイアウト
└── globals.css                   # グローバルCSS

components/
├── ui/
│   ├── Button.tsx                # ボタンコンポーネント
│   ├── TextArea.tsx              # テキストエリア
│   ├── Card.tsx                  # カード
│   ├── Tabs.tsx                  # タブ
│   ├── Modal.tsx                 # モーダル
│   └── Spinner.tsx               # ローディングスピナー
├── forms/
│   └── ReportInput.tsx           # レポート入力フォーム
├── results/
│   ├── RubricDisplay.tsx         # Rubric表示
│   ├── SummaryDisplay.tsx        # 要約表示
│   └── CommentEditor.tsx         # コメント編集
└── layout/
    ├── Header.tsx                # ヘッダー
    └── Sidebar.tsx               # サイドバー

lib/
├── supabase.ts                   # Supabase クライアント
├── api.ts                        # API呼び出し関数
└── utils.ts                      # ユーティリティ関数

styles/
└── design-tokens.css             # Academic Minimal UIトークン
```

### FastAPI ディレクトリ構造

```
api/
├── main.py                       # FastAPIアプリケーション
├── auth.py                       # 認証ミドルウェア
├── pii_detector.py               # PII検出クラス
├── comment_generator.py          # コメント生成ロジック
├── rubric_scorer.py              # Rubric採点ロジック
├── rag_search.py                 # RAG検索（Jaccard類似度）
├── encryption.py                 # データ暗号化
├── models.py                     # Pydanticモデル
└── database.py                   # Supabase DB接続

prompts/
├── reflection.txt                # reflectionプロンプト
└── final.txt                     # finalプロンプト

data/
└── sample_comments.json          # 過去コメント例（Phase 1のみ）
```

---

## デプロイメント

### Phase 1 デプロイ構成

**フロントエンド (Next.js)**:
- **ホスティング**: Vercel
- **ドメイン**: Vercel自動生成ドメイン（例: `your-app.vercel.app`）
- **環境変数**:
  ```
  NEXT_PUBLIC_SUPABASE_URL=https://xxx.supabase.co
  NEXT_PUBLIC_SUPABASE_ANON_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
  NEXT_PUBLIC_API_BASE_URL=http://127.0.0.1:8010
  ```

**バックエンド (FastAPI)**:
- **Phase 1**: 開発環境のみ（教授のローカルPC）
- **Phase 2-A**: クラウドホスティング検討（Render, Railway, AWS Lambda等）

**データベース (Supabase)**:
- **プラン**: Free Tier（Phase 1）
- **リージョン**: Asia Pacific (Tokyo)
- **環境変数**:
  ```
  SUPABASE_URL=https://xxx.supabase.co
  SUPABASE_ANON_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
  SUPABASE_SERVICE_ROLE_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
  DATABASE_URL=postgresql://postgres:password@db.xxx.supabase.co:5432/postgres
  ```

### デプロイ手順（Vercel）

1. **GitHubリポジトリ連携**:
   ```bash
   git init
   git add .
   git commit -m "Initial commit"
   git remote add origin https://github.com/your-username/your-repo.git
   git push -u origin main
   ```

2. **Vercelプロジェクト作成**:
   - Vercelダッシュボードで「New Project」
   - GitHubリポジトリを選択
   - Framework Preset: Next.js
   - Root Directory: `frontend/` (必要に応じて)

3. **環境変数設定**:
   - Settings > Environment Variables で設定

4. **デプロイ**:
   - `git push` で自動デプロイ

### Supabase セットアップ手順

1. **プロジェクト作成**:
   - https://supabase.com/dashboard
   - 「New Project」→ 名前・パスワード・リージョン選択

2. **Google OAuth 設定**:
   - Authentication > Providers > Google
   - Google Cloud Console で OAuth 2.0 クライアント作成
   - Authorized redirect URIs: `https://xxx.supabase.co/auth/v1/callback`
   - Client ID / Secret を Supabase に設定

3. **データベーステーブル作成**:
   - SQL Editor で上記の CREATE TABLE 文を実行

4. **RLS 有効化**:
   - 上記の RLS ポリシーを実行

---

## セキュリティ

### データ暗号化

**アルゴリズム**: AES-256-GCM

**実装**:
```python
# api/encryption.py
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend
import os
import base64

ENCRYPTION_KEY = os.getenv("ENCRYPTION_KEY")  # 32バイトのキー

def encrypt(plaintext: str) -> str:
    """テキストを暗号化"""
    # IVを生成（12バイト推奨）
    iv = os.urandom(12)

    # 暗号化
    cipher = Cipher(
        algorithms.AES(ENCRYPTION_KEY.encode()),
        modes.GCM(iv),
        backend=default_backend()
    )
    encryptor = cipher.encryptor()
    ciphertext = encryptor.update(plaintext.encode()) + encryptor.finalize()

    # IV + tag + ciphertext を Base64 エンコード
    result = iv + encryptor.tag + ciphertext
    return base64.b64encode(result).decode()

def decrypt(encrypted: str) -> str:
    """暗号化テキストを復号"""
    # Base64 デコード
    data = base64.b64decode(encrypted.encode())

    # IV, tag, ciphertext を分離
    iv = data[:12]
    tag = data[12:28]
    ciphertext = data[28:]

    # 復号
    cipher = Cipher(
        algorithms.AES(ENCRYPTION_KEY.encode()),
        modes.GCM(iv, tag),
        backend=default_backend()
    )
    decryptor = cipher.decryptor()
    plaintext = decryptor.update(ciphertext) + decryptor.finalize()

    return plaintext.decode()
```

### セキュリティヘッダ

**FastAPI設定**:
```python
# api/main.py
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

# CORS設定
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://your-app.vercel.app"],  # 本番ドメイン
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# セキュリティヘッダ
@app.middleware("http")
async def add_security_headers(request, call_next):
    response = await call_next(request)
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["X-XSS-Protection"] = "1; mode=block"
    response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
    return response
```

---

## 付録

### OpenAPI仕様書（自動生成）

FastAPIは自動的にOpenAPI仕様書を生成します:
- **Swagger UI**: `http://127.0.0.1:8010/docs`
- **ReDoc**: `http://127.0.0.1:8010/redoc`
- **JSON**: `http://127.0.0.1:8010/openapi.json`

### 環境変数一覧

**Next.js (.env.local)**:
```
NEXT_PUBLIC_SUPABASE_URL=https://xxx.supabase.co
NEXT_PUBLIC_SUPABASE_ANON_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
NEXT_PUBLIC_API_BASE_URL=http://127.0.0.1:8010
```

**FastAPI (.env)**:
```
SUPABASE_URL=https://xxx.supabase.co
SUPABASE_ANON_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
SUPABASE_SERVICE_ROLE_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
ENCRYPTION_KEY=your-32-byte-encryption-key
OPENAI_API_KEY=sk-proj-...
LLM_MODEL=gpt-4o-mini
```

---

**以上**
