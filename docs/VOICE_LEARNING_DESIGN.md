# 教授の声紋学習機能 設計書

**作成日**: 2026-01-12
**目的**: 教授の声を学習し、次回から自動で教授の発言のみを抽出
**優先度**: High

---

## 🎯 機能概要

### コンセプト

**「一度教えれば、ずっと覚えている」**

1. **初回セットアップ**: 教授の声を登録（3-5分の音声サンプル）
2. **声紋抽出**: 声の特徴を数値化して保存
3. **自動識別**: 次回から自動で教授の声を判定
4. **継続学習**: 使うほど精度が向上

---

## 🧠 技術アプローチ

### 方法: **Speaker Embedding（話者埋め込み）**

声の特徴を高次元ベクトルに変換して保存・比較する技術

**使用ライブラリ**: `speechbrain` または `pyannote.audio`

```python
from speechbrain.pretrained import SpeakerRecognition

# モデルの読み込み
verifier = SpeakerRecognition.from_hparams(
    source="speechbrain/spkrec-ecapa-voxceleb",
    savedir="pretrained_models/spkrec"
)

# 教授の声から声紋を抽出
professor_embedding = verifier.encode_batch(professor_audio)

# 新しい音声と比較
score = verifier.verify_batch(new_audio, professor_embedding)
# score > 0.25 なら同一人物と判定
```

---

## 📊 システム設計

### 処理フロー

```
【初回セットアップ】
教授の音声サンプル（3-5分）
    ↓
声紋抽出（Speaker Embedding）
    ↓
データベースに保存（professor_voiceprint）
    ↓
完了！


【2回目以降の音声アップロード】
講義音声（複数話者）
    ↓
話者識別（pyannote.audio）
    ↓
各話者の声紋を抽出
    ↓
保存済みの教授の声紋と比較
    ↓
類似度 > 閾値 → 教授と判定
    ↓
教授の発言のみを抽出
    ↓
データベースに保存
```

---

## 💾 データベース設計

### 新しいテーブル: `professor_voiceprints`

教授の声紋データを保存するテーブル

```sql
CREATE TABLE professor_voiceprints (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES auth.users(id),
    voiceprint_name VARCHAR(255) NOT NULL,  -- 例: "榎戸教授 2026年1月"
    embedding VECTOR(192),  -- 声紋ベクトル（192次元）
    audio_duration_seconds INT NOT NULL,  -- サンプル音声の長さ
    sample_count INT DEFAULT 1,  -- サンプル数（継続学習で増加）
    confidence_score FLOAT,  -- 声紋の信頼度（0.0-1.0）
    metadata JSONB,  -- 追加情報
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    is_active BOOLEAN DEFAULT true  -- アクティブな声紋かどうか
);

-- インデックス
CREATE INDEX idx_voiceprints_user ON professor_voiceprints(user_id);
CREATE INDEX idx_voiceprints_active ON professor_voiceprints(user_id, is_active);
```

### metadata の構造例

```json
{
    "source_filename": "lecture_sample_2026-01-12.mp3",
    "recording_date": "2026-01-12",
    "recording_environment": "講義室",
    "sample_quality": "high",
    "notes": "通常の講義音声から抽出"
}
```

---

## 🎨 UI/UX設計

### 初回セットアップフロー

#### Step 1: セットアップ画面（新規）

```
┌─────────────────────────────────────────┐
│  🎤 教授の声を登録                        │
├─────────────────────────────────────────┤
│                                         │
│  声を学習させることで、次回から自動的に   │
│  教授の発言のみを抽出できるようになります │
│                                         │
│  【必要なもの】                          │
│  ・ 3-5分程度の音声サンプル              │
│  ・ 教授のみが話している部分              │
│                                         │
│  ┌───────────────────────────┐          │
│  │ 📁 音声サンプルを選択      │          │
│  └───────────────────────────┘          │
│                                         │
│  [次へ]                                 │
└─────────────────────────────────────────┘
```

#### Step 2: 音声確認画面

```
┌─────────────────────────────────────────┐
│  🔍 音声を確認                           │
├─────────────────────────────────────────┤
│                                         │
│  📄 ファイル: lecture_sample.mp3        │
│  ⏱️  長さ: 4分32秒                       │
│                                         │
│  🎧 [再生] [停止]                        │
│  ━━━━━━━━━━━━━━━━━━━━━━ 0:00 / 4:32     │
│                                         │
│  ✅ 確認事項:                            │
│  ・ 教授のみが話していますか？            │
│  ・ 雑音が少ない音声ですか？              │
│                                         │
│  [戻る] [声を登録する]                   │
└─────────────────────────────────────────┘
```

#### Step 3: 処理中画面

```
┌─────────────────────────────────────────┐
│  🧠 声を学習中...                        │
├─────────────────────────────────────────┤
│                                         │
│  [████████████░░░░░░░░░] 65%            │
│                                         │
│  ✓ 音声をテキスト化しました               │
│  ✓ 話者を識別しています...               │
│  ⏳ 声紋を抽出しています...               │
│                                         │
│  しばらくお待ちください（約30秒）          │
└─────────────────────────────────────────┘
```

#### Step 4: 完了画面

```
┌─────────────────────────────────────────┐
│  ✅ 声の登録が完了しました！              │
├─────────────────────────────────────────┤
│                                         │
│  🎤 登録名: 榎戸教授 2026年1月           │
│  📊 信頼度: 95%                          │
│  ⏱️  サンプル長: 4分32秒                 │
│                                         │
│  次回から音声をアップロードすると、        │
│  自動的に教授の発言のみを抽出します。      │
│                                         │
│  💡 ヒント:                              │
│  複数のサンプルを登録すると精度が向上します│
│                                         │
│  [もう1つ登録] [完了]                    │
└─────────────────────────────────────────┘
```

---

### 2回目以降の音声アップロード

#### 自動識別の表示

```
┌─────────────────────────────────────────┐
│  📁 lecture_2026-01-15.mp3              │
├─────────────────────────────────────────┤
│                                         │
│  🎤 話者を自動識別中...                  │
│                                         │
│  ✅ 教授の声を検出しました！              │
│     類似度: 92% (高精度)                 │
│                                         │
│  📊 発言の内訳:                          │
│  ・ 教授: 18分30秒 (82%)                │
│  ・ その他: 4分10秒 (18%)                │
│                                         │
│  ☑️ 教授の発言のみを保存                 │
│                                         │
│  [保存] [全員の発言を保存]               │
└─────────────────────────────────────────┘
```

---

## 🔧 実装詳細

### 1. 声紋抽出（Speaker Embedding）

```python
from speechbrain.pretrained import SpeakerRecognition
import torch

class VoiceprintExtractor:
    """教授の声紋を抽出・管理するクラス"""

    def __init__(self):
        # SpeechBrainのECAPA-TDNNモデル（業界標準）
        self.verifier = SpeakerRecognition.from_hparams(
            source="speechbrain/spkrec-ecapa-voxceleb",
            savedir="models/speaker_recognition"
        )

    def extract_voiceprint(self, audio_path: str) -> np.ndarray:
        """
        音声ファイルから声紋を抽出

        Returns:
            np.ndarray: 192次元の声紋ベクトル
        """
        # 音声を読み込み
        signal = self.verifier.load_audio(audio_path)

        # 声紋を抽出（192次元ベクトル）
        embedding = self.verifier.encode_batch(signal)

        return embedding.squeeze().cpu().numpy()

    def compare_voiceprints(
        self,
        voiceprint1: np.ndarray,
        voiceprint2: np.ndarray
    ) -> float:
        """
        2つの声紋を比較

        Returns:
            float: 類似度スコア（0.0-1.0、高いほど類似）
        """
        # コサイン類似度を計算
        similarity = np.dot(voiceprint1, voiceprint2) / (
            np.linalg.norm(voiceprint1) * np.linalg.norm(voiceprint2)
        )

        return float(similarity)

    def is_same_speaker(
        self,
        voiceprint1: np.ndarray,
        voiceprint2: np.ndarray,
        threshold: float = 0.25
    ) -> bool:
        """
        同一話者かどうかを判定

        Args:
            threshold: 閾値（デフォルト0.25、業界標準）
        """
        similarity = self.compare_voiceprints(voiceprint1, voiceprint2)
        return similarity > threshold
```

---

### 2. データベース操作

```python
async def save_professor_voiceprint(
    user_id: str,
    voiceprint_name: str,
    embedding: np.ndarray,
    audio_duration: int,
    metadata: dict
) -> dict:
    """教授の声紋をデータベースに保存"""

    # 埋め込みベクトルをリストに変換
    embedding_list = embedding.tolist()

    response = supabase.table("professor_voiceprints").insert({
        "user_id": user_id,
        "voiceprint_name": voiceprint_name,
        "embedding": embedding_list,
        "audio_duration_seconds": audio_duration,
        "sample_count": 1,
        "confidence_score": 0.85,  # 初期値
        "metadata": metadata,
        "is_active": True
    }).execute()

    return response.data[0]


async def get_professor_voiceprint(user_id: str) -> Optional[np.ndarray]:
    """ユーザーの教授声紋を取得"""

    response = supabase.table("professor_voiceprints") \
        .select("embedding") \
        .eq("user_id", user_id) \
        .eq("is_active", True) \
        .order("updated_at", desc=True) \
        .limit(1) \
        .execute()

    if not response.data:
        return None

    # リストをnumpy配列に変換
    embedding = np.array(response.data[0]["embedding"])
    return embedding
```

---

### 3. 自動識別ロジック

```python
async def identify_professor_in_audio(
    audio_path: str,
    user_id: str
) -> dict:
    """
    音声から教授の発言を自動識別

    Returns:
        {
            "professor_segments": [...],  # 教授の発言セグメント
            "other_segments": [...],      # その他の発言
            "confidence": 0.92,           # 判定の信頼度
            "professor_duration": 1110,   # 教授の発言時間（秒）
            "total_duration": 1350        # 全体の長さ（秒）
        }
    """
    # 1. 保存済みの教授の声紋を取得
    professor_voiceprint = await get_professor_voiceprint(user_id)

    if professor_voiceprint is None:
        raise ValueError("教授の声紋が登録されていません")

    # 2. 音声から話者を識別
    from pyannote.audio import Pipeline
    diarization = Pipeline.from_pretrained(
        "pyannote/speaker-diarization-3.1"
    )

    diarization_result = diarization(audio_path)

    # 3. 各話者の声紋を抽出
    extractor = VoiceprintExtractor()
    speaker_voiceprints = {}

    for turn, _, speaker in diarization_result.itertracks(yield_label=True):
        if speaker not in speaker_voiceprints:
            # この話者の音声セグメントを抽出
            segment_audio = extract_audio_segment(
                audio_path,
                turn.start,
                turn.end
            )

            # 声紋を抽出
            voiceprint = extractor.extract_voiceprint(segment_audio)
            speaker_voiceprints[speaker] = voiceprint

    # 4. 教授の声紋と比較
    professor_speaker = None
    max_similarity = 0.0

    for speaker, voiceprint in speaker_voiceprints.items():
        similarity = extractor.compare_voiceprints(
            professor_voiceprint,
            voiceprint
        )

        if similarity > max_similarity:
            max_similarity = similarity
            professor_speaker = speaker

    # 5. 教授の発言セグメントを抽出
    professor_segments = []
    other_segments = []
    professor_duration = 0

    for turn, _, speaker in diarization_result.itertracks(yield_label=True):
        segment = {
            "start": turn.start,
            "end": turn.end,
            "duration": turn.end - turn.start,
            "speaker": speaker
        }

        if speaker == professor_speaker:
            professor_segments.append(segment)
            professor_duration += segment["duration"]
        else:
            other_segments.append(segment)

    return {
        "professor_segments": professor_segments,
        "other_segments": other_segments,
        "confidence": max_similarity,
        "professor_duration": int(professor_duration),
        "total_duration": int(diarization_result.get_timeline().duration()),
        "professor_speaker_id": professor_speaker
    }
```

---

## 📈 継続学習（Incremental Learning）

### 声紋の精度向上

使うほど精度が向上する仕組み：

```python
async def update_professor_voiceprint(
    user_id: str,
    new_voiceprint: np.ndarray,
    confidence: float
):
    """
    新しい音声サンプルで声紋を更新

    アプローチ: 移動平均で既存の声紋を更新
    """
    # 既存の声紋を取得
    existing = supabase.table("professor_voiceprints") \
        .select("*") \
        .eq("user_id", user_id) \
        .eq("is_active", True) \
        .single() \
        .execute()

    if not existing.data:
        return

    old_embedding = np.array(existing.data["embedding"])
    old_count = existing.data["sample_count"]

    # 移動平均で更新
    # 新しい声紋の重みは信頼度に応じて調整
    weight = min(confidence, 0.3)  # 最大30%の影響
    updated_embedding = (
        old_embedding * (1 - weight) + new_voiceprint * weight
    )

    # データベースを更新
    supabase.table("professor_voiceprints") \
        .update({
            "embedding": updated_embedding.tolist(),
            "sample_count": old_count + 1,
            "confidence_score": min(
                existing.data["confidence_score"] + 0.02,
                0.99
            ),
            "updated_at": "NOW()"
        }) \
        .eq("id", existing.data["id"]) \
        .execute()
```

---

## 🔒 セキュリティとプライバシー

### 声紋データの取り扱い

1. **暗号化**: 声紋ベクトルは暗号化して保存
2. **アクセス制御**: ユーザー自身の声紋のみアクセス可能
3. **削除権**: ユーザーはいつでも声紋を削除可能

### 同意取得

初回セットアップ時に表示：

```
📢 声紋データの取り扱いについて

・ 声紋データは声の特徴を数値化したものです
・ 元の音声を復元することはできません
・ 教授の発言を自動識別する目的でのみ使用します
・ いつでも削除できます

[ ] 同意する
```

---

## 💰 コストとパフォーマンス

### モデルサイズ

| モデル | サイズ | 用途 |
|--------|--------|------|
| SpeechBrain ECAPA-TDNN | 約200MB | 声紋抽出 |
| pyannote.audio | 約1GB | 話者識別 |

### 処理時間

| 処理 | 時間（30分音声） |
|------|-----------------|
| 声紋抽出（初回） | 約10秒 |
| 話者識別 | 約60秒 |
| 声紋比較 | 約1秒 |
| **合計** | **約70秒** |

### APIコスト

- **Whisper API**: $0.18（30分）
- **SpeechBrain**: 無料（ローカル実行）
- **pyannote.audio**: 無料（Hugging Face Token必要）

---

## 🚀 実装ロードマップ

### Week 1: 基盤構築
- [ ] SpeechBrainのセットアップ
- [ ] データベーステーブル作成
- [ ] 声紋抽出APIの実装

### Week 2: 初回セットアップUI
- [ ] 声紋登録画面の実装
- [ ] 音声サンプルのアップロード機能
- [ ] 声紋抽出・保存ロジック

### Week 3: 自動識別機能
- [ ] 話者識別との統合
- [ ] 声紋照合ロジックの実装
- [ ] 教授発言の自動抽出

### Week 4: 継続学習と最適化
- [ ] 声紋更新ロジックの実装
- [ ] 精度モニタリング
- [ ] パフォーマンス最適化

---

## 📊 成功指標（KPI）

| 指標 | 目標値 |
|------|--------|
| 初回識別精度 | 90%以上 |
| 5回使用後の精度 | 95%以上 |
| 誤判定率 | 5%以下 |
| 処理時間（30分音声） | 90秒以内 |
| ユーザー満足度 | 4.5/5以上 |

---

## 🔄 使用フロー（完成後）

### 初回のみ

1. 設定 > 声の登録
2. 3-5分の音声サンプルをアップロード
3. 「声を登録する」をクリック
4. 完了！

### 2回目以降

1. 参照例管理 > ファイルから読み込む
2. 講義音声をアップロード
3. **自動で教授の発言のみが抽出される** ✨
4. 確認して保存

---

**次のアクション**: 実装開始の承認待ち

実装を開始しますか？
