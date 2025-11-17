-- ==========================================
-- 教授コメント自動化ボット データベーススキーマ
-- ==========================================

-- レポートテーブル
CREATE TABLE reports (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
  student_id TEXT,
  report_text TEXT NOT NULL,
  encrypted_text TEXT, -- 暗号化されたレポート本文（将来実装）
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- コメント生成結果テーブル
CREATE TABLE feedbacks (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
  report_id UUID REFERENCES reports(id) ON DELETE CASCADE,

  -- 生成されたコメント
  ai_comment TEXT NOT NULL,
  edited_comment TEXT, -- ユーザーが編集したコメント

  -- Rubric評価結果（JSONB形式）
  rubric JSONB NOT NULL,

  -- 要約結果（JSONB形式）
  summary JSONB NOT NULL,

  -- メタデータ
  llm_used BOOLEAN DEFAULT FALSE,
  llm_model TEXT,
  used_refs JSONB, -- 参照例のリスト

  -- 品質評価
  edit_time_seconds INTEGER, -- 手直し時間（秒）
  satisfaction_score INTEGER CHECK (satisfaction_score >= 1 AND satisfaction_score <= 5), -- 満足度（1-5）
  feedback_text TEXT, -- フィードバックコメント

  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- インデックス作成
CREATE INDEX idx_reports_user_id ON reports(user_id);
CREATE INDEX idx_reports_created_at ON reports(created_at DESC);
CREATE INDEX idx_feedbacks_user_id ON feedbacks(user_id);
CREATE INDEX idx_feedbacks_report_id ON feedbacks(report_id);
CREATE INDEX idx_feedbacks_created_at ON feedbacks(created_at DESC);

-- Row Level Security (RLS) 有効化
ALTER TABLE reports ENABLE ROW LEVEL SECURITY;
ALTER TABLE feedbacks ENABLE ROW LEVEL SECURITY;

-- RLSポリシー: ユーザーは自分のデータのみ閲覧・操作可能
CREATE POLICY "Users can view their own reports"
  ON reports FOR SELECT
  USING (auth.uid() = user_id);

CREATE POLICY "Users can insert their own reports"
  ON reports FOR INSERT
  WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Users can update their own reports"
  ON reports FOR UPDATE
  USING (auth.uid() = user_id);

CREATE POLICY "Users can delete their own reports"
  ON reports FOR DELETE
  USING (auth.uid() = user_id);

CREATE POLICY "Users can view their own feedbacks"
  ON feedbacks FOR SELECT
  USING (auth.uid() = user_id);

CREATE POLICY "Users can insert their own feedbacks"
  ON feedbacks FOR INSERT
  WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Users can update their own feedbacks"
  ON feedbacks FOR UPDATE
  USING (auth.uid() = user_id);

CREATE POLICY "Users can delete their own feedbacks"
  ON feedbacks FOR DELETE
  USING (auth.uid() = user_id);

-- 更新日時を自動更新するトリガー関数
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
  NEW.updated_at = NOW();
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- トリガー設定
CREATE TRIGGER update_reports_updated_at
  BEFORE UPDATE ON reports
  FOR EACH ROW
  EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_feedbacks_updated_at
  BEFORE UPDATE ON feedbacks
  FOR EACH ROW
  EXECUTE FUNCTION update_updated_at_column();

-- ==========================================
-- 参照例（ナレッジベース）テーブル
-- ==========================================

CREATE TABLE knowledge_base (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  reference_id TEXT UNIQUE NOT NULL, -- 元のID（prof_0001等）
  type TEXT NOT NULL CHECK (type IN ('reflection', 'final')), -- レポート種別
  text TEXT NOT NULL, -- コメント本文
  tags TEXT[], -- タグ配列
  source TEXT DEFAULT 'professor_examples', -- データソース
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- インデックス作成
CREATE INDEX idx_knowledge_base_type ON knowledge_base(type);
CREATE INDEX idx_knowledge_base_created_at ON knowledge_base(created_at DESC);

-- RLS設定（全ユーザーが読み取り可能）
ALTER TABLE knowledge_base ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Anyone can view knowledge base"
  ON knowledge_base FOR SELECT
  USING (true); -- 全員が読み取り可能

-- 管理者のみ書き込み可能（今後実装予定）
-- CREATE POLICY "Only admins can insert knowledge base"
--   ON knowledge_base FOR INSERT
--   WITH CHECK (auth.jwt() ->> 'role' = 'admin');

-- トリガー設定
CREATE TRIGGER update_knowledge_base_updated_at
  BEFORE UPDATE ON knowledge_base
  FOR EACH ROW
  EXECUTE FUNCTION update_updated_at_column();
