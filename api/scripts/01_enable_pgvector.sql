-- ==========================================
-- Phase 2: pgvector拡張の有効化
-- ==========================================
-- このSQLをSupabase SQL Editorで実行してください

-- 1. pgvector拡張を有効化
CREATE EXTENSION IF NOT EXISTS vector;

-- 2. 拡張が有効化されたか確認
SELECT * FROM pg_extension WHERE extname = 'vector';

-- 期待される出力:
-- extname | vector
-- extversion | 0.5.0 (またはそれ以上)
