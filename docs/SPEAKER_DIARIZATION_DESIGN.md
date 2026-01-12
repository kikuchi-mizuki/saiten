# 話者識別機能の設計書

**作成日**: 2026-01-12
**対象**: 参照例音声アップロード機能
**目的**: 教授の声だけを識別してデータベースに保存

---

## 🎯 機能概要

音声ファイルから**教授の発言のみを自動抽出**し、参照例としてデータベースに保存する機能。

### ユースケース

1. **講義録音からの抽出**
   - 教授と学生が混在する講義音声
   - 教授の発言のみを参照例として保存

2. **ゼミ・ディスカッションからの抽出**
   - 複数の学生と教授の対話
   - 教授のコメント部分のみを抽出

3. **個別指導の記録**
   - 1対1の指導音声
   - 教授の指導内容を蓄積

---

## 🔧 技術アーキテクチャ

### 処理フロー

```
音声ファイル
    ↓
[1] Whisper API（タイムスタンプ付き文字起こし）
    ↓
[2] pyannote.audio（話者識別）
    ↓
[3] マッチング（どの発言が誰のものか）
    ↓
[4] 教授の発言を抽出
    ↓
[5] データベースに保存
```

---

## 📦 使用技術

### 1. Whisper API（OpenAI）

**役割**: 音声をテキストに変換し、各単語のタイムスタンプを取得

**APIリクエスト例**:
```python
from openai import OpenAI

client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

with open("lecture.mp3", "rb") as audio_file:
    transcript = client.audio.transcriptions.create(
        model="whisper-1",
        file=audio_file,
        language="ja",
        response_format="verbose_json",  # タイムスタンプ付き
        timestamp_granularities=["segment"]  # セグメント単位
    )
```

**レスポンス例**:
```json
{
  "text": "それでは今日の講義を始めます...",
  "segments": [
    {
      "start": 0.0,
      "end": 3.5,
      "text": "それでは今日の講義を始めます"
    },
    {
      "start": 4.0,
      "end": 8.2,
      "text": "先週お話しした戦略立案について..."
    }
  ]
}
```

---

### 2. pyannote.audio（話者識別）

**役割**: 音声から話者を区別（Speaker A, Speaker B, ...）

**インストール**:
```bash
pip install pyannote.audio
```

**使用例**:
```python
from pyannote.audio import Pipeline

# Hugging Faceのトークンが必要（無料）
pipeline = Pipeline.from_pretrained(
    "pyannote/speaker-diarization-3.1",
    use_auth_token="hf_xxxxxxxxxxxxx"
)

# 話者識別の実行
diarization = pipeline("lecture.mp3")

# 結果の取得
for turn, _, speaker in diarization.itertracks(yield_label=True):
    print(f"{turn.start:.1f}s - {turn.end:.1f}s: {speaker}")
```

**出力例**:
```
0.0s - 3.5s: SPEAKER_00  # 教授
4.0s - 8.2s: SPEAKER_00  # 教授
10.5s - 15.3s: SPEAKER_01  # 学生A
16.0s - 22.1s: SPEAKER_00  # 教授
```

---

## 🧠 教授の声の特定ロジック

### アプローチ1: 発言時間ベース（自動判定）

**仮説**: 講義では教授が最も長く話す

**ロジック**:
```python
def identify_professor_speaker(diarization):
    """最も発言時間が長い話者を教授と判定"""
    speaker_durations = {}

    for turn, _, speaker in diarization.itertracks(yield_label=True):
        duration = turn.end - turn.start
        speaker_durations[speaker] = speaker_durations.get(speaker, 0) + duration

    # 最も発言時間が長い話者
    professor_speaker = max(speaker_durations, key=speaker_durations.get)

    return professor_speaker, speaker_durations
```

**メリット**:
- 完全自動
- ほとんどのケースで正確

**デメリット**:
- 学生が長く話す場合に誤判定の可能性

---

### アプローチ2: UI選択（手動確認）

**フロー**:
1. 話者ごとの発言時間を表示
2. サンプル音声を再生
3. 教授がどの話者かを手動選択

**UI例**:
```
話者の識別結果：

[ ] SPEAKER_00（発言時間: 15分30秒）🔊再生
    サンプル: "それでは今日の講義を始めます..."

[✓] SPEAKER_01（発言時間: 2分10秒）🔊再生
    サンプル: "先生、質問があります..."

[ ] SPEAKER_02（発言時間: 1分45秒）🔊再生
    サンプル: "なるほど、わかりました..."

👉 教授の声を選択してください
```

**メリット**:
- 100%正確
- ユーザーが確認できる

**デメリット**:
- 手動操作が必要

---

### アプローチ3: ハイブリッド（推奨）

1. **自動判定**: 最も発言時間が長い話者を教授候補として提示
2. **確認UI**: ユーザーが確認・修正可能
3. **学習**: 一度選択した声の特徴を保存し、次回から自動判定の精度向上

---

## 💾 データベーススキーマ拡張

### knowledge_base テーブルに追加

```sql
ALTER TABLE knowledge_base ADD COLUMN IF NOT EXISTS speaker_metadata JSONB;
```

**speaker_metadata の構造**:
```json
{
  "is_professor": true,
  "speaker_id": "SPEAKER_00",
  "confidence": 0.95,
  "audio_timestamp": {
    "start": 10.5,
    "end": 22.1
  },
  "total_speakers": 3,
  "speaker_durations": {
    "SPEAKER_00": 930.5,
    "SPEAKER_01": 130.2,
    "SPEAKER_02": 105.3
  }
}
```

---

## 🎨 UI/UX設計

### 参照例アップロード画面の拡張

**現在の画面**:
```
[ファイル選択] [アップロード]
```

**拡張後**:
```
[ファイル選択]

📁 選択中: lecture_2024-01-12.mp3

⚙️ オプション:
[ ] 話者を識別して教授の発言のみを抽出

[アップロード]
```

---

### 話者選択画面（新規）

アップロード後、話者が複数検出された場合に表示：

```
🎤 話者を検出しました

話者A（発言時間: 15分30秒）🎧
サンプル: "それでは今日の講義を始めます。先週お話しした..."
[ ] この話者が教授

話者B（発言時間: 2分10秒）🎧
サンプル: "先生、質問があります。戦略立案の際に..."
[✓] この話者が教授

話者C（発言時間: 1分45秒）🎧
サンプル: "なるほど、わかりました。ありがとうございます..."
[ ] この話者が教授

[次へ] [スキップ（全員の発言を保存）]
```

---

## 📊 処理時間の見積もり

| 音声時間 | Whisper API | pyannote.audio | 合計 |
|---------|-------------|----------------|------|
| 5分 | 10秒 | 15秒 | **25秒** |
| 30分 | 30秒 | 60秒 | **90秒** |
| 60分 | 60秒 | 120秒 | **180秒** |

**注意**: pyannote.audioは初回実行時にモデルダウンロードが必要（約1GB）

---

## 💰 コスト見積もり

### Whisper API

- **料金**: $0.006 / 分
- **例**: 30分の講義 = $0.18（約27円）

### pyannote.audio

- **料金**: 無料（オープンソース）
- **要件**: Hugging Face Token（無料）

### 合計

- **月間100時間の音声処理**: 約$36（約5,400円）

---

## 🔐 セキュリティ・プライバシー

### 音声データの取り扱い

1. **一時ファイル**: 処理後すぐに削除
2. **保存データ**: テキストのみ（音声は保存しない）
3. **話者情報**: 匿名化（"SPEAKER_00"のみ、名前は保存しない）

### 同意取得

音声アップロード時に以下を表示：
```
⚠️ この音声ファイルには複数の話者が含まれている可能性があります。
   処理のため一時的に音声を分析しますが、音声データは保存されません。
   テキスト化されたデータのみが保存されます。

[ ] 同意する
```

---

## 🚀 実装ステップ

### Phase 1: 基本実装（2週間）

1. **Week 1**:
   - [ ] pyannote.audioのセットアップ
   - [ ] Whisper APIのタイムスタンプ対応
   - [ ] 話者識別の基本ロジック実装

2. **Week 2**:
   - [ ] 教授の声の自動判定ロジック
   - [ ] データベーススキーマ拡張
   - [ ] バックエンドAPI実装

### Phase 2: UI実装（1週間）

3. **Week 3**:
   - [ ] 話者選択UIの実装
   - [ ] プレビュー機能（音声再生）
   - [ ] エラーハンドリング

### Phase 3: 改善・最適化（1週間）

4. **Week 4**:
   - [ ] 処理速度の最適化
   - [ ] ユーザーテスト
   - [ ] ドキュメント整備

---

## 📝 使用方法（完成後）

### 基本的な流れ

1. **音声ファイルをアップロード**
   - 参照例管理画面 > ファイルから読み込む
   - .mp3, .wav, .m4a ファイルを選択

2. **話者識別オプションを有効化**
   - 「話者を識別して教授の発言のみを抽出」にチェック

3. **アップロード**
   - 自動的に話者を識別

4. **教授の声を選択（必要な場合）**
   - 複数の話者が検出された場合、選択画面が表示
   - サンプル音声を聞いて教授の声を選択

5. **保存**
   - 教授の発言のみがデータベースに保存される

---

## 🔧 技術的な課題と対策

### 課題1: pyannote.audioのモデルサイズ

**問題**: モデルが約1GB

**対策**:
- 初回起動時に自動ダウンロード
- キャッシュディレクトリに保存（再利用）
- Railwayのディスク容量を確認

### 課題2: 処理時間

**問題**: 長い音声では数分かかる

**対策**:
- バックグラウンド処理（非同期）
- 進捗表示UI
- 処理完了通知

### 課題3: Hugging Face Token

**問題**: pyannote.audioの使用にHugging Face Tokenが必要

**対策**:
- 環境変数で管理（`HUGGING_FACE_TOKEN`）
- セットアップガイドに記載

---

## 📚 参考資料

- [pyannote.audio公式ドキュメント](https://github.com/pyannote/pyannote-audio)
- [Whisper API - Timestamp](https://platform.openai.com/docs/guides/speech-to-text/timestamps)
- [Hugging Face - Speaker Diarization](https://huggingface.co/pyannote/speaker-diarization-3.1)

---

**承認**: 未承認
**ステータス**: 設計中
**次のアクション**: ユーザー承認後、実装開始
