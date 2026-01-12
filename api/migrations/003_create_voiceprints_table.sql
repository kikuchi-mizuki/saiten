-- 教授の声紋を保存するテーブル
CREATE TABLE IF NOT EXISTS professor_voiceprints (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
    voiceprint_name VARCHAR(255) NOT NULL,
    embedding VECTOR(192),  -- 声紋ベクトル（192次元、SpeechBrain ECAPA-TDNN）
    audio_duration_seconds INT NOT NULL,
    sample_count INT DEFAULT 1,  -- 学習に使用したサンプル数
    confidence_score FLOAT,  -- 声紋の信頼度スコア (0.0-1.0)
    metadata JSONB,  -- その他のメタデータ（ファイル名、言語、etc）
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    is_active BOOLEAN DEFAULT true,  -- 複数の声紋を管理する場合に使用

    CONSTRAINT voiceprint_confidence_range CHECK (confidence_score >= 0.0 AND confidence_score <= 1.0),
    CONSTRAINT voiceprint_duration_positive CHECK (audio_duration_seconds > 0),
    CONSTRAINT voiceprint_sample_count_positive CHECK (sample_count > 0)
);

-- インデックス
CREATE INDEX IF NOT EXISTS idx_voiceprints_user_id ON professor_voiceprints(user_id);
CREATE INDEX IF NOT EXISTS idx_voiceprints_is_active ON professor_voiceprints(is_active);
CREATE INDEX IF NOT EXISTS idx_voiceprints_created_at ON professor_voiceprints(created_at DESC);

-- 声紋のベクトル検索用インデックス（コサイン類似度）
CREATE INDEX IF NOT EXISTS idx_voiceprints_embedding ON professor_voiceprints
USING ivfflat (embedding vector_cosine_ops) WITH (lists = 100);

-- RLS (Row Level Security) ポリシー
ALTER TABLE professor_voiceprints ENABLE ROW LEVEL SECURITY;

-- ユーザーは自分の声紋のみ閲覧可能
CREATE POLICY "Users can view their own voiceprints"
    ON professor_voiceprints
    FOR SELECT
    USING (auth.uid() = user_id);

-- ユーザーは自分の声紋のみ作成可能
CREATE POLICY "Users can create their own voiceprints"
    ON professor_voiceprints
    FOR INSERT
    WITH CHECK (auth.uid() = user_id);

-- ユーザーは自分の声紋のみ更新可能
CREATE POLICY "Users can update their own voiceprints"
    ON professor_voiceprints
    FOR UPDATE
    USING (auth.uid() = user_id);

-- ユーザーは自分の声紋のみ削除可能
CREATE POLICY "Users can delete their own voiceprints"
    ON professor_voiceprints
    FOR DELETE
    USING (auth.uid() = user_id);

-- updated_atの自動更新トリガー
CREATE OR REPLACE FUNCTION update_voiceprints_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER voiceprints_updated_at_trigger
    BEFORE UPDATE ON professor_voiceprints
    FOR EACH ROW
    EXECUTE FUNCTION update_voiceprints_updated_at();

-- コメント
COMMENT ON TABLE professor_voiceprints IS '教授の声紋データを保存するテーブル。音声識別・話者認識に使用';
COMMENT ON COLUMN professor_voiceprints.embedding IS 'SpeechBrain ECAPA-TDNNで抽出した192次元の声紋ベクトル';
COMMENT ON COLUMN professor_voiceprints.sample_count IS '継続学習で使用したサンプル数。増えるほど精度向上';
COMMENT ON COLUMN professor_voiceprints.confidence_score IS '声紋の信頼度スコア。0.9以上が推奨';
COMMENT ON COLUMN professor_voiceprints.is_active IS '複数の声紋がある場合、アクティブなもののみ使用';
