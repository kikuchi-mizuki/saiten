-- ==========================================
-- Phase 2: Embeddingベースの検索関数
-- ==========================================
-- このSQLをSupabase SQL Editorで実行してください
-- 前提: 02_alter_knowledge_base.sql が実行済み

-- Embeddingベースの類似検索関数
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

-- 関数の説明:
-- - <=> はコサイン距離を計算（0に近いほど類似）
-- - 1 - distance で類似度に変換（1に近いほど類似）
-- - ORDER BY で最も類似したものから順に取得
-- - LIMIT で上位N件を取得

-- テスト: ダミーのEmbeddingで検索を試す（実際のEmbeddingは1536次元なので、テストは後で実施）
-- SELECT * FROM search_knowledge_by_embedding(
--   ARRAY[0.1, 0.2, 0.3, ...]::vector(1536),
--   5
-- );
