# Phase 2 Week 7: PPT生成機能 要件定義書

**最終更新**: 2025-12-08
**バージョン**: 1.0
**対象**: PPT生成機能（Genspark用プロンプト生成システム）
**策定方法**: 壁打ちセッション

---

## 📋 改訂履歴

| バージョン | 日付 | 変更内容 | 作成者 |
|----------|------|---------|--------|
| 1.0 | 2025-12-08 | PPT生成機能要件定義書初版作成（壁打ちセッション結果反映） | Claude |

---

## 🎯 機能の目的

### システムの役割

**PPT生成支援システム**ではなく、**Genspark用プロンプト生成システム**として実装する。

```
【システムの役割】
入力：ユーザーのプロンプト（講演・講義の概要）
  ↓
処理：教授のナレッジベースから関連思考を検索・統合
  ↓
出力：Gensparkで使える完璧なプロンプト
  ↓
ユーザー：Gensparkにコピー&ペースト
  ↓
結果：美しいPPTファイル（Gensparkが生成）
```

### 核心的な価値提案

1. **教授らしさの自動反映**
   - ナレッジベースから教授の実際の言葉を検索
   - 教授のプロファイル（経歴、専門性、話し方）を統合
   - 「教授が作ったような」コンテンツを自動生成

2. **Gensparkの美しいデザインを活用**
   - 自前でPPT生成するより高品質
   - デザイン指示を詳細に記述してGensparkに渡す

3. **時間短縮**
   - 従来：2-3時間の手作業
   - 本システム：5-10分（編集含む）
   - **80%以上の時短効果**

---

## 🏗️ システム全体フロー

### 完全なユーザーフロー

```
┌─────────────────────────────────────┐
│ 0. 初回セットアップ（任意）           │
├─────────────────────────────────────┤
│ • 教授プロファイル設定               │
│   - 経歴・専門性                    │
│   - 話し方の特徴                    │
│   - よく使う表現                    │
│ • デザイン設定                      │
│   - 配色テーマ                      │
│   - レイアウトスタイル               │
│   - フォント                        │
│                                     │
│ ※デフォルト値で開始可能              │
│   後から変更・カスタマイズできる     │
└─────────────────────────────────────┘
              ↓
┌─────────────────────────────────────┐
│ 1. プロンプト入力                    │
├─────────────────────────────────────┤
│ ユーザー: 詳細なプロンプトを入力      │
│ 例：「夫人会で講演。40代女性、       │
│      個人事業主または起業志望者向け」 │
│                                     │
│ ヒント表示:                         │
│ • 対象者（年齢、職業、背景）         │
│ • イベント形式（講演、講義）         │
│ • 伝えたいメッセージ                │
│ • 時間配分                          │
└─────────────────────────────────────┘
              ↓
┌─────────────────────────────────────┐
│ 2. 詳細内容生成（60秒）              │
├─────────────────────────────────────┤
│ システム処理:                        │
│ ① LLM検索クエリ生成（5-10秒）       │
│    - gpt-4o-miniで3-5個のクエリ生成 │
│                                     │
│ ② ナレッジベース検索（2-3秒）        │
│    - 各クエリで上位7件検索          │
│    - 関連度0.7以上                  │
│    - 合計20件（重複排除）           │
│                                     │
│ ③ 詳細内容生成（40-60秒）           │
│    - gpt-4oで詳細なMarkdown生成     │
│    - 教授の言葉を各所に反映         │
│    - スライド構成案を作成           │
│                                     │
│ 進捗表示:                           │
│ ✅ 検索クエリ生成完了                │
│ ✅ ナレッジベース検索完了（20件）     │
│ 🔄 詳細内容を生成中... 70%          │
└─────────────────────────────────────┘
              ↓
┌─────────────────────────────────────┐
│ 3. 内容確認・編集（ユーザー操作）     │
├─────────────────────────────────────┤
│ 表示:                               │
│ • Markdown形式の詳細内容            │
│ • プレビュー表示（スライド形式）     │
│ • スライド枚数、推定時間            │
│                                     │
│ ユーザー操作:                        │
│ • 内容を確認                        │
│ • 必要に応じて編集                  │
│   - セクション追加・削除            │
│   - 表現の調整                      │
│   - 具体例の追加                    │
│ • プレビューで結果確認              │
│                                     │
│ オプション:                          │
│ • 下書き保存（後で再編集）          │
│ • デザイン設定の個別変更            │
└─────────────────────────────────────┘
              ↓
┌─────────────────────────────────────┐
│ 4. Gensparkプロンプト生成（10秒）    │
├─────────────────────────────────────┤
│ システム処理:                        │
│ ① 教授プロファイル取得（1秒）        │
│    - 経歴、専門性、話し方の特徴     │
│                                     │
│ ② デザイン仕様の追加（1秒）          │
│    - 配色、レイアウト、フォント     │
│    - 英語の詳細な指示文に変換       │
│                                     │
│ ③ 最終プロンプト組み立て（3-5秒）    │
│    - Speaker Profile               │
│    - Design Specifications         │
│    - Content Structure             │
│                                     │
│ 進捗表示:                           │
│ ✅ 教授プロファイル読み込み完了       │
│ ✅ デザイン仕様追加完了              │
│ 🔄 最終プロンプト整形中... 85%      │
└─────────────────────────────────────┘
              ↓
┌─────────────────────────────────────┐
│ 5. プロンプト表示・コピー            │
├─────────────────────────────────────┤
│ 表示:                               │
│ • 完成したGensparkプロンプト        │
│   (15,000-25,000文字)              │
│ • 文字数、スライド数の情報          │
│                                     │
│ ユーザー操作:                        │
│ • [📋 プロンプトをコピー] ボタン     │
│ • コピー完了の確認メッセージ        │
│                                     │
│ オプション:                          │
│ • プロンプトを保存（履歴に追加）     │
│ • 内容を編集し直す                  │
│                                     │
│ 次のステップ案内:                    │
│ 1. Gensparkにアクセス               │
│ 2. プロンプトをペースト              │
│ 3. 生成実行                         │
└─────────────────────────────────────┘
              ↓
┌─────────────────────────────────────┐
│ 6. Gensparkで実行（ユーザー操作）     │
├─────────────────────────────────────┤
│ ※システム外の操作                   │
│                                     │
│ ユーザー:                           │
│ 1. https://genspark.ai にアクセス   │
│ 2. プロンプトを貼り付け              │
│ 3. 生成実行                         │
│ 4. 生成されたPPTをダウンロード       │
│                                     │
│ Gensparkが生成:                     │
│ • 美しいデザインのPPTファイル        │
│ • 教授の思考を反映した内容          │
│ • すぐに使えるプロフェッショナルな資料│
└─────────────────────────────────────┘
```

---

## 📐 機能要件

### 1. 教授プロファイル管理

#### 1.1 基本情報

**入力項目**：
- 名前（任意）
- 肩書（任意）
- 詳細な経歴（自由記述、1000文字まで）
- 専門分野タグ（配列、例：["起業論", "戦略論", "M&A"]）

**初期設定**：
- デフォルト値で開始可能
- ナレッジベースから自動推測（Phase 3で実装）
- 後から変更・追加可能

#### 1.2 話し方の特徴

**選択式（複数選択可）**：
- □ 実例を多く使う
- □ 失敗談も包み隠さず語る
- □ 温かく背中を押すような語り口
- □ 顧客視点を重視
- □ 完璧より行動を重視

#### 1.3 よく使う表現・口癖

**入力方式**：
- テキストエリア（自由記述）
- 1行1フレーズ
- 例：
  ```
  顧客が何を求めているのかを深く理解する
  完璧な計画は必要ありません
  小さな一歩を踏み出す勇気
  事業は『人』がすべて
  ```

#### 1.4 デザイン設定

**配色テーマ**：
- ○ プロフェッショナル（ネイビー + グレー）
- ○ 温かい・親しみやすい（コーラル + ゴールド）
- ● カスタム
  - Primary Color: `#2C5F7C` 🎨
  - Secondary Color: `#FF6B6B` 🎨
  - Accent Color: `#F4A259` 🎨
  - Background: `#F8F9FA` 🎨

**デフォルト値**：
```json
{
  "color_theme": "professional_warm",
  "colors": {
    "primary": "#2C5F7C",
    "secondary": "#FF6B6B",
    "accent": "#F4A259",
    "background": "#F8F9FA"
  }
}
```

**レイアウトスタイル**：
- ● シンプル・余白重視
- ○ リッチ・ビジュアル重視
- ○ バランス型

**タイポグラフィ**：
- タイトルフォント: [ゴシック体 ▼]
- 本文フォント: [明朝体 ▼]

**全体の雰囲気（複数選択可）**：
- ☑ ビジネスライク
- ☑ 親しみやすい
- ☐ アカデミック
- ☑ 前向き・希望を与える

---

### 2. PPT内容生成

#### 2.1 プロンプト入力

**入力方式**：
- 自由記述（テキストエリア）
- 文字数制限：3,000文字

**入力ヒント**：
```
💡 プロンプト作成のヒント：
• 対象者：年齢、職業、背景、知識レベル
• イベント：講演、講義、セミナー、ワークショップ
• テーマ：伝えたい核心メッセージ
• 時間配分：導入・本論・まとめの時間
• 特記事項：避けたいトピック、必ず含めたい要素
```

**入力例**：
```
夫人会で講演することになりました。40代の女性の集まりで、
個人事業主、またはこれから仕事を始めたいと考えている方々です。
私は海外での事業経験が長く、新規事業立ち上げ、M&Aの経験を
多くしてきました。パナソニックに34年間務め、取締役まで務めました。
そんな私から彼女たちにどのような講演をすれば良いか、
その講演内容の要旨を書いてください。
```

#### 2.2 検索クエリ生成

**処理**：
```python
# gpt-4o-mini で検索クエリ生成
queries = generate_search_queries(user_prompt)
# 例：
# [
#   "起業における顧客視点の重要性",
#   "女性の強みを活かした事業戦略",
#   "40代からのキャリア再構築"
# ]
```

**パラメータ**：
- モデル: `gpt-4o-mini`
- 生成クエリ数: 3-5個
- Temperature: 0.3（安定性重視）
- 処理時間目標: 5-10秒

#### 2.3 ナレッジベース検索

**検索方式**：
```python
# 各クエリでベクトル検索
for query in queries:
    embedding = get_embedding(query)
    results = search_knowledge_base(
        embedding=embedding,
        user_id=user_id,
        limit=7,
        min_similarity=0.7
    )
```

**検索パラメータ**：
- 各クエリあたり: 上位7件
- 最低関連度: 0.7（コサイン類似度）
- 最終結果: 20件（重複排除後）
- 検索対象: 全カテゴリ（reflection, final, other）

**フォールバック**：
```python
if len(results) < 5:
    # 閾値を下げて再検索
    results = search_knowledge_base(min_similarity=0.5)
    warning = "関連するナレッジが少ないため、一般的な内容が含まれます"

if len(results) == 0:
    # 空でも続行（警告付き）
    warning = "このトピックは教授のナレッジベースにありません"
```

#### 2.4 詳細内容生成

**処理**：
```python
# gpt-4o で詳細なMarkdown生成
content = generate_detailed_content(
    user_prompt=user_prompt,
    knowledge_base=search_results,
    professor_profile=profile
)
```

**プロンプト構成**：
```
【システムプロンプト】
あなたは経験豊富な教授です。以下のプロファイルに基づいて、
講演・講義の詳細な内容を生成してください。

【教授プロファイル】
- 経歴: パナソニックに34年間勤務、取締役まで務める
- 専門: 起業論、戦略論、M&A、海外事業
- 話し方: 温かく背中を押すような語り口、実例を多用

【教授の関連知識】（ナレッジベースから抽出）
1. 「顧客が何を求めているのかを深く理解することが...」
2. 「競争優位の本質は、模倣困難性にあります...」
...

【ユーザーのプロンプト】
夫人会で講演。40代女性、個人事業主...

【出力形式】
Markdown形式で以下を生成：
# PPTタイトル
## 副題

---

## スライド1: [タイトル]
### 内容
- 箇条書き

### 教授の視点
[教授の言葉を引用]

**デザイン指示**: [レイアウトの指示]

---
（以降、全スライド）
```

**パラメータ**：
- モデル: `gpt-4o`
- Temperature: 0.7（創造性と安定性のバランス）
- max_tokens: 計算式 `min(len(prompt) * 3.5, 15000)`
- 処理時間目標: 40-60秒

**出力例**：
```markdown
# 私らしく働く力

## 副題: 40代から始める事業のつくり方

---

## スライド1: オープニング

### タイトル
私らしく働く力

### 内容
- 経験ゼロでも、人生の後半からでも
- 事業は始められる

### 教授の視点
事業を始めるのに、完璧な準備は必要ありません。
大切なのは「誰かの課題を解決したい」という想いと、
小さな一歩を踏み出す勇気です。

**デザイン指示**: センター揃え、大きな文字

---

## スライド2: 自己紹介
...
```

---

### 3. 内容編集機能

#### 3.1 Markdown編集

**編集エリア**：
- テキストエリア（モノスペースフォント）
- シンタックスハイライト（任意、Phase 3）
- 自動保存（30秒ごと、ローカルストレージ）

**編集支援**：
```
文字数: 3,245 / 30,000
スライド数: 17枚

💡 編集のヒント:
・「---」でスライドを区切ります
・「##」がスライドタイトルになります
・箇条書きは「-」または「•」を使います
```

#### 3.2 プレビュー機能

**表示方式**：
- タブ切り替え: [✏️ 編集] [👁️ プレビュー]
- リアルタイムパース（Markdown → HTML）
- スライド形式で表示

**プレビュー画面**：
```
┌─────────────────────────────────────┐
│ スライド 1 / 17          [< >]      │
├─────────────────────────────────────┤
│                                     │
│        私らしく働く力                │
│                                     │
│   経験ゼロでも、人生の後半からでも   │
│   事業は始められる                  │
│                                     │
└─────────────────────────────────────┘

[◀ 前へ] [次へ ▶] [編集モードに戻る]
```

**機能**：
- スライド間移動（矢印キー対応）
- 全スライド一覧表示
- スライドのスキップ

#### 3.3 バリデーション

**自動チェック**：
```python
def validate_markdown(content):
    issues = []

    # 1. スライド区切りチェック
    slides = content.split('---')
    if len(slides) < 2:
        issues.append("⚠️ スライドの区切り（---）が見つかりません")

    # 2. 空スライドチェック
    for i, slide in enumerate(slides):
        if len(slide.strip()) < 10:
            issues.append(f"⚠️ スライド{i+1}が空または短すぎます")

    # 3. タイトルチェック
    if not content.startswith('#'):
        issues.append("⚠️ PPTタイトルが見つかりません")

    return issues
```

**警告表示**：
```
⚠️ 以下の問題が見つかりました:
• スライド3が空または短すぎます
• スライド7の区切りが不明確です

自動修正を試みました。
問題なければそのまま続行できます。

[内容を確認] [そのまま続行]
```

---

### 4. Gensparkプロンプト生成

#### 4.1 プロンプト構成

**生成されるプロンプトの構造**：

```markdown
# Presentation Generation Request

## Speaker Profile

### Background
- 34 years at Panasonic, served as Executive Director
- Extensive experience in overseas business development and M&A
- Known for emphasizing customer-centric thinking and practical entrepreneurship

### Expertise
- Entrepreneurship and Business Strategy
- M&A and Organizational Management
- Global Business Development

### Speaking Style
- Warm and encouraging tone that motivates audience
- Uses real-world examples extensively
- Shares both successes and failures openly
- Emphasizes customer perspective
- Values action over perfection

### Characteristic Phrases
- "Understanding what customers truly need is the foundation of all business"
- "You don't need a perfect plan to start"
- "The courage to take that first small step"
- "Business is ultimately about people"

---

## Design Specifications

### Visual Style
Professional yet warm and approachable, suitable for lectures
and presentations to diverse audiences.

### Color Palette
- **Primary Color**: Navy Blue (#2C5F7C)
  - Conveys trust and intelligence
- **Secondary Color**: Coral Pink (#FF6B6B)
  - Adds warmth and femininity for diverse audiences
- **Accent Color**: Gold (#F4A259)
  - Represents possibility and hope
- **Background**: Off-white (#F8F9FA)
  - Clean and easy on the eyes

### Typography
- **Headings**: Gothic/Sans-serif, Bold
  - Font size: 44pt for main titles, 32pt for section headers
- **Body Text**: Mincho/Serif
  - Font size: 18-20pt for readability

### Layout Guidelines
- **Whitespace**: Generous margins and padding
- **Alignment**: Left-aligned for body text
- **Visual Elements**: Icons and emojis moderately, focus on text
- **Bullet Points**: Maximum 3-5 per slide

### Slide Structure
- **Title Slides**: Center-aligned, large text, minimal
- **Content Slides**: Title at top, 3-5 bullets
- **Quote Slides**: Large text, professor's insights highlighted

### Overall Atmosphere
Professional but not cold, approachable and encouraging,
forward-looking and hopeful.

---

## Content Structure

### Slide 1: Title Slide
**Title**: 私らしく働く力

**Subtitle**: 40代から始める事業のつくり方

**Footer**: 夫人会講演 | 2025年12月8日

**Design Notes**:
- Center-aligned
- Large, bold typography
- Use primary and secondary colors for visual impact

---

### Slide 2: Self Introduction

**Title**: 自己紹介

**Content**:
- パナソニックに34年間勤務、取締役まで務める
- 海外事業の立ち上げ・運営の豊富な経験
- M&A（企業買収・合併）を多数リード
- 新規事業の立ち上げを複数経験

**Professor's Message**:
"事業を始めるのに、完璧な準備は必要ありません。
大切なのは「誰かの課題を解決したい」という想いと、
小さな一歩を踏み出す勇気です。"

**Design Notes**:
- Left-aligned content
- Professor's message in a highlighted box
- Professional yet approachable layout

---

（以降、全17スライドの詳細内容）

---

## Additional Instructions

### Tone and Voice
- Maintain a warm, encouraging, and professional tone throughout
- Use concrete examples wherever possible
- Balance theory with practical advice
- Address the audience directly ("あなた")

### Content Adaptation
- Ensure all content is appropriate for the target audience
  (40-something women, aspiring entrepreneurs)
- Avoid overly technical jargon
- Focus on actionable insights

### Visual Consistency
- Maintain consistent color scheme across all slides
- Use icons and visual elements sparingly but effectively
- Ensure text is large enough for easy reading

---

**End of Prompt**
Total Slides: 17
Estimated Duration: 60 minutes
```

#### 4.2 生成パラメータ

**処理時間**：
- 教授プロファイル取得: 1秒
- デザイン指示文の英訳: 2-3秒
- 最終プロンプト組み立て: 3-5秒
- **合計**: 10秒以内

**文字数制限**：
- 推奨: 15,000-20,000文字
- 最大: 25,000文字
- 超過時: 警告表示 + 対処法提示

**バリデーション**：
```python
def validate_genspark_prompt(prompt):
    length = len(prompt)

    if length > 25000:
        return False, "プロンプトが長すぎます（25,000文字超）"

    if length < 1000:
        return False, "プロンプトが短すぎます"

    # 必須セクションのチェック
    required_sections = [
        "# Presentation Generation Request",
        "## Speaker Profile",
        "## Design Specifications",
        "## Content Structure"
    ]

    for section in required_sections:
        if section not in prompt:
            return False, f"必須セクション '{section}' が見つかりません"

    return True, None
```

---

### 5. 生成履歴管理

#### 5.1 履歴保存

**保存内容**：
- 元のプロンプト（ユーザー入力）
- 生成されたMarkdown内容
- 編集後のMarkdown内容
- 最終的なGensparkプロンプト
- メタデータ（スライド数、推定時間）

**保存タイミング**：
- Gensparkプロンプト生成完了時
- 自動保存（明示的な保存ボタンは任意）

**保持期間**：
- **90日間**
- 90日経過後に自動削除
- 削除30日前に通知（Phase 3）

#### 5.2 履歴一覧（Week 7実装）

**最低限の機能**：
```
┌─────────────────────────────────────┐
│ PPT生成履歴                          │
├─────────────────────────────────────┤
│ [+ 新規作成]                         │
├─────────────────────────────────────┤
│ 📊 2025-12-08                       │
│ 夫人会講演「私らしく働く力」          │
│ 17枚 | [表示] [削除]                │
│                                     │
│ 📊 2025-12-05                       │
│ MBA講義「競争戦略の基礎」            │
│ 12枚 | [表示] [削除]                │
│                                     │
│ ※ 生成から90日後に自動削除されます    │
└─────────────────────────────────────┘
```

**機能**：
- 一覧表示（作成日降順）
- 詳細表示（プロンプト全文表示）
- プロンプトコピー
- 削除
- ページネーション（20件/ページ）

**Phase 3で追加予定**：
- 検索機能
- フィルタ（日付範囲、キーワード）
- 再編集機能
- 複製機能
- タイトル編集

---

## 🎯 非機能要件

### 1. パフォーマンス要件

| 処理 | 目標時間 | 許容時間 | タイムアウト |
|------|---------|---------|-------------|
| 検索クエリ生成 | 5-10秒 | 15秒 | 30秒 |
| ナレッジベース検索 | 2-3秒 | 5秒 | 10秒 |
| 詳細内容生成 | 40-60秒 | 90秒 | 120秒 |
| Gensparkプロンプト生成 | 5-10秒 | 15秒 | 30秒 |
| **合計（システム処理）** | **60-80秒** | **120秒** | **180秒** |

**進捗表示**：
- 詳細な進捗バー（必須）
- 各ステップの完了状態表示
- 残り時間の推定表示

---

### 2. 可用性・信頼性

**エラーハンドリング**：

| エラー | 対処法 | 優先度 |
|--------|--------|--------|
| ナレッジベース検索0件 | 警告 + 閾値を下げて再検索 | 中 |
| LLMタイムアウト | リトライ3回 → gpt-4o-mini フォールバック | 高 |
| Markdown不正 | 自動修正 + 警告表示 | 中 |
| プロンプト過長 | 警告 + 短縮方法提示 | 低 |

**リトライポリシー**：
```python
RETRY_CONFIG = {
    "max_retries": 3,
    "backoff_factor": 2,  # 指数バックオフ
    "retry_on": [
        "TimeoutError",
        "APIConnectionError",
        "RateLimitError"
    ]
}
```

---

### 3. セキュリティ

**アクセス制御**：
- 教授プロファイル：ユーザー自身のみアクセス可能
- 生成履歴：ユーザー自身のみアクセス可能
- ナレッジベース：ユーザー自身のものだけ検索

**データ保護**：
- 生成内容のログ保存（デバッグ用、30日後削除）
- OpenAI APIへの送信データ（規約に準拠）
- Gensparkへの送信はユーザーが手動実行（システムは関与しない）

---

### 4. コスト要件

**月間想定コスト（月4回使用）**：

| 項目 | 1回あたり | 月間 |
|------|----------|------|
| 検索クエリ生成（gpt-4o-mini） | ¥0.02 | ¥0.08 |
| Embedding生成 | ¥0.0002 | ¥0.001 |
| 詳細内容生成（gpt-4o） | ¥5.5 | ¥22 |
| **合計** | **¥5.52** | **¥22** |

**年間コスト**: ¥264

**コスト管理**：
- 上限設定は不要
- 月次レポート（Phase 3）
- 使用量モニタリング（Phase 3）

---

### 5. 拡張性

**Phase 3での拡張予定**：
- 複数のAI PPTサービス対応（Gamma.app、Tome）
- 過去PPTからのスタイル学習
- 多言語対応（英語プロンプト生成）
- チームでの共有機能
- テンプレート機能

**設計での考慮**：
- プロンプト生成ロジックを抽象化
- デザイン設定のJSON化（柔軟な拡張）
- ナレッジベース検索の汎用化

---

## ✅ 成功基準

### Must Have（必須）

**Phase 2 Week 7 完了の条件**：

1. ✅ **機能が動作する**
   - [ ] プロンプト入力からGensparkプロンプト出力まで完了
   - [ ] エラーなく処理が完了する
   - [ ] 進捗表示が正しく動作する

2. ✅ **教授の思考が反映される**
   - [ ] ナレッジベース検索が機能する
   - [ ] 生成内容に教授の言葉が含まれる
   - [ ] 教授プロファイルの情報が反映される

3. ✅ **Gensparkで使える**
   - [ ] 出力プロンプトをGensparkに貼り付けて実行できる
   - [ ] Gensparkが正常にPPTを生成する
   - [ ] 生成されたPPTが開ける

4. ✅ **パフォーマンス基準を満たす**
   - [ ] 詳細内容生成が90秒以内
   - [ ] Gensparkプロンプト生成が15秒以内
   - [ ] タイムアウトエラーが発生しない

---

### Should Have（期待）

5. ✅ **教授プロファイルが機能する**
   - [ ] デフォルト設定で利用開始できる
   - [ ] プロファイル編集が可能
   - [ ] デザイン設定が反映される

6. ✅ **履歴管理が機能する**
   - [ ] 生成履歴が保存される
   - [ ] 過去のプロンプトを表示・コピーできる
   - [ ] 90日後に自動削除される

7. ✅ **編集機能が使いやすい**
   - [ ] Markdown編集がスムーズ
   - [ ] プレビュー表示が見やすい
   - [ ] バリデーションが適切に動作

---

### Nice to Have（理想）

8. ⭐ **生成されたPPTの品質が高い**
   - [ ] そのまま、または最小限の修正で使える
   - [ ] デザインが美しい
   - [ ] 内容が的確で教授らしい

9. ⭐ **教授が継続的に使いたいと思う**
   - [ ] 月4回以上の利用
   - [ ] 満足度4.0/5.0以上

10. ⭐ **時間短縮効果が明確**
    - [ ] 従来2-3時間 → 10-15分（編集含む）
    - [ ] 80%以上の時短効果

---

## 📊 評価・テスト計画

### Week 8 テスト内容

**1. 機能テスト**：
- [ ] 3つの異なるプロンプトで生成テスト
- [ ] エラーハンドリングの動作確認
- [ ] 履歴管理の動作確認

**2. 品質テスト**：
- [ ] 生成された内容に教授の言葉が含まれているか
- [ ] Gensparkでエラーなく実行できるか
- [ ] 生成されたPPTのスライド構成が適切か

**3. パフォーマンステスト**：
- [ ] 処理時間の計測（5回平均）
- [ ] タイムアウトが発生しないか
- [ ] 進捗表示が正確か

**4. ユーザーテスト（教授）**：
- [ ] 実際に1つのプロンプトで生成
- [ ] Gensparkで実行してPPT作成
- [ ] 満足度アンケート（1-5点）
- [ ] 改善点のヒアリング

---

## 🚀 実装優先順位

### Week 7 実装範囲

**最優先（P0）**：
1. プロンプト入力画面
2. 詳細内容生成（LLM統合）
3. Markdown編集画面
4. Gensparkプロンプト生成
5. 基本的なエラーハンドリング

**高優先（P1）**：
6. 教授プロファイル設定（デフォルト値）
7. デザイン設定（デフォルト値）
8. プレビュー機能
9. 進捗表示
10. 履歴保存

**中優先（P2）**：
11. 履歴一覧画面
12. バリデーション
13. 詳細な進捗表示
14. 自動保存

**低優先（P3、Phase 3へ）**：
15. プロファイル詳細編集
16. 履歴検索・フィルタ
17. 再編集機能
18. カスタムデザイン編集

---

## 📝 制約事項・前提条件

### 前提条件

1. **Phase 1-2 Week 6 までの機能が完成している**
   - ナレッジベース管理機能
   - Embedding + pgvector 検索
   - 教授プロファイルの基本項目

2. **Gensparkへのアクセス**
   - ユーザー（教授）がGensparkアカウントを持っている
   - Gensparkの利用方法を理解している

3. **開発環境**
   - OpenAI API キー
   - Supabase データベース
   - Next.js + FastAPI 環境

### 制約事項

1. **Gensparkとの直接統合はしない**
   - プロンプト生成まで
   - Gensparkへの送信はユーザーが手動

2. **Week 7 の実装範囲**
   - 最低限の機能のみ
   - 詳細なカスタマイズはPhase 3

3. **デザインの完全再現は不可**
   - Gensparkの解釈に依存
   - プロンプトでの指示のみ

---

## 🔗 関連ドキュメント

- `requirements_phase2.md`: Phase 2 全体要件定義
- `specifications_ppt_generation_functional.md`: 機能仕様書
- `specifications_ppt_generation_technical.md`: 技術仕様書
- `implementation_plan_week7_ppt_generation.md`: Week 7 実装計画

---

**策定日**: 2025-12-08
**策定者**: Claude
**承認**: 榎戸教授（予定）
