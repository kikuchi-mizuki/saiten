# Phase 2: 開発手順書

**最終更新**: 2025-11-24
**バージョン**: 1.0
**対象**: Phase 2開発者向け
**前提**: Phase 1 MVP完成済み

---

## 📋 目次

1. [Phase 2概要](#phase-2概要)
2. [開発環境準備](#開発環境準備)
3. [Week 1-2: RAG基盤強化](#week-1-2-rag基盤強化)
4. [Week 3-4: ナレッジベース管理UI](#week-3-4-ナレッジベース管理ui)
5. [Week 5-6: 音声入力機能](#week-5-6-音声入力機能)
6. [Week 7: PPT資料生成機能](#week-7-ppt資料生成機能)
7. [Week 8: テスト・改善・ドキュメント](#week-8-テスト改善ドキュメント)
8. [トラブルシューティング](#トラブルシューティング)

---

## Phase 2概要

### 目標
教授の思考を学習し、講義・講演用PPT資料を自動生成するシステムへのアップグレード

### 開発期間
**8週間**（2025-11-25 ～ 2026-01-19予定）

### 主要機能
1. RAG精度向上（Embedding + pgvector）
2. ナレッジベース管理UI（ファイルアップロード・テキストで教授の思考を追加）
3. ファイルアップロード機能（Whisper API）- **要件変更**: 音声録音 → ファイルアップロード
4. PPT資料自動生成機能

---

## 開発環境準備

### 前提条件
- Phase 1の開発環境が正常に動作していること
- Node.js 18+, Python 3.11+がインストール済み
- Supabaseプロジェクトが作成済み
- OpenAI APIキーが設定済み

### 新規に必要な設定

#### 1. OpenAI Embeddings APIキー確認
Phase 1で使用しているOpenAI APIキーがEmbeddings APIにも対応していることを確認。

```bash
# 環境変数確認
echo $OPENAI_API_KEY
```

#### 2. Supabase pgvector拡張の有効化

Supabaseダッシュボードで以下を実行：

1. Project Settings → Database → Extensions
2. `vector` 拡張を検索して有効化

または、SQL Editorで：

```sql
-- pgvector拡張を有効化
CREATE EXTENSION IF NOT EXISTS vector;

-- 確認
SELECT * FROM pg_extension WHERE extname = 'vector';
```

#### 3. Python依存関係の追加

```bash
# プロジェクトルートで実行
cd api
pip install openai python-pptx
pip freeze > requirements.txt
```

**新規追加パッケージ**:
- `openai`: OpenAI API（Embeddings, Whisper）
- `python-pptx`: PPTファイル生成

#### 4. 環境変数の追加

`.env` ファイルに以下を追加：

```bash
# Phase 2用の設定
EMBEDDING_MODEL=text-embedding-3-small
EMBEDDING_DIMENSIONS=1536
MAX_AUDIO_DURATION_SECONDS=600  # 10分
PPT_TEMPLATE_PATH=./templates/default.pptx
```

---

## Week 1-2: RAG基盤強化

### 目標
Embeddingベースの高精度検索を実装

### Day 1-2: OpenAI Embeddings API統合

#### 1. Embedding生成関数の実装

`api/utils/embedding.py` を作成：

```python
import os
from openai import OpenAI
from typing import List

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "text-embedding-3-small")
EMBEDDING_DIMENSIONS = int(os.getenv("EMBEDDING_DIMENSIONS", "1536"))

def generate_embedding(text: str) -> List[float]:
    """
    テキストをEmbedding化する

    Args:
        text: Embedding化するテキスト

    Returns:
        List[float]: Embeddingベクトル（1536次元）
    """
    try:
        response = client.embeddings.create(
            model=EMBEDDING_MODEL,
            input=text
        )
        return response.data[0].embedding
    except Exception as e:
        print(f"Embedding generation error: {e}")
        raise

def generate_embeddings_batch(texts: List[str]) -> List[List[float]]:
    """
    複数のテキストを一括でEmbedding化する

    Args:
        texts: Embedding化するテキストのリスト

    Returns:
        List[List[float]]: Embeddingベクトルのリスト
    """
    try:
        response = client.embeddings.create(
            model=EMBEDDING_MODEL,
            input=texts
        )
        return [data.embedding for data in response.data]
    except Exception as e:
        print(f"Batch embedding generation error: {e}")
        raise
```

#### 2. テスト実行

```python
# api/utils/embedding.py の末尾に追加（テスト用）
if __name__ == "__main__":
    # テスト
    test_text = "学生が起業を考えるとき、まず顧客視点を持つことが重要です。"
    embedding = generate_embedding(test_text)
    print(f"Embedding dimensions: {len(embedding)}")
    print(f"First 5 values: {embedding[:5]}")
```

実行：

```bash
cd api
python utils/embedding.py
# 出力例:
# Embedding dimensions: 1536
# First 5 values: [0.023, -0.015, 0.042, ...]
```

### Day 3-4: Supabase pgvector設定

#### 1. knowledge_baseテーブルの拡張

Supabase SQL Editorで以下を実行：

```sql
-- knowledge_baseテーブルにカラム追加
ALTER TABLE knowledge_base
  ADD COLUMN content_type TEXT NOT NULL DEFAULT 'comment',
  ADD COLUMN tags TEXT[] DEFAULT '{}',
  ADD COLUMN source TEXT,
  ADD COLUMN embedding VECTOR(1536);

-- インデックス作成（ベクトル検索用）
CREATE INDEX ON knowledge_base
USING ivfflat (embedding vector_cosine_ops)
WITH (lists = 100);

-- 既存データの確認
SELECT id, comment_text, report_type, content_type, tags
FROM knowledge_base
LIMIT 5;
```

#### 2. Supabase Pythonクライアントの更新

`api/utils/supabase_client.py` に以下を追加：

```python
def insert_knowledge_with_embedding(
    comment_text: str,
    content_type: str,
    report_type: str,
    tags: List[str],
    source: str,
    embedding: List[float]
) -> dict:
    """
    Embeddingを含むナレッジベースを追加
    """
    try:
        result = supabase.table("knowledge_base").insert({
            "comment_text": comment_text,
            "content_type": content_type,
            "report_type": report_type,
            "tags": tags,
            "source": source,
            "embedding": embedding
        }).execute()
        return result.data[0]
    except Exception as e:
        print(f"Insert knowledge with embedding error: {e}")
        raise

def search_knowledge_by_embedding(
    query_embedding: List[float],
    limit: int = 5
) -> List[dict]:
    """
    Embeddingベースでナレッジベースを検索
    """
    try:
        # pgvectorのコサイン類似度検索
        # RPC関数を使用（後で作成）
        result = supabase.rpc(
            "search_knowledge_by_embedding",
            {
                "query_embedding": query_embedding,
                "match_count": limit
            }
        ).execute()
        return result.data
    except Exception as e:
        print(f"Search knowledge by embedding error: {e}")
        raise
```

#### 3. Supabase RPC関数の作成

Supabase SQL Editorで以下を実行：

```sql
-- Embeddingベースの検索関数
CREATE OR REPLACE FUNCTION search_knowledge_by_embedding(
  query_embedding VECTOR(1536),
  match_count INT DEFAULT 5
)
RETURNS TABLE (
  id UUID,
  comment_text TEXT,
  content_type TEXT,
  report_type TEXT,
  tags TEXT[],
  source TEXT,
  similarity FLOAT
)
LANGUAGE plpgsql
AS $$
BEGIN
  RETURN QUERY
  SELECT
    kb.id,
    kb.comment_text,
    kb.content_type,
    kb.report_type,
    kb.tags,
    kb.source,
    1 - (kb.embedding <=> query_embedding) AS similarity
  FROM knowledge_base kb
  WHERE kb.embedding IS NOT NULL
  ORDER BY kb.embedding <=> query_embedding
  LIMIT match_count;
END;
$$;
```

### Day 5-7: 既存データのEmbedding化

#### 1. バッチ処理スクリプトの作成

`api/scripts/migrate_embeddings.py` を作成：

```python
import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from utils.embedding import generate_embeddings_batch
from utils.supabase_client import supabase

def migrate_embeddings():
    """
    既存のknowledge_baseデータをEmbedding化
    """
    # 既存データ取得
    result = supabase.table("knowledge_base").select("*").execute()
    knowledge_items = result.data

    print(f"Total items: {len(knowledge_items)}")

    # バッチサイズ（OpenAI APIの制限を考慮）
    batch_size = 100

    for i in range(0, len(knowledge_items), batch_size):
        batch = knowledge_items[i:i+batch_size]
        texts = [item["comment_text"] for item in batch]

        print(f"Processing batch {i//batch_size + 1}...")

        # Embedding生成
        embeddings = generate_embeddings_batch(texts)

        # 更新
        for item, embedding in zip(batch, embeddings):
            supabase.table("knowledge_base").update({
                "embedding": embedding
            }).eq("id", item["id"]).execute()

        print(f"Batch {i//batch_size + 1} completed.")

    print("All embeddings migrated successfully!")

if __name__ == "__main__":
    migrate_embeddings()
```

#### 2. 実行

```bash
cd api
python scripts/migrate_embeddings.py
```

### Day 8-10: コサイン類似度検索の実装

#### 1. RAG検索関数の更新

`api/utils/rag.py` を更新：

```python
from utils.embedding import generate_embedding
from utils.supabase_client import search_knowledge_by_embedding

def search_similar_comments_embedding(
    query_text: str,
    limit: int = 5
) -> List[dict]:
    """
    Embeddingベースでコメント検索

    Args:
        query_text: 検索クエリ
        limit: 取得件数

    Returns:
        類似コメントのリスト
    """
    # クエリをEmbedding化
    query_embedding = generate_embedding(query_text)

    # pgvectorで検索
    results = search_knowledge_by_embedding(query_embedding, limit)

    return results
```

#### 2. メインAPIの更新

`api/main.py` の `generate` エンドポイントを更新：

```python
# RAG検索部分を変更
# 旧: Jaccard類似度
# similar_comments = search_similar_comments_jaccard(masked_text, limit=2)

# 新: Embedding類似度
similar_comments = search_similar_comments_embedding(masked_text, limit=5)
```

### Day 11-14: 検索精度の検証

#### 1. 検証スクリプトの作成

`api/scripts/evaluate_rag.py` を作成：

```python
import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from utils.rag import search_similar_comments_jaccard, search_similar_comments_embedding

def evaluate_rag():
    """
    JaccardとEmbeddingの検索精度を比較
    """
    # テストクエリ（Phase 1のサンプルレポートから抽出）
    test_queries = [
        "起業において顧客視点が重要だと学んだ",
        "競争戦略の本質は差別化である",
        "リーダーシップには共感力が必要",
        # ... 20件程度用意
    ]

    for i, query in enumerate(test_queries):
        print(f"\n=== Test {i+1}: {query[:30]}... ===")

        # Jaccard検索
        jaccard_results = search_similar_comments_jaccard(query, limit=3)
        print("\n[Jaccard Results]")
        for j, result in enumerate(jaccard_results):
            print(f"{j+1}. {result['comment_text'][:50]}...")

        # Embedding検索
        embedding_results = search_similar_comments_embedding(query, limit=3)
        print("\n[Embedding Results]")
        for j, result in enumerate(embedding_results):
            print(f"{j+1}. (similarity: {result['similarity']:.3f}) {result['comment_text'][:50]}...")

        # 教授に評価してもらう（手動）
        print("\n教授評価:")
        print("Jaccard: [ ] 関連性あり [ ] やや関連 [ ] 関連なし")
        print("Embedding: [ ] 関連性あり [ ] やや関連 [ ] 関連なし")
        input("Enterキーで次へ...")

if __name__ == "__main__":
    evaluate_rag()
```

#### 2. 検証実施

```bash
cd api
python scripts/evaluate_rag.py
```

教授に20件のクエリで評価してもらい、結果を記録。

**Week 1-2 完了基準**:
- [ ] Embedding生成関数が動作する
- [ ] pgvector検索が動作する
- [ ] 既存113件がEmbedding化されている
- [ ] 検証レポート完成（Jaccard vs Embedding）

---

## Week 3-4: ナレッジベース管理UI

### 目標
教授が思考を追加・管理できる画面を実装

### Day 1-3: ナレッジベース一覧画面

#### 1. ページファイル作成

`frontend/app/knowledge-base/page.tsx` を作成：

```tsx
'use client'

import { useEffect, useState } from 'react'
import { useRouter } from 'next/navigation'
import Link from 'next/link'
import { getCurrentUser, signOut } from '@/lib/auth'
import type { User } from '@supabase/supabase-js'

interface KnowledgeItem {
  id: string
  comment_text: string
  content_type: string
  report_type: string
  tags: string[]
  source: string
  created_at: string
}

export default function KnowledgeBasePage() {
  const router = useRouter()
  const [user, setUser] = useState<User | null>(null)
  const [isLoading, setIsLoading] = useState(true)
  const [knowledge, setKnowledge] = useState<KnowledgeItem[]>([])
  const [searchQuery, setSearchQuery] = useState('')
  const [selectedTag, setSelectedTag] = useState('all')

  useEffect(() => {
    async function checkAuth() {
      const currentUser = await getCurrentUser()
      if (!currentUser) {
        router.push('/login')
        return
      }
      setUser(currentUser)
      await loadKnowledge()
      setIsLoading(false)
    }
    checkAuth()
  }, [router])

  async function loadKnowledge() {
    try {
      const response = await fetch('/api/knowledge-base', {
        headers: {
          'Authorization': `Bearer ${await getToken()}`
        }
      })
      const data = await response.json()
      setKnowledge(data.knowledge)
    } catch (error) {
      console.error('Load knowledge error:', error)
      alert('ナレッジベースの読み込みに失敗しました')
    }
  }

  // フィルタリング
  const filteredKnowledge = knowledge.filter(item => {
    const matchesSearch = item.comment_text.includes(searchQuery)
    const matchesTag = selectedTag === 'all' || item.tags.includes(selectedTag)
    return matchesSearch && matchesTag
  })

  // 全タグを抽出
  const allTags = Array.from(new Set(knowledge.flatMap(item => item.tags)))

  if (isLoading) {
    return <div>読み込み中...</div>
  }

  return (
    <div className="min-h-screen" style={{ backgroundColor: 'var(--bg)' }}>
      {/* ヘッダー */}
      <header className="border-b" style={{ backgroundColor: 'var(--surface)', borderColor: 'var(--border)' }}>
        <div className="max-w-7xl mx-auto px-6 py-4 flex items-center justify-between">
          <h1 className="text-[18px] font-semibold" style={{ color: 'var(--text)' }}>
            ナレッジベース管理
          </h1>
          <div className="flex items-center gap-4">
            <Link href="/dashboard" className="px-4 py-2 rounded-[var(--radius-sm)] text-[13px] font-medium transition">
              ダッシュボード
            </Link>
            <button onClick={async () => { await signOut(); router.push('/login'); }}>
              ログアウト
            </button>
          </div>
        </div>
      </header>

      {/* メインコンテンツ */}
      <main className="max-w-7xl mx-auto px-6 py-8">
        {/* アクションボタン */}
        <div className="flex justify-end gap-3 mb-6">
          <Link href="/knowledge-base/add-text" className="px-4 py-2 rounded">
            新規追加（テキスト）
          </Link>
          <Link href="/knowledge-base/add-audio" className="px-4 py-2 rounded">
            音声入力
          </Link>
        </div>

        {/* 検索・フィルタ */}
        <div className="mb-6 flex gap-4">
          <input
            type="text"
            placeholder="検索..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="flex-1 px-4 py-2 rounded border"
          />
          <select
            value={selectedTag}
            onChange={(e) => setSelectedTag(e.target.value)}
            className="px-4 py-2 rounded border"
          >
            <option value="all">全て</option>
            {allTags.map(tag => (
              <option key={tag} value={tag}>{tag}</option>
            ))}
          </select>
        </div>

        {/* 一覧 */}
        <div className="space-y-4">
          {filteredKnowledge.map((item) => (
            <div key={item.id} className="p-6 rounded border">
              <div className="flex items-start justify-between mb-3">
                <div className="flex-1">
                  <div className="flex gap-2 mb-2">
                    {item.tags.map(tag => (
                      <span key={tag} className="px-2 py-1 text-[12px] rounded" style={{ backgroundColor: 'var(--surface-subtle)' }}>
                        {tag}
                      </span>
                    ))}
                  </div>
                  <p className="text-[14px]" style={{ color: 'var(--text)' }}>
                    {item.comment_text.substring(0, 100)}...
                  </p>
                  <p className="text-[12px] mt-2" style={{ color: 'var(--text-muted)' }}>
                    {new Date(item.created_at).toLocaleString('ja-JP')} | {item.content_type} | ソース: {item.source || 'N/A'}
                  </p>
                </div>
                <div className="flex gap-2">
                  <Link href={`/knowledge-base/edit/${item.id}`} className="px-3 py-1 text-[13px] rounded">
                    編集
                  </Link>
                  <button onClick={() => handleDelete(item.id)} className="px-3 py-1 text-[13px] rounded">
                    削除
                  </button>
                </div>
              </div>
            </div>
          ))}
        </div>
      </main>
    </div>
  )
}
```

#### 2. バックエンドAPI実装

`api/main.py` に以下を追加：

```python
@app.get("/knowledge-base")
async def get_knowledge_base(
    authorization: str = Header(None),
    page: int = 1,
    limit: int = 20
):
    """
    ナレッジベース一覧取得
    """
    # JWT検証（省略）
    user_id = verify_jwt(authorization)

    # ナレッジベース取得（全ユーザー共通）
    offset = (page - 1) * limit
    result = supabase.table("knowledge_base")\
        .select("*")\
        .order("created_at", desc=True)\
        .range(offset, offset + limit - 1)\
        .execute()

    return {
        "knowledge": result.data,
        "total": len(result.data)
    }
```

### Day 4-7: テキスト追加機能

#### 1. テキスト追加ページ

`frontend/app/knowledge-base/add-text/page.tsx` を作成：

```tsx
'use client'

import { useState } from 'react'
import { useRouter } from 'next/navigation'

export default function AddTextPage() {
  const router = useRouter()
  const [text, setText] = useState('')
  const [contentType, setContentType] = useState('comment')
  const [suggestedTags, setSuggestedTags] = useState<string[]>([])
  const [tags, setTags] = useState<string[]>([])
  const [isGeneratingTags, setIsGeneratingTags] = useState(false)

  async function handleGenerateTags() {
    if (!text.trim()) {
      alert('テキストを入力してください')
      return
    }

    setIsGeneratingTags(true)
    try {
      const response = await fetch('/api/generate-tags', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${await getToken()}`
        },
        body: JSON.stringify({ text })
      })
      const data = await response.json()
      setSuggestedTags(data.tags)
      setTags(data.tags)
    } catch (error) {
      console.error('Generate tags error:', error)
      alert('タグ生成に失敗しました')
    } finally {
      setIsGeneratingTags(false)
    }
  }

  async function handleSave() {
    if (!text.trim()) {
      alert('テキストを入力してください')
      return
    }

    try {
      const response = await fetch('/api/knowledge-base', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${await getToken()}`
        },
        body: JSON.stringify({
          text,
          content_type: contentType,
          tags,
          source: 'text'
        })
      })

      if (response.ok) {
        router.push('/knowledge-base')
      } else {
        alert('保存に失敗しました')
      }
    } catch (error) {
      console.error('Save error:', error)
      alert('保存に失敗しました')
    }
  }

  return (
    <div className="min-h-screen p-8">
      <h1 className="text-[18px] font-semibold mb-6">新規追加（テキスト）</h1>

      <div className="max-w-4xl">
        <label className="block mb-2 text-[14px]">内容:</label>
        <textarea
          value={text}
          onChange={(e) => setText(e.target.value)}
          className="w-full h-64 p-3 border rounded"
          placeholder="教授の思考を入力してください..."
        />
        <p className="text-[12px] text-right mt-1">文字数: {text.length}</p>

        <label className="block mb-2 mt-6 text-[14px]">コンテンツタイプ:</label>
        <div className="flex gap-4">
          <label>
            <input type="radio" value="comment" checked={contentType === 'comment'} onChange={(e) => setContentType(e.target.value)} />
            コメント例
          </label>
          <label>
            <input type="radio" value="lecture" checked={contentType === 'lecture'} onChange={(e) => setContentType(e.target.value)} />
            講義内容
          </label>
          <label>
            <input type="radio" value="speech" checked={contentType === 'speech'} onChange={(e) => setContentType(e.target.value)} />
            講演内容
          </label>
          <label>
            <input type="radio" value="memo" checked={contentType === 'memo'} onChange={(e) => setContentType(e.target.value)} />
            メモ
          </label>
        </div>

        <button
          onClick={handleGenerateTags}
          disabled={isGeneratingTags}
          className="mt-6 px-4 py-2 rounded"
        >
          {isGeneratingTags ? 'タグ生成中...' : 'AIでタグを提案'}
        </button>

        {suggestedTags.length > 0 && (
          <div className="mt-4">
            <label className="block mb-2 text-[14px]">提案タグ:</label>
            <div className="flex gap-2 flex-wrap">
              {suggestedTags.map(tag => (
                <span key={tag} className="px-3 py-1 text-[13px] rounded border">
                  {tag}
                </span>
              ))}
            </div>
          </div>
        )}

        <div className="mt-8 flex gap-4">
          <button onClick={handleSave} className="px-6 py-2 rounded">
            保存
          </button>
          <button onClick={() => router.back()} className="px-6 py-2 rounded">
            キャンセル
          </button>
        </div>
      </div>
    </div>
  )
}
```

#### 2. タグ生成API

`api/main.py` に以下を追加：

```python
@app.post("/generate-tags")
async def generate_tags(
    request: dict,
    authorization: str = Header(None)
):
    """
    テキストから自動でタグを生成
    """
    # JWT検証（省略）
    user_id = verify_jwt(authorization)

    text = request.get("text")

    # LLMでタグ生成
    prompt = f"""以下のテキストを読み、適切なタグを3-5個提案してください。
タグは「起業論」「戦略論」「リーダーシップ」「組織論」「イノベーション」「顧客視点」などの形式で、
日本語で簡潔に記述してください。

テキスト:
{text}

タグ（カンマ区切りで出力）:"""

    response = call_openai(prompt, max_tokens=50, system_message="あなたはテキスト分類の専門家です。")
    tags_str = response.strip()
    tags = [tag.strip() for tag in tags_str.split(',')]

    return {"tags": tags}

@app.post("/knowledge-base")
async def add_knowledge(
    request: dict,
    authorization: str = Header(None)
):
    """
    ナレッジベースに追加
    """
    # JWT検証（省略）
    user_id = verify_jwt(authorization)

    text = request.get("text")
    content_type = request.get("content_type")
    tags = request.get("tags", [])
    source = request.get("source", "text")

    # Embedding生成
    from utils.embedding import generate_embedding
    embedding = generate_embedding(text)

    # データベース保存
    from utils.supabase_client import insert_knowledge_with_embedding
    result = insert_knowledge_with_embedding(
        comment_text=text,
        content_type=content_type,
        report_type="reflection",  # デフォルト
        tags=tags,
        source=source,
        embedding=embedding
    )

    return {"success": True, "knowledge": result}
```

### Day 8-14: 編集・削除機能

（詳細は省略。基本的なCRUD操作を実装）

**Week 3-4 完了基準**:
- [ ] ナレッジベース一覧画面が動作する
- [ ] テキスト追加機能が動作する
- [ ] AI自動タグ付けが動作する
- [ ] 編集・削除機能が動作する

---

## Week 5-6: ファイルアップロード機能

**要件変更**: 音声録音機能（MediaRecorder API）→ ファイルアップロード機能に変更

### 目標
音声/テキストファイルをアップロードしてナレッジベースに追加できるようにする

### Day 1-5: フロントエンドファイルアップロード機能

#### 1. ファイルアップロードページ

`frontend/app/knowledge-base/upload-file/page.tsx` を作成：

```tsx
'use client'

import { useState } from 'react'
import { useRouter } from 'next/navigation'

export default function UploadFilePage() {
  const router = useRouter()
  const [selectedFile, setSelectedFile] = useState<File | null>(null)
  const [isDragging, setIsDragging] = useState(false)
  const [isUploading, setIsUploading] = useState(false)
  const [uploadProgress, setUploadProgress] = useState(0)
  const [extractedText, setExtractedText] = useState('')
  const [suggestedTags, setSuggestedTags] = useState<string[]>([])

  // ドラッグ&ドロップ処理
  function handleDragEnter(e: React.DragEvent) {
    e.preventDefault()
    setIsDragging(true)
  }

  function handleDragLeave(e: React.DragEvent) {
    e.preventDefault()
    setIsDragging(false)
  }

  function handleDrop(e: React.DragEvent) {
    e.preventDefault()
    setIsDragging(false)
    const files = e.dataTransfer.files
    if (files.length > 0) {
      handleFileSelect(files[0])
    }
  }

  // ファイル選択処理
  function handleFileSelect(file: File) {
    // ファイルタイプ検証
    const validAudioTypes = ['audio/mpeg', 'audio/wav', 'audio/m4a']
    const validTextTypes = ['text/plain']

    if (!validAudioTypes.includes(file.type) && !validTextTypes.includes(file.type)) {
      alert('対応していないファイル形式です。mp3, wav, m4a, txt のみ対応しています。')
      return
    }

    // ファイルサイズ検証
    const maxSize = validAudioTypes.includes(file.type) ? 25 * 1024 * 1024 : 1 * 1024 * 1024
    if (file.size > maxSize) {
      alert(`ファイルサイズが大きすぎます。${validAudioTypes.includes(file.type) ? '25MB' : '1MB'}以下にしてください。`)
      return
    }

    setSelectedFile(file)
  }

  // アップロード処理
  async function handleUpload() {
    if (!selectedFile) return

    setIsUploading(true)
    setUploadProgress(0)

    try {
      const formData = new FormData()
      formData.append('file', selectedFile)

      // プログレスバーのシミュレーション（実際のアップロードプログレスは別途実装が必要）
      const progressInterval = setInterval(() => {
        setUploadProgress(prev => Math.min(prev + 10, 90))
      }, 200)

      const response = await fetch('/api/upload-file', {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${await getToken()}`
        },
        body: formData
      })

      clearInterval(progressInterval)
      setUploadProgress(100)

      const data = await response.json()
      setExtractedText(data.text)
      setSuggestedTags(data.suggested_tags)
    } catch (error) {
      console.error('Upload error:', error)
      alert('ファイルのアップロードに失敗しました')
    } finally {
      setIsUploading(false)
    }
  }

  return (
    <div className="min-h-screen p-8">
      <h1 className="text-[18px] font-semibold mb-6">ファイルアップロード</h1>

      <div className="max-w-2xl mx-auto">
        {!selectedFile && (
          <div
            className={`text-center p-12 border-2 border-dashed rounded ${isDragging ? 'border-blue-500 bg-blue-50' : 'border-gray-300'}`}
            onDragEnter={handleDragEnter}
            onDragOver={(e) => e.preventDefault()}
            onDragLeave={handleDragLeave}
            onDrop={handleDrop}
          >
            <div className="text-[48px] mb-4">📁</div>
            <p className="text-[16px] mb-4">ファイルをドラッグ&ドロップ</p>
            <p className="text-[14px] mb-6">または</p>
            <label className="px-6 py-3 rounded text-[16px] cursor-pointer inline-block bg-blue-500 text-white">
              📎 ファイルを選択
              <input
                type="file"
                accept=".mp3,.wav,.m4a,.txt"
                className="hidden"
                onChange={(e) => {
                  if (e.target.files && e.target.files.length > 0) {
                    handleFileSelect(e.target.files[0])
                  }
                }}
              />
            </label>
            <p className="text-[12px] mt-6 text-gray-500">
              対応形式:<br />
              • 音声: mp3, wav, m4a（最大25MB）<br />
              • テキスト: txt（最大1MB）
            </p>
          </div>
        )}

        {selectedFile && !extractedText && (
          <div className="text-center p-12 border rounded">
            <div className="text-[48px] mb-4">✅</div>
            <p className="text-[18px] mb-2">ファイル選択: {selectedFile.name}</p>
            <p className="text-[14px] mb-6">サイズ: {(selectedFile.size / 1024 / 1024).toFixed(2)}MB</p>

            {!isUploading && (
              <button onClick={handleUpload} className="px-6 py-3 rounded text-[16px] bg-blue-500 text-white">
                🚀 アップロード開始
              </button>
            )}

            {isUploading && (
              <div>
                <p className="text-[16px] mb-4">🔄 アップロード中...</p>
                <div className="w-full bg-gray-200 rounded h-4 mb-4">
                  <div
                    className="bg-blue-500 h-4 rounded transition-all"
                    style={{ width: `${uploadProgress}%` }}
                  />
                </div>
                <p className="text-[14px] text-gray-500">
                  {selectedFile.type.startsWith('audio/') && uploadProgress === 100 && '🔄 テキスト変換中...（Whisper APIで処理中）'}
                </p>
              </div>
            )}
          </div>
        )}

        {extractedText && (
          <div className="p-6 border rounded">
            <p className="text-[14px] mb-2">抽出されたテキスト:</p>
            <textarea
              value={extractedText}
              onChange={(e) => setExtractedText(e.target.value)}
              className="w-full h-64 p-3 border rounded mb-4"
            />

            <p className="text-[14px] mb-2">提案タグ:</p>
            <div className="flex gap-2 flex-wrap mb-4">
              {suggestedTags.map(tag => (
                <span key={tag} className="px-3 py-1 text-[13px] rounded border bg-gray-100">
                  {tag}
                </span>
              ))}
            </div>

            <div className="mt-4 flex gap-4">
              <button
                onClick={() => router.push(`/knowledge-base/add-text?text=${encodeURIComponent(extractedText)}&tags=${suggestedTags.join(',')}`)}
                className="px-6 py-2 rounded bg-blue-500 text-white"
              >
                保存
              </button>
              <button
                onClick={() => {
                  setSelectedFile(null);
                  setExtractedText('');
                  setSuggestedTags([]);
                }}
                className="px-6 py-2 rounded border"
              >
                やり直し
              </button>
            </div>
          </div>
        )}
      </div>
    </div>
  )
}
```

### Day 6-10: Whisper API統合とテキスト抽出

#### 1. ファイルアップロードAPI

`api/main.py` に以下を追加：

```python
from openai import OpenAI
import os
import chardet

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

@app.post("/upload-file")
async def upload_file(
    file: UploadFile = File(...),
    authorization: str = Header(None)
):
    """
    音声/テキストファイルをアップロードしてテキスト抽出
    """
    # JWT検証（省略）
    user_id = verify_jwt(authorization)

    # ファイルタイプ判定
    file_extension = file.filename.split('.')[-1].lower()

    if file_extension in ['mp3', 'wav', 'm4a']:
        # 音声ファイル処理
        return await handle_audio_file(file)
    elif file_extension == 'txt':
        # テキストファイル処理
        return await handle_text_file(file)
    else:
        raise HTTPException(status_code=400, detail="対応していないファイル形式です")

async def handle_audio_file(file: UploadFile):
    """音声ファイルの処理"""
    # 一時保存
    audio_path = f"/tmp/{file.filename}"
    with open(audio_path, "wb") as f:
        f.write(await file.read())

    try:
        # Whisper APIで変換
        with open(audio_path, "rb") as audio_file:
            transcript = client.audio.transcriptions.create(
                model="whisper-1",
                file=audio_file,
                language="ja"
            )

        # 一時ファイル削除
        os.remove(audio_path)

        # タグ生成
        suggested_tags = await generate_tags_from_text(transcript.text)

        return {
            "text": transcript.text,
            "suggested_tags": suggested_tags,
            "file_type": "audio"
        }
    except Exception as e:
        print(f"Audio processing error: {e}")
        if os.path.exists(audio_path):
            os.remove(audio_path)
        raise HTTPException(status_code=500, detail="音声変換に失敗しました")

async def handle_text_file(file: UploadFile):
    """テキストファイルの処理"""
    try:
        # ファイル内容を読み込み
        content = await file.read()

        # 文字コード自動検出
        detected = chardet.detect(content)
        encoding = detected['encoding'] or 'utf-8'

        # デコード
        text = content.decode(encoding)

        # タグ生成
        suggested_tags = await generate_tags_from_text(text)

        return {
            "text": text,
            "suggested_tags": suggested_tags,
            "file_type": "text"
        }
    except Exception as e:
        print(f"Text file processing error: {e}")
        raise HTTPException(status_code=500, detail="テキストファイルの読み込みに失敗しました")

async def generate_tags_from_text(text: str) -> list:
    """LLMでタグを生成"""
    prompt = f"""以下のテキストを読み、適切なタグを3-5個提案してください。
タグは「起業論」「戦略論」「リーダーシップ」「組織論」「イノベーション」「顧客視点」などの形式で、
日本語で簡潔に記述してください。

テキスト:
{text[:500]}...

タグ（カンマ区切りで出力）:"""

    response = call_openai(prompt, max_tokens=50, system_message="あなたはテキスト分類の専門家です。")
    tags_str = response.strip()
    tags = [tag.strip() for tag in tags_str.split(',')]

    return tags[:5]
```

#### 2. 依存パッケージの追加

```bash
pip install chardet
pip freeze > requirements.txt
```

**Week 5-6 完了基準**:
- [ ] ファイルアップロード機能が動作する（ドラッグ&ドロップ、ファイル選択）
- [ ] 音声ファイル（mp3, wav, m4a）→Whisper APIでテキスト変換が動作する
- [ ] テキストファイル（txt）→内容抽出が動作する
- [ ] LLM自動タグ付けが動作する
- [ ] 変換されたテキストをナレッジベースに保存できる

---

## Week 7: PPT資料生成機能

### 目標
ターゲット・構成を指定してPPT生成

### Day 1-3: PPT生成入力画面

`frontend/app/ppt-generator/page.tsx` を作成（実装は省略、要件定義書参照）

### Day 4-7: バックエンドPPT生成API

#### 1. PPT生成関数

`api/utils/ppt_generator.py` を作成：

```python
from pptx import Presentation
from pptx.util import Inches, Pt
from typing import List, Dict

def generate_ppt(
    target_audience: str,
    theme: str,
    structure: List[str],
    slide_contents: List[Dict[str, str]]
) -> str:
    """
    PPTファイルを生成

    Args:
        target_audience: ターゲット
        theme: テーマ
        structure: 構成
        slide_contents: スライド内容（タイトル + 本文）

    Returns:
        生成されたPPTファイルのパス
    """
    prs = Presentation()

    # スライドサイズ設定（16:9）
    prs.slide_width = Inches(10)
    prs.slide_height = Inches(7.5)

    # タイトルスライド
    title_slide_layout = prs.slide_layouts[0]
    slide = prs.slides.add_slide(title_slide_layout)
    title = slide.shapes.title
    subtitle = slide.placeholders[1]
    title.text = theme
    subtitle.text = f"対象: {target_audience}"

    # 各スライド
    for content in slide_contents:
        slide_layout = prs.slide_layouts[1]  # タイトル + 本文
        slide = prs.slides.add_slide(slide_layout)
        title = slide.shapes.title
        body = slide.placeholders[1]

        title.text = content["title"]
        text_frame = body.text_frame
        text_frame.text = content["body"]

    # 保存
    output_path = f"/tmp/{theme}_{target_audience}.pptx"
    prs.save(output_path)

    return output_path
```

#### 2. PPT生成API

`api/main.py` に以下を追加：

```python
@app.post("/generate-ppt")
async def generate_ppt_endpoint(
    request: dict,
    authorization: str = Header(None)
):
    """
    PPT資料を自動生成
    """
    # JWT検証（省略）
    user_id = verify_jwt(authorization)

    target_audience = request.get("target_audience")
    theme = request.get("theme")
    structure = request.get("structure")  # ["導入", "理論解説", ...]

    # 1. テーマをEmbedding化
    from utils.embedding import generate_embedding
    theme_embedding = generate_embedding(theme)

    # 2. 関連ナレッジベース検索
    from utils.supabase_client import search_knowledge_by_embedding
    related_knowledge = search_knowledge_by_embedding(theme_embedding, limit=20)

    # 3. 各セクションのスライド内容を生成
    slide_contents = []
    for section in structure:
        # プロンプト作成
        knowledge_text = "\n".join([k["comment_text"] for k in related_knowledge[:5]])
        prompt = f"""以下の関連する教授の思考を参考に、「{section}」セクションのスライドを作成してください。

対象: {target_audience}
テーマ: {theme}
セクション: {section}

関連する教授の思考:
{knowledge_text}

スライドのタイトルと本文（箇条書き、3-5項目）を生成してください。

タイトル:
本文:
-
-
-"""

        # LLM（gpt-4o）で生成
        response = call_openai(prompt, max_tokens=500, system_message="あなたは教授の思考を学んだ資料作成アシスタントです。", model="gpt-4o")

        # パース（簡易版）
        lines = response.strip().split('\n')
        title = lines[0].replace('タイトル:', '').strip()
        body = '\n'.join([line.strip() for line in lines[2:] if line.strip()])

        slide_contents.append({
            "title": title,
            "body": body
        })

    # 4. PPTファイル生成
    from utils.ppt_generator import generate_ppt as generate_ppt_file
    ppt_path = generate_ppt_file(target_audience, theme, structure, slide_contents)

    # 5. ファイルをレスポンスとして返す
    from fastapi.responses import FileResponse
    return FileResponse(
        path=ppt_path,
        filename=f"{theme}_{target_audience}.pptx",
        media_type="application/vnd.openxmlformats-officedocument.presentationml.presentation"
    )
```

**Week 7 完了基準**:
- [ ] PPT生成入力画面が動作する
- [ ] PPT生成APIが動作する
- [ ] PPTファイルがダウンロードできる

---

## Week 8: テスト・改善・ドキュメント

（詳細は省略）

**Week 8 完了基準**:
- [ ] 統合テスト完了
- [ ] UAT完了
- [ ] ドキュメント完成

---

## トラブルシューティング

### pgvector拡張が有効化できない
- Supabaseの無料プランでは利用できない場合があります
- Proプランへのアップグレードを検討

### Whisper API が動作しない
- 音声ファイルのサイズを確認（上限25MB）
- ファイル形式を確認（.mp3, .wav, .m4a等）

### PPT生成が遅い
- LLM呼び出しを並列化
- スライド数を制限（上限20枚）

---

**以上**
