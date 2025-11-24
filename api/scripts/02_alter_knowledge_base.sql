-- ==========================================
-- Phase 2: knowledge_baseテーブルの拡張
-- ==========================================
-- このSQLをSupabase SQL Editorで実行してください
-- 前提: 01_enable_pgvector.sql が実行済み

-- 1. knowledge_baseテーブルに新しいカラムを追加
ALTER TABLE knowledge_base
  ADD COLUMN IF NOT EXISTS content_type TEXT NOT NULL DEFAULT 'comment',
  ADD COLUMN IF NOT EXISTS tags TEXT[] DEFAULT '{}',
  ADD COLUMN IF NOT EXISTS source TEXT,
  ADD COLUMN IF NOT EXISTS embedding VECTOR(1536);

-- 2. embeddingカラムにインデックスを作成（ベクトル検索用）
-- IVFFlat: 高速な近似最近傍探索アルゴリズム
-- lists = 100: クラスタ数（データ量に応じて調整、目安: sqrt(データ数)）
CREATE INDEX IF NOT EXISTS knowledge_base_embedding_idx
ON knowledge_base
USING ivfflat (embedding vector_cosine_ops)
WITH (lists = 100);

-- 3. テーブル構造を確認
\d knowledge_base

-- 期待される出力:
-- カラム一覧に以下が含まれていることを確認:
-- - content_type: text
-- - tags: text[]
-- - source: text
-- - embedding: vector(1536)
