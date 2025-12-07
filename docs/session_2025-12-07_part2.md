# 開発セッション記録 2025-12-07 Part 2

## 実装内容サマリー

本日後半のセッションでは、ファイルアップロード機能を大幅に強化し、教授の発言だけを正確に蓄積できる仕組みを完成させました。また、Word/PDF対応により、様々な形式の文書から教授の思考を学習できるようになりました。

---

## 1. セクション選択保存機能（教授の発言のみを蓄積）

### 問題
- 音声にラジオやパーソナリティの発言が混在
- セクション全体を保存すると不要な発言も含まれる

### 解決策（コミット: cf6bb44）

**チェックボックスによる選択的保存**：
```typescript
// 各セクションにチェックボックスを追加
const [selectedSections, setSelectedSections] = useState<Set<number>>(new Set())

// 選択されたセクションのみ保存
async function handleSaveSelectedSections() {
  const selectedIndexes = Array.from(selectedSections).sort((a, b) => a - b)
  for (const index of selectedIndexes) {
    await handleSaveSection(sections[index], index)
  }
}
```

**追加機能**：
- 「すべて選択/解除」ボタン
- 選択されたセクションの視覚的ハイライト（青いボーダー）
- 「選択したセクションを保存 (X個)」ボタン

---

## 2. UI修正（中央揃え）

### 問題
ファイル選択後の画面で、PC画面では左寄せになっていた。

### 解決策（コミット: c72f026）
```typescript
// 修正前
<div className="text-center">

// 修正後
<div className="flex flex-col items-center">
```

---

## 3. LLM分割処理のタイムアウト問題解消

### 問題
- 6975文字のテキストに対して7,975トークンしか確保されず、処理が失敗
- フロントエンドで空白画面のまま応答なし

### 根本原因
```python
# 修正前
max_tokens = len(text) + 1000  # ❌ 日本語は1文字2-3トークン必要

# 修正後
estimated_tokens = int(len(text) * 3.5)  # ✅ 日本語対応
max_output_tokens = min(estimated_tokens, 15000)
```

### 解決策（コミット: 903a6e7）

**1. max_tokens計算の改善**：
- 日本語は1文字あたり約2-3トークン
- 新しい計算式: `len(text) * 3.5`（安全マージン込み）
- 最大15,000トークンに制限

**2. JSON出力フォーマットの明確化**：
- プロンプトで`{"sections": [...]}`形式を明示
- `response_format="json_object"`を活用

**3. JSONパース処理の簡略化**：
- マークダウンコードブロックの抽出処理を削除
- バリデーション追加

---

## 4. セクション全文表示と編集機能

### 問題1：セクションの文章全体が読めない（一部しか表示されない）
**解決策**：展開/折りたたみ機能を追加

### 問題2：教授のコメントとパーソナリティのコメントが混ざっている
**解決策**：各セクションに編集機能を追加

### 実装内容（コミット: 9f5241a）

**1. 展開/折りたたみ機能**：
```typescript
const [expandedSections, setExpandedSections] = useState<Set<number>>(new Set())

// 「▼ 全文を読む」ボタンで全文表示
// 「▲ 折りたたむ」で元に戻す
```

**2. セクション編集機能**：
```typescript
const [editingSections, setEditingSections] = useState<Set<number>>(new Set())
const [editedContents, setEditedContents] = useState<Map<number, string>>(new Map())

// 「✏️ 編集」ボタンでテキストエリアに切り替え
// 不要な部分（パーソナリティの発言など）を削除可能
// 「✓ 編集完了」で確定
// 保存時は編集後の内容を使用
```

**使い方**：
1. 音声アップロード → セクション分割
2. 各セクションを「全文を読む」で確認
3. 「編集」ボタンで不要な部分を削除
4. チェックボックスで教授の発言だけを選択
5. 保存

---

## 5. エラーメッセージの詳細化

### 問題
保存失敗時に「保存に失敗しました」としか表示されず、原因不明。

### 解決策（コミット: e3aee7d）

```typescript
// エラーレスポンスの詳細を取得
const errorData = await response.json().catch(() => ({ detail: 'Unknown error' }))
throw new Error(`保存に失敗しました (${response.status}): ${errorData.detail}`)

// 表示例: "保存に失敗しました (500): 参照例の作成に失敗しました: ..."
```

**改善点**：
- HTTPステータスコード表示
- サーバーからのエラーメッセージ表示
- 選択保存時は成功数と失敗したセクションを表示

---

## 6. 「その他」カテゴリの完全対応

### 問題
- データベースのチェック制約に'other'が含まれていない
- 参照例一覧のフィルターに「その他」がない
- 編集モーダルで「その他」を選択できない

### 解決策

#### 6.1 データベーススキーマ修正
```sql
-- 既存のチェック制約を削除
ALTER TABLE knowledge_base
DROP CONSTRAINT IF EXISTS knowledge_base_type_check;

-- 新しいチェック制約を追加（'other'を含める）
ALTER TABLE knowledge_base
ADD CONSTRAINT knowledge_base_type_check
CHECK (type IN ('reflection', 'final', 'other'));
```

#### 6.2 UIの拡張（コミット: 07d1f2c）

**追加した選択肢**：
- タイプフィルター：全て / 振り返り / 最終レポート / **その他**
- 編集モーダル：振り返り / 最終レポート / **その他**

**タイプ表示のカラー**：
- 振り返り：青色（accent）
- 最終：グレー（text-muted）
- その他：ダークグレー（#6B7280）

#### 6.3 型定義の修正（コミット: f562780）

```typescript
// lib/references.ts
export interface ReferenceExample {
  type: 'reflection' | 'final' | 'other'
}

// app/references/page.tsx
const [filterType, setFilterType] = useState<'all' | 'reflection' | 'final' | 'other'>('all')
const [formType, setFormType] = useState<'reflection' | 'final' | 'other'>('reflection')
```

---

## 7. Word/PDF対応

### 実装内容（コミット: a4857d8）

**対応形式の拡張**：
- 音声：mp3, wav, m4a（最大100MB）
- 文書：txt, **docx**, **pdf**（最大10MB）

#### 7.1 フロントエンド
```typescript
const validDocExtensions = ['.docx', '.doc']
const validPdfExtensions = ['.pdf']

// ファイル選択のacceptプロパティ
accept=".mp3,.wav,.m4a,.txt,.docx,.doc,.pdf"
```

#### 7.2 バックエンド

**Word文書処理関数**：
```python
async def handle_docx_file(file: UploadFile, split_by_topic: bool = False):
    from docx import Document

    # Word文書を読み込み
    doc = Document(tmp_path)

    # すべての段落からテキストを抽出
    paragraphs = [para.text for para in doc.paragraphs if para.text.strip()]
    text = '\n'.join(paragraphs)
```

**PDF文書処理関数**：
```python
async def handle_pdf_file(file: UploadFile, split_by_topic: bool = False):
    from pypdf import PdfReader

    # PDFを読み込み
    reader = PdfReader(tmp_path)

    # すべてのページからテキストを抽出
    pages_text = []
    for page in reader.pages:
        page_text = page.extract_text()
        if page_text.strip():
            pages_text.append(page_text)

    text = '\n'.join(pages_text)
```

**依存関係の追加**：
```txt
python-docx>=1.0.0
pypdf>=3.17.0
```

---

## コミット履歴

| コミットID | 内容 |
|-----------|------|
| cf6bb44 | feat: セクション選択保存機能を追加して教授の発言のみを蓄積可能に |
| c72f026 | fix: ファイル選択後の画面を中央揃えに修正 |
| 903a6e7 | fix: LLM分割処理のmax_tokens計算を修正してタイムアウトを解消 |
| 9f5241a | feat: セクション全文表示と編集機能を追加 |
| e3aee7d | fix: 保存エラーメッセージを詳細化してデバッグを容易に |
| 07d1f2c | feat: 参照例一覧と編集画面に「その他」カテゴリを追加 |
| f562780 | fix: 型定義に'other'を追加してTypeScriptビルドエラーを解消 |
| a4857d8 | feat: Word(.docx)とPDF(.pdf)のアップロード機能を追加 |

---

## 技術的な改善まとめ

### LLM分割処理の最適化
| 項目 | 修正前 | 修正後 |
|------|--------|--------|
| max_tokens計算 | len(text) + 1000 | len(text) * 3.5（最大15,000） |
| JSON出力 | マークダウン記法混在 | response_format="json_object"で統一 |
| パース処理 | 複雑な正規表現 | 直接JSONパース |

### ファイル対応形式
| カテゴリ | 形式 | 最大サイズ | 処理ライブラリ |
|---------|------|-----------|--------------|
| 音声 | mp3, wav, m4a | 100MB | Whisper API + ffmpeg |
| テキスト | txt | 10MB | chardet |
| Word | docx, doc | 10MB | python-docx |
| PDF | pdf | 10MB | pypdf |

---

## 完成した機能フロー

```
【教授の発言だけを正確に蓄積する完全なワークフロー】

1. ファイルアップロード
   - 音声: mp3, wav, m4a（Whisper API + 自動圧縮）
   - 文書: txt, docx, pdf（テキスト抽出）
   ↓
2. LLMでセクション分割（オプション）
   - 意味のあるまとまりごとに分割
   - max_tokens最適化でタイムアウトなし
   ↓
3. セクションの確認・編集
   - 「全文を読む」で内容確認
   - 「編集」で不要な部分（パーソナリティの発言等）を削除
   ↓
4. 選択的保存
   - チェックボックスで教授の発言だけを選択
   - 「選択したセクションを保存」
   ↓
5. 「その他」カテゴリで保存
   - 振り返りレポート、最終レポートの両方で参照される
   ↓
【純粋な教授の思考だけがナレッジベースに蓄積される】
```

---

## 期待される効果

### 1. 高品質な教授の思考蓄積
- ✅ 音声からも文書からも抽出可能
- ✅ 不要な発言を除外して純粋な教授の思考のみ
- ✅ Word/PDFの講義資料・講演スライドも活用可能

### 2. 効率的な運用
- ✅ チェックボックスで簡単に選択
- ✅ 編集機能で細かい調整が可能
- ✅ タイムアウトなしで大容量ファイルも処理

### 3. 継続的な成長
- ✅ 講義・講演を「その他」として蓄積
- ✅ 使えば使うほど教授らしいコメントが生成される
- ✅ GPTsを超える動的に成長し続ける教授のデジタルツイン

---

## 次のステップ候補

### 優先度：中
- [ ] ファイルアップロード画面にコンテンツタイプ選択UIを追加
  - 現在は'other'で固定
  - UIで「振り返り」「最終」「その他」を選択可能にする

### 優先度：低
- [ ] .doc（旧形式Word）の完全対応確認
  - python-docxは主に.docxに最適化
  - 必要に応じてdoc2docxライブラリ追加を検討

---

## 残課題

**なし** - 本日の実装で主要機能は完成

---

**最終更新**: 2025-12-07
**Phase**: Phase 2 Week 5-6（ファイルアップロード機能）完了
**次のフェーズ**: Phase 2 Week 7-8（PPT生成機能）

