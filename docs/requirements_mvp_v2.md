# 教授コメント自動化ボット MVP 要件定義書 v2.0

**最終更新**: 2025-11-11
**バージョン**: 2.0（壁打ちセッション反映版）
**対象フェーズ**: Phase 1 MVP

---

## 📋 改訂履歴

| バージョン | 日付 | 変更内容 | 作成者 |
|----------|------|---------|--------|
| 1.0 | 2025-10-XX | 初版作成 | - |
| 2.0 | 2025-11-11 | 壁打ちセッション結果反映、Next.js採用、Phase構成変更、要件調整 | Claude |

## 🎯 プロジェクト概要

### 目的

経営戦略論の教授が学生レポート（reflection/final）に対して温かく示唆に富んだコメントを作成する作業を、AI（GPT-4o-mini）を活用して効率化するシステムを構築する。

### 背景

- 教授は週5本 × 20週 = 年間100本のレポートコメントを作成
- 1本あたり5〜10分の作業時間が必要
- 過去の自身のコメント例（50件）を参照しながら一貫性を保つ必要がある
- 温かみと示唆性のバランスが重要

### スコープ（Phase 1 MVP）

**Phase 1 に含むもの**:
- ✅ reflection レポート対応（週次レポート）
- ✅ final レポート対応（最終レポート） ← **Phase 1で実装**
- ✅ Rubric 自動採点（5項目、1-5点）+ 理由生成
- ✅ 要約生成（学生の主張を100文字程度で要約）
- ✅ 教授コメント生成（過去コメント例を参照しつつ、300-400文字程度）
- ✅ RAG（Jaccard類似度ベース、簡易版）
- ✅ Google OAuth認証
- ✅ Supabaseデータベース連携（履歴保存・取得・削除）
- ✅ PII検出・マスキング（正規表現ベース、簡易版）
- ✅ 手直し時間測定 + 満足度アンケート（簡易版）
- ✅ 基本統計表示（メトリクス数値のみ、グラフなし）
- ✅ エクスポート機能（JSON/CSV）

**Phase 1 に含まないもの（Phase 2以降へ延期）**:
- ❌ 音声入力・音声出力
- ❌ PPTX/PDF資料アップロード対応
- ❌ 高度なRAG（Embedding + pgvector）
- ❌ 高度なダッシュボード（グラフ・可視化）
- ❌ オンボーディングチュートリアル
- ❌ RBAC（ロールベースアクセス制御）
- ❌ 本格的な監視基盤（Prometheus/Grafana）
- ❌ 正式なSLO/SLA定義

---

## 🏗️ Phase構成（改訂版）

### Phase 1: MVP開発（本要件定義書の対象）
**期間**: 13-15週間（Week 0を含む）
**目標**: 教授単独利用可能な基本システム完成

- Week 0: 準備週間（5日間）
- Week 1-2: 環境セットアップ + Google OAuth認証
- Week 3-4: メイン画面 + UI実装
- Week 5-6: バックエンド強化 + PII検出 + final対応
- Week 7-9: Supabaseデータベース連携
- Week 10-11: 品質評価機能 + 既存機能完成
- Week 12: 検証・改善（UAT実施）
- Week 13-14: 最終調整・ドキュメント・デプロイ準備

### Phase 2-A: データ基盤強化（4-5週間）
**目標**: データ蓄積活用 + RAG強化

- Embedding + pgvector による高度なRAG実装
- ナレッジベース管理機能
- RBAC（複数ユーザー対応準備）
- 本格的な監視基盤構築
- 正式なSLO/SLA定義

### Phase 2-B: マルチモーダル対応（3-4週間）
**目標**: 音声・資料対応

- 音声入力（Whisper API）
- 音声出力（TTS API）
- PPTX/PDF資料アップロード対応
- OCR + Vision API連携

### Phase 3: リアルタイムチャットボット（6-8週間）
**目標**: 学生向けチャット機能

- リアルタイムチャット機能（Next.js + WebSocket）
- Supabase Realtime活用
- 教授コメントアーカイブの活用
- コスト管理強化（学生利用のため）

---

## 🎨 技術スタック（Phase 1）

### フロントエンド
- **フレームワーク**: Next.js 14 (App Router)
- **言語**: TypeScript
- **スタイリング**: TailwindCSS
- **デザインシステム**: Academic Minimal UI（Streamlitから移植）
- **状態管理**: React Hooks (useState, useContext)
- **認証**: Supabase Auth（Google OAuth）
- **デプロイ**: Vercel

**変更理由**:
- Phase 3でリアルタイムチャット機能が必要なため、Streamlitでは技術的に困難
- Next.jsならば段階的な機能拡張が容易
- TypeScriptで型安全性を確保

### バックエンド
- **フレームワーク**: FastAPI
- **言語**: Python 3.11+
- **処理方式**: 同期処理（Phase 1は単一ユーザーのため非同期化不要）
- **LLM**: OpenAI API (gpt-4o-mini)
- **RAG**: Jaccard類似度（簡易版）
- **PII検出**: 正規表現ベース（簡易版）

### データベース・認証
- **データベース**: Supabase (PostgreSQL)
- **認証**: Supabase Auth（Google OAuth）
- **セキュリティ**: Row Level Security (RLS)
- **暗号化**: レポート本文を暗号化して保存

### 開発・運用
- **バージョン管理**: Git
- **ログ記録**: Pythonロギング（基本レベル）
- **エラー監視**: ベストエフォート（Phase 2-Aで本格化）
- **コスト管理**: 月次の手動確認（OpenAIダッシュボード）

---

## 📐 システムアーキテクチャ

### 構成図（概要）

```
[ブラウザ]
   ↓ HTTPS
[Next.js Frontend]
   ↓ REST API (HTTPS)
[FastAPI Backend]
   ↓ gpt-4o-mini
[OpenAI API]

[Next.js Frontend]
   ↓ Google OAuth
[Supabase Auth]
   ↓ RLS
[Supabase PostgreSQL]
```

### 認証フロー

1. ユーザーが「Googleでログイン」ボタンをクリック
2. Supabase Auth が Google OAuth フローを開始
3. Googleの同意画面でユーザーが許可
4. Supabase Auth がセッションを確立（JWT発行）
5. Next.jsフロントエンドがJWTを保持
6. FastAPI バックエンドへのリクエスト時に Authorization ヘッダーでJWTを送信
7. FastAPI が Supabase で JWT を検証
8. 検証成功後、リクエスト処理を実行

### データフロー（コメント生成）

1. ユーザーがレポート本文を入力
2. **PII検出**: 個人情報（氏名、学籍番号、メールアドレス等）を検出・マスキング
3. **Rubric自動採点**: レポート本文をLLMに送信し、5項目を1-5点で採点 + 理由生成
4. **要約生成**: レポートの要点を100文字程度で要約
5. **RAG検索**: 過去の教授コメント50件からJaccard類似度で上位3件を取得
6. **コメント生成**: reflection.txt または final.txt プロンプトを使用してコメント生成
7. **データ保存**: レポート本文（暗号化）、マスキング後本文、Rubric、要約、コメントをSupabaseに保存
8. **結果表示**: ユーザーに結果を表示（Rubric、要約、コメント）
9. **手直し時間測定**: ユーザーがコメントを編集した時間を記録
10. **満足度アンケート**: コメント確定後に満足度（1-5）を収集

---

## 🔐 セキュリティ要件（Phase 1）

### Phase 1 で実装する項目（必須）

| 項目 | 内容 | 優先度 |
|------|------|--------|
| 認証 | Google OAuth（Supabase Auth） | 必須 |
| セッション管理 | Supabase JWT、有効期限7日間 | 必須 |
| HTTPS | Vercel標準対応 | 必須 |
| データ暗号化 | レポート本文を暗号化して保存（AES-256） | 必須 |
| PII検出 | 正規表現ベース（氏名、学籍番号、メールアドレス等） | 必須 |
| Row Level Security | Supabase RLS（ユーザー毎にデータ分離） | 必須 |
| CORS設定 | Vercelドメインのみ許可 | 必須 |
| セキュリティヘッダ | X-Content-Type-Options, X-Frame-Options等 | 必須 |
| 即時削除機能 | ユーザーがデータを即座に削除可能 | 必須 |
| ログ記録 | 基本的なアクセスログ・エラーログ | 必須 |

### Phase 2-A で実装する項目（延期）

- RBAC（ロールベースアクセス制御）
- 本格的な監視基盤（Prometheus/Grafana）
- 正式なSLA（72時間以内のデータ削除保証等）
- レート制限（Rate Limiting）
- WAF（Web Application Firewall）
- 定期的な脆弱性スキャン

### PII検出対象（Phase 1）

**検出対象**:
- 氏名（日本語フルネーム、漢字・ひらがな・カタカナ）
- 学籍番号（数字・英数字の組み合わせ）
- メールアドレス
- 電話番号

**検出方法**:
- 正規表現パターンマッチング
- 高精度な固有表現抽出（NER）はPhase 2-Aで実装

**マスキング方法**:
- 「[氏名]」「[学籍番号]」「[メールアドレス]」「[電話番号]」に置換
- マスキング後の本文をLLMに送信（個人情報を送信しない）

---

## 📊 品質評価・KPI（Phase 1）

### 目標KPI（Phase 1終了時点）

| KPI | Phase 1目標値 | 測定方法 |
|-----|--------------|---------|
| Rubric採点精度 | 教授の採点との差 ±1.0以内 80%以上 | UAT期間中に20件測定 |
| コメント満足度 | 平均4.0以上（5点満点） | 満足度アンケート（UAT期間中） |
| 手直し時間削減率 | 30%以上削減 | 手直し時間測定機能で記録 |
| システム成功率 | 95%以上 | エラーログから算出 |

### Phase 2-A で追加するKPI

- コメント文字数一致率（参照例±10%以内）
- RAG検索精度（Embedding類似度での評価）
- コメント生成速度（P95レスポンスタイム < 5秒）
- 可用性（Uptime 99.5%以上）

### ベースライン測定

**実施時期**: Week 0（Phase 1開始前）

**測定内容**:
- AI不使用時の平均手直し時間（1件あたり）
- AI不使用時の総コメント作成時間（1件あたり）

**測定方法**:
- 教授に5件のレポートについて従来通りコメント作成してもらう
- タイマーで時間を計測

---

## 🎯 機能要件（Phase 1）

### 1. 認証機能

#### 1.1 ログイン画面
- Google OAuth ログインボタン表示
- 初回ログイン時の利用規約同意チェックボックス（docs/policy.mdに基づく）
- ログイン失敗時のエラーメッセージ表示

#### 1.2 セッション管理
- Supabase JWT による認証状態管理
- セッション有効期限: 7日間
- 自動ログアウト機能（セッション切れ時）

### 2. メイン画面（レポートコメント生成）

#### 2.1 レイアウト
- 2カラムレイアウト（7:5の比率）
- 左カラム: レポート入力エリア
- 右カラム: 結果表示エリア（タブ切り替え）

#### 2.2 左カラム（入力エリア）
- **レポート種別選択**: reflection / final のラジオボタン
- **レポート本文入力**: テキストエリア（5000文字制限）
- **文字数カウンター**: リアルタイム表示
- **「生成」ボタン**: クリックでコメント生成開始
- **「クリア」ボタン**: 入力内容をクリア

#### 2.3 右カラム（結果表示エリア）
- **タブ構成**:
  - タブ1: Rubric採点結果
  - タブ2: 要約
  - タブ3: コメント（手直し可能）

#### 2.4 Rubric採点結果タブ
- 5項目を表形式で表示:
  - 理解度（1-5点） + 理由
  - 論理性（1-5点） + 理由
  - 独自性（1-5点） + 理由
  - 実践性（1-5点） + 理由
  - 表現力（1-5点） + 理由
- 合計点表示（25点満点）

#### 2.5 要約タブ
- 学生の主張を100文字程度で要約
- コピーボタン

#### 2.6 コメントタブ
- 生成されたコメントを表示
- テキストエリアで編集可能
- **「コピー」ボタン**: クリップボードにコピー
- **「保存」ボタン**: データベースに保存
- **手直し時間測定**: コメント生成完了時点から「保存」ボタン押下までの時間を自動記録
- **満足度アンケート**: 保存後にモーダル表示（1-5点）

#### 2.7 ローディングUX
- 生成中は段階的に進捗を表示:
  1. PII検出中...
  2. Rubric採点中...
  3. 要約生成中...
  4. 過去コメント検索中...
  5. コメント生成中...
- 各ステップ完了時にチェックマーク表示

#### 2.8 エラーハンドリング
- OpenAI API エラー時: ヒューリスティックフォールバック実行
- ネットワークエラー時: リトライボタン表示
- PII検出エラー時: 警告表示してユーザーに確認を求める

### 3. 履歴機能

#### 3.1 履歴一覧画面
- ヘッダーの「履歴」ボタンからアクセス
- 過去に生成したコメントの一覧を表示:
  - 生成日時
  - レポート種別（reflection/final）
  - レポート本文の冒頭50文字
  - Rubric合計点
- ページネーション（10件/ページ）
- クリックで詳細表示

#### 3.2 履歴詳細画面
- 過去のレポート本文、Rubric、要約、コメントを表示
- 再編集不可（読み取り専用）
- 「削除」ボタン: 即座にデータベースから削除

#### 3.3 エクスポート機能
- 履歴一覧画面に「エクスポート」ボタン
- JSON形式またはCSV形式でダウンロード
- エクスポート対象: 全履歴（ユーザー自身のデータのみ）

### 4. バックエンド機能

#### 4.1 コメント生成API（POST /generate）
- **入力**:
  - report_text: レポート本文
  - report_type: "reflection" または "final"
  - user_id: 認証ユーザーID（JWTから取得）
- **処理フロー**:
  1. PII検出・マスキング
  2. Rubric自動採点 + 理由生成
  3. 要約生成
  4. RAG検索（Jaccard類似度で上位3件取得）
  5. コメント生成（prompts/reflection.txt または prompts/final.txt 使用）
  6. データ暗号化
  7. データベース保存
- **出力**:
  - rubric: {理解度, 論理性, 独自性, 実践性, 表現力}
  - rubric_reasons: {理解度の理由, 論理性の理由, ...}
  - summary: 要約本文
  - comment: 生成されたコメント
  - masked_text: マスキング後のレポート本文
  - history_id: 保存されたレコードのID

#### 4.2 履歴取得API（GET /history）
- **入力**:
  - user_id: 認証ユーザーID（JWTから取得）
  - page: ページ番号（デフォルト1）
  - limit: 件数（デフォルト10）
- **出力**:
  - histories: 履歴一覧（配列）
  - total: 総件数

#### 4.3 履歴削除API（DELETE /history/{history_id}）
- **入力**:
  - history_id: 削除対象のレコードID
  - user_id: 認証ユーザーID（JWTから取得）
- **処理**:
  - データベースから即座に物理削除
  - RLSにより他ユーザーのデータは削除不可

#### 4.4 エクスポートAPI（GET /export）
- **入力**:
  - user_id: 認証ユーザーID（JWTから取得）
  - format: "json" または "csv"
- **出力**:
  - JSON形式またはCSV形式のファイル

#### 4.5 統計情報API（GET /stats）
- **入力**:
  - user_id: 認証ユーザーID（JWTから取得）
- **出力**:
  - 総コメント生成数
  - 平均Rubric点数（5項目別）
  - 平均手直し時間
  - 平均満足度

#### 4.6 認証ミドルウェア
- すべてのAPIエンドポイントで JWT 検証を実行
- 検証失敗時は 401 Unauthorized を返却

### 5. PII検出機能

#### 5.1 PIIDetectorクラス
- **検出対象**:
  - 氏名: 正規表現パターン（姓・名の組み合わせ）
  - 学籍番号: 正規表現パターン（数字・英数字）
  - メールアドレス: 正規表現パターン
  - 電話番号: 正規表現パターン（ハイフン有無両対応）

- **検出方法**:
  ```python
  class PIIDetector:
      def detect(self, text: str) -> List[PIIMatch]:
          # 正規表現で検出
          pass

      def mask(self, text: str, matches: List[PIIMatch]) -> str:
          # [氏名]等に置換
          pass
  ```

#### 5.2 検出精度の目標
- 氏名検出率: 80%以上（Phase 1目標）
- 誤検出率: 20%以下
- ※ Phase 2-AでNER（固有表現抽出）による高精度化を実施

### 6. final レポート対応

#### 6.1 prompts/final.txt 作成
- reflection.txt をベースに調整
- final レポート特有の指示を追加:
  - 全体の成長を評価
  - より深い示唆を提供
  - 次のステップ（卒業後のキャリア等）への示唆

#### 6.2 コメント生成時の分岐
- report_type が "final" の場合は prompts/final.txt を使用
- それ以外は prompts/reflection.txt を使用

---

## 🗄️ データベース設計（Phase 1）

### テーブル設計

#### 1. histories テーブル（コメント生成履歴）

| カラム名 | 型 | NULL | 説明 |
|---------|---|------|------|
| id | UUID | NOT NULL | 主キー |
| user_id | UUID | NOT NULL | ユーザーID（Supabase Auth） |
| report_type | TEXT | NOT NULL | "reflection" or "final" |
| report_text_encrypted | TEXT | NOT NULL | 暗号化されたレポート本文 |
| masked_text | TEXT | NOT NULL | マスキング後のレポート本文 |
| rubric_scores | JSONB | NOT NULL | {理解度, 論理性, ...} |
| rubric_reasons | JSONB | NOT NULL | {理解度の理由, ...} |
| summary | TEXT | NOT NULL | 要約本文 |
| comment | TEXT | NOT NULL | 生成されたコメント |
| edit_time_seconds | INTEGER | NULL | 手直し時間（秒） |
| satisfaction | INTEGER | NULL | 満足度（1-5） |
| created_at | TIMESTAMP | NOT NULL | 作成日時 |
| updated_at | TIMESTAMP | NOT NULL | 更新日時 |

**インデックス**:
- PRIMARY KEY (id)
- INDEX ON (user_id, created_at DESC)

**RLS（Row Level Security）**:
```sql
CREATE POLICY "Users can only see their own histories"
ON histories FOR SELECT
USING (auth.uid() = user_id);

CREATE POLICY "Users can only insert their own histories"
ON histories FOR INSERT
WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Users can only delete their own histories"
ON histories FOR DELETE
USING (auth.uid() = user_id);
```

#### 2. knowledge_base テーブル（過去コメント例）

| カラム名 | 型 | NULL | 説明 |
|---------|---|------|------|
| id | UUID | NOT NULL | 主キー |
| comment_text | TEXT | NOT NULL | コメント本文 |
| report_type | TEXT | NOT NULL | "reflection" or "final" |
| created_at | TIMESTAMP | NOT NULL | 作成日時 |

**初期データ**:
- data/sample_comments.json から50件移行

**RLS**:
- 全ユーザーが読み取り可能
- 管理者のみ挿入・更新・削除可能（Phase 2-Aで実装）

#### 3. users テーブル（Supabase Auth標準テーブル）
- Supabase Authが自動管理
- 追加カラムは不要（Phase 1）

### 暗号化方式

- **アルゴリズム**: AES-256-GCM
- **鍵管理**: Supabase Vaultに保存（環境変数として管理）
- **暗号化対象**: report_text のみ（masked_text は平文）
- **実装**: Python cryptography ライブラリ

---

## 🎨 UI/UXデザイン

### Academic Minimal UI（デザインシステム）

#### 設計思想
- 学術的で落ち着いた雰囲気
- 視認性・可読性を最重視
- 温かみのある色使い

#### カラーパレット

```css
/* design-tokens.css */
:root {
  --color-bg-primary: #fefefe;
  --color-bg-secondary: #f7f7f7;
  --color-text-primary: #2c2c2c;
  --color-text-secondary: #6b6b6b;
  --color-accent: #4a90e2;
  --color-accent-hover: #357abd;
  --color-border: #e0e0e0;
  --color-success: #5cb85c;
  --color-warning: #f0ad4e;
  --color-error: #d9534f;
}
```

#### コンポーネント設計

**Button**:
```tsx
// components/ui/Button.tsx
<button className="px-4 py-2 bg-accent text-white rounded-md hover:bg-accent-hover transition">
  生成
</button>
```

**TextArea**:
```tsx
// components/ui/TextArea.tsx
<textarea className="w-full h-64 p-3 border border-border rounded-md focus:ring-2 focus:ring-accent" />
```

**Card**:
```tsx
// components/ui/Card.tsx
<div className="bg-bg-secondary border border-border rounded-lg p-4 shadow-sm" />
```

**Tabs**:
```tsx
// components/ui/Tabs.tsx
<div className="flex border-b border-border">
  <button className="px-4 py-2 border-b-2 border-accent text-accent">
    Rubric
  </button>
  <button className="px-4 py-2 text-text-secondary hover:text-text-primary">
    要約
  </button>
</div>
```

#### レスポンシブ対応
- Phase 1はデスクトップのみ対応（教授は固定PC使用）
- Phase 2-Aでモバイル対応検討

---

## ⚙️ 運用要件（Phase 1）

### Phase 1 で実装する項目（必須）

| 項目 | 内容 | 目標値 |
|------|------|--------|
| システム成功率 | エラーログから算出 | 95%以上 |
| ログ記録 | アクセスログ・エラーログをファイル出力 | 必須 |
| 即時削除 | ユーザーによるデータ即時削除 | 必須 |
| コスト監視 | 月次の手動確認（OpenAIダッシュボード） | 必須 |

### Phase 2-A で実装する項目（延期）

- 可用性（Uptime 99.5%以上）
- レスポンスタイム（P95 < 5秒）
- 正式なSLA（72時間以内のデータ削除保証）
- 本格的な監視基盤（Prometheus/Grafana/Datadog）
- レート制限（Rate Limiting）
- 日次コスト監視
- アラート通知（Slack/Email）

### ログ記録方針

#### Phase 1（基本レベル）

**記録内容**:
- アクセスログ（URL、メソッド、ステータスコード、レスポンスタイム）
- エラーログ（エラー内容、スタックトレース、発生時刻）
- API呼び出しログ（OpenAI API、成功/失敗、トークン数）

**保存先**:
- ファイルシステム（logs/app.log）
- ローテーション: 7日間保持

**実装方法**:
```python
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/app.log'),
        logging.StreamHandler()
    ]
)
```

#### Phase 2-A（本格化）
- Datadog APM導入
- カスタムメトリクス収集
- ダッシュボード構築

### コスト管理

#### Phase 1（月次の手動確認）

**確認項目**:
- OpenAI API使用料（OpenAIダッシュボードで確認）
- Vercel使用料（Vercelダッシュボードで確認）
- Supabase使用料（Supabaseダッシュボードで確認）

**実施頻度**: 月1回

**アクション基準**:
- 月間コストが¥3,000を超えた場合は使用量を確認
- 異常な急増があればOpenAI APIキーを再生成

#### Phase 2-A（自動監視）
- Datadog Cost Monitoring導入
- 日次レポート自動送信
- 閾値超過時の自動アラート

---

## 📅 開発スケジュール（Phase 1）

### 全体スケジュール: 13-15週間

| 期間 | フェーズ | 内容 |
|------|---------|------|
| Week 0 | 準備週間 | 利用規約作成、OSSライセンス整理、学内審査資料準備、ナレッジベース構造確定 |
| Week 1-2 | 環境構築 + 認証 | Next.js + Supabase セットアップ、Google OAuth実装 |
| Week 3-4 | UI実装 | Academic Minimal UI移植、メイン画面実装 |
| Week 5-6 | バックエンド強化 | PII検出、final対応、セキュリティ設定 |
| Week 7-9 | DB連携 | Supabaseテーブル設計、RLS設定、データ暗号化、履歴機能 |
| Week 10-11 | 品質評価 | 手直し時間測定、満足度アンケート、統計表示、テスト実装 |
| Week 12 | 検証・改善 | UAT実施、ベースライン測定、バグ修正 |
| Week 13-14 | 最終調整 | ドキュメント作成、デプロイ準備、Phase 2-Aキックオフ |

### Week 0: 準備週間（5日間）

**目標**: Phase 1開発に必要な準備を完了

**タスク**:
1. **利用規約・同意文作成**（docs/policy.md）
   - 個人情報の取り扱い
   - データ保存期間（無期限、ただし即時削除可能）
   - OpenAI APIへのデータ送信についての同意
   - OSSライセンス情報（docs/licenses.md参照）

2. **OSSライセンス一覧作成**（docs/licenses.md）
   - Next.js: MIT License
   - TailwindCSS: MIT License
   - FastAPI: MIT License
   - Supabase: Apache 2.0
   - OpenAI Python SDK: MIT License
   - その他依存ライブラリのライセンス一覧

3. **学内審査資料準備**（必要に応じて）
   - システム概要説明資料
   - セキュリティ対策説明資料
   - 個人情報保護対策説明資料

4. **ナレッジベース構造確定**
   - data/sample_comments.json の整理
   - reflection / final の分類確認
   - 不要なコメント例の削除
   - Phase移行基準の合意（教授と打ち合わせ）

5. **開発環境準備**
   - GitHubリポジトリ作成
   - VercelアカウントWORK
   - Supabaseアカウント作成
   - OpenAI APIキー確認

### Week 1-2: 環境セットアップ + 認証（2週間）

**タスク**:
1. Next.jsプロジェクト作成 + TypeScript設定
2. TailwindCSS設定 + design-tokens.css作成
3. Supabaseプロジェクト作成 + データベース作成
4. Google OAuth設定（Supabase Auth）
5. ログイン画面実装
6. 認証フロー実装（JWT検証）
7. FastAPI認証ミドルウェア実装

**成果物**:
- Next.jsプロジェクト
- ログイン画面
- 認証機能

### Week 3-4: メイン画面 + UI実装（2週間）

**タスク**:
1. Academic Minimal UI移植（Streamlit CSSからTailwindCSSへ）
2. 共通UIコンポーネント実装（Button/TextArea/Card/Tabs）
3. メイン画面レイアウト（2カラム）
4. タブ表示実装（Rubric/要約/コメント）
5. ローディングUX実装（段階的表示）
6. エラーメッセージガイドライン作成

**成果物**:
- メイン画面UI
- 共通UIコンポーネント

### Week 5-6: バックエンド強化 + PII検出（2週間）

**タスク**:
1. FastAPI認証ミドルウェア実装
2. PII検出機能実装（PIIDetectorクラス）
3. final対応（prompts/final.txt作成）
4. セキュリティヘッダ設定
5. CORS設定
6. 基本ログ記録実装

**成果物**:
- PII検出機能
- final対応
- セキュリティ設定

### Week 7-9: DB連携 + データ管理（3週間）

**タスク**:
1. Supabaseテーブル設計 + マイグレーション実行
2. Row Level Security (RLS) 設定
3. データ暗号化実装（AES-256-GCM）
4. API修正（DB保存処理追加）
5. 履歴取得API実装
6. 履歴削除機能実装
7. エクスポート機能実装（JSON/CSV）
8. sample_comments.json → knowledge_base テーブルへ移行

**成果物**:
- データベーススキーマ
- 履歴機能
- エクスポート機能

### Week 10-11: 品質評価 + 既存機能完成（2週間）

**タスク**:
1. 手直し時間測定機能実装
2. 満足度アンケート実装（簡易版）
3. 基本統計表示（メトリクス数値のみ）
4. Rubric理由生成の改善
5. 要約生成の改善
6. ユニットテスト実装（主要ロジック）
7. UAT計画書作成

**成果物**:
- 品質測定機能
- 統計表示機能
- UAT計画書

### Week 12: 検証・改善（1週間）

**タスク**:
1. 教授による実運用テスト（UAT実施）
2. ベースライン測定（AI不使用時の手直し時間）
3. フィードバック収集
4. バグ修正
5. 微調整

**成果物**:
- UAT報告書
- バグ修正

### Week 13-14: 最終調整・ドキュメント（1〜2週間）

**タスク**:
1. ユーザーマニュアル作成
2. 管理者マニュアル作成
3. 技術仕様書作成（本ドキュメント更新）
4. 緊急対応手順書作成
5. データ移行計画書作成（Phase 2-A用）
6. デプロイ準備（Vercel + Supabase本番環境）
7. Phase 2-Aキックオフミーティング準備

**成果物**:
- 各種ドキュメント
- 本番環境デプロイ

---

## 🧪 テスト戦略

### Phase 1 で実施するテスト

#### 1. ユニットテスト
- **対象**: 主要ロジック
  - PIIDetector.detect()
  - PIIDetector.mask()
  - Rubric scoring logic
  - RAG search (Jaccard similarity)
  - Encryption/Decryption

- **ツール**: pytest
- **カバレッジ目標**: 60%以上

#### 2. 結合テスト
- **対象**: API エンドポイント
  - POST /generate
  - GET /history
  - DELETE /history/{id}
  - GET /export
  - GET /stats

- **ツール**: pytest + httpx
- **カバレッジ目標**: 主要エンドポイントの正常系・異常系

#### 3. UAT（ユーザー受け入れテスト）
- **実施者**: 教授
- **期間**: Week 12（1週間）
- **テスト内容**:
  - 20件のレポートに対してコメント生成
  - Rubric採点精度の確認
  - 手直し時間の測定
  - 満足度アンケートの記入
- **合格基準**:
  - Rubric採点精度 ±1.0以内 80%以上
  - 満足度 平均4.0以上
  - 手直し時間削減率 30%以上

### Phase 2-A で追加するテスト

- E2Eテスト（Playwright）
- パフォーマンステスト（Locust）
- セキュリティテスト（OWASP ZAP）
- 負荷テスト（Apache JMeter）

---

## 📚 ドキュメント一覧（Phase 1成果物）

| ドキュメント名 | ファイル名 | 内容 |
|--------------|-----------|------|
| 要件定義書v2 | docs/requirements_mvp_v2.md | 本ドキュメント |
| 技術仕様書 | docs/architecture.md | システムアーキテクチャ、DB設計、API仕様 |
| 開発手順書 | docs/development_guide.md | Week毎の実装手順、セットアップ手順 |
| 利用規約 | docs/policy.md | 個人情報取り扱い、同意文 |
| OSSライセンス一覧 | docs/licenses.md | 使用OSSのライセンス情報 |
| ユーザーマニュアル | docs/user_manual.md | 教授向けの使い方ガイド |
| 管理者マニュアル | docs/admin_manual.md | 技術管理者向けの運用ガイド |
| 緊急対応手順書 | docs/incident_response.md | 障害発生時の対応手順 |
| データ移行計画書 | docs/migration_plan.md | Phase 2-A用のデータ移行計画 |
| UAT計画書 | docs/uat_plan.md | UAT実施計画 |
| UAT報告書 | docs/uat_report.md | UAT実施結果 |

---

## 💰 コスト見積もり（Phase 1）

### 月間コスト（Phase 1運用時）

| 項目 | 詳細 | 月額コスト |
|------|------|-----------|
| OpenAI API | gpt-4o-mini、週5件 × 20週 = 100件/年<br>≒ 10件/月、1件0.02ドル | ¥30 |
| Vercel | Hobby Plan（無料枠） | ¥0 |
| Supabase | Free Tier（500MB、50,000リクエスト） | ¥0 |
| **合計** | | **¥30/月** |

### Phase 2-A運用時のコスト増加

| 項目 | 月額コスト |
|------|-----------|
| OpenAI API | ¥200（利用量増加） |
| Vercel | ¥2,000（Pro Plan） |
| Supabase | ¥3,000（Pro Plan） |
| Datadog | ¥5,000（APM） |
| **合計** | **¥10,200/月** |

---

## 🚀 Phase移行基準

### Phase 1 → Phase 2-A 移行条件

以下の全条件を満たした場合にPhase 2-Aへ移行:

1. **KPI達成**:
   - Rubric採点精度 ±1.0以内 80%以上
   - コメント満足度 平均4.0以上
   - 手直し時間削減率 30%以上
   - システム成功率 95%以上

2. **UAT完了**:
   - 教授による20件のテストが完了
   - 重大なバグが存在しない

3. **教授の判断**:
   - 教授がPhase 2-Aへの移行を承認

### Phase 2-A → Phase 2-B 移行条件

1. データベースに100件以上のコメント履歴が蓄積
2. RAG検索精度の改善が確認できる
3. 教授がマルチモーダル機能（音声・資料）を必要と判断

### Phase 2-B → Phase 3 移行条件

1. 学生向けチャット機能の必要性が確認できる
2. コスト管理体制が確立している
3. 教授が学生への公開を承認

---

## ⚠️ リスク管理

### Phase 1 で想定されるリスク

| リスク | 影響度 | 発生確率 | 対策 |
|--------|--------|---------|------|
| OpenAI API障害 | 高 | 低 | ヒューリスティックフォールバック実装 |
| PII検出精度不足 | 中 | 中 | 誤検出を許容（Phase 2-Aで改善） |
| 開発期間超過 | 中 | 中 | スコープ調整、Week 0バッファ確保 |
| Google OAuth設定ミス | 低 | 低 | Supabase公式ドキュメント参照 |
| Rubric採点精度不足 | 高 | 中 | プロンプト改善、UAT期間で調整 |
| データ暗号化の実装ミス | 高 | 低 | cryptographyライブラリ使用、テスト実施 |
| SupabaseのRLS設定ミス | 高 | 低 | 公式ドキュメント参照、テスト実施 |
| コスト超過 | 低 | 低 | 月次確認、無料枠内で運用 |

---

## 📖 参考資料

### 技術ドキュメント

- **Next.js**: https://nextjs.org/docs
- **TailwindCSS**: https://tailwindcss.com/docs
- **FastAPI**: https://fastapi.tiangolo.com/
- **Supabase**: https://supabase.com/docs
- **Supabase Auth**: https://supabase.com/docs/guides/auth
- **OpenAI API**: https://platform.openai.com/docs/api-reference
- **Python cryptography**: https://cryptography.io/en/latest/

### 設計方針

- **Academic Minimal UI**: Streamlit app/streamlit_app.py の CSS を参考
- **過去コメント例**: data/sample_comments.json（50件）
- **プロンプト**: prompts/reflection.txt（要作成: prompts/final.txt）

---

## ✅ Phase 1 完了定義（Definition of Done）

Phase 1が完了したと判断する基準:

### 機能完成
- [ ] Google OAuth認証が動作する
- [ ] メイン画面でコメント生成ができる
- [ ] PII検出・マスキングが動作する
- [ ] Rubric自動採点 + 理由生成が動作する
- [ ] 要約生成が動作する
- [ ] final対応が動作する
- [ ] 履歴機能（保存・取得・削除）が動作する
- [ ] エクスポート機能（JSON/CSV）が動作する
- [ ] 手直し時間測定が動作する
- [ ] 満足度アンケートが動作する
- [ ] 基本統計表示が動作する

### 品質達成
- [ ] ユニットテスト カバレッジ60%以上
- [ ] 結合テスト 主要エンドポイント正常系・異常系完了
- [ ] UAT実施完了（20件）
- [ ] KPI達成（Rubric ±1.0以内 80%以上、満足度4.0以上、手直し時間削減30%以上）

### ドキュメント完成
- [ ] 要件定義書v2（本ドキュメント）
- [ ] 技術仕様書（architecture.md）
- [ ] 開発手順書（development_guide.md）
- [ ] 利用規約（policy.md）
- [ ] OSSライセンス一覧（licenses.md）
- [ ] ユーザーマニュアル（user_manual.md）
- [ ] 管理者マニュアル（admin_manual.md）
- [ ] 緊急対応手順書（incident_response.md）
- [ ] データ移行計画書（migration_plan.md）
- [ ] UAT計画書（uat_plan.md）
- [ ] UAT報告書（uat_report.md）

### デプロイ完了
- [ ] Vercel本番環境デプロイ
- [ ] Supabase本番環境構築
- [ ] Google OAuth本番設定
- [ ] 本番環境での動作確認

### 教授承認
- [ ] 教授によるUAT完了承認
- [ ] Phase 2-A移行の合意

---

## 📞 問い合わせ先

**開発責任者**: [担当者名]
**メール**: [メールアドレス]
**Slack**: [Slackチャンネル]

---

**以上**
