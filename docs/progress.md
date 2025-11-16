# 開発進捗状況

**最終更新**: 2025-11-16
**現在のフェーズ**: Week 12 準備完了（Phase 1 MVP 90%完了）

---

## 📊 全体進捗

| フェーズ | 期間 | 状態 | 完了日 |
|---------|------|------|--------|
| **Week 0: 準備週間** | 5日間 | ✅ 完了 | 2025-11-11 |
| **Week 1: 環境セットアップ** | 1週間 | ✅ 完了 | 2025-11-11 |
| **Week 2: 認証実装** | 1週間 | ✅ 完了 | 2025-11-14 |
| **Week 3-4: UI実装** | 2週間 | ✅ 完了 | 2025-11-14 |
| **Week 5-6: バックエンド強化** | 2週間 | ✅ 完了 | 2025-11-14 |
| **Week 7-9: DB連携** | 3週間 | ✅ 完了 | 2025-11-14 |
| **Week 10-11: 品質評価** | 2週間 | ✅ 完了 | 2025-11-14 |
| **Week 12: 検証・改善** | 1週間 | 🔄 準備完了 | 2025-11-16 |
| Week 13-14: 最終調整 | 1-2週間 | ⏳ 未着手 | - |

**進捗率**: 90% (12/13週間、準備作業完了)

---

## ✅ Week 0: 準備週間（完了）

### 実施内容

#### 1. 利用規約・同意文作成
- **ファイル**: `docs/policy.md`
- **内容**:
  - サービス概要
  - 個人情報の取り扱い
  - 第三者へのデータ提供（OpenAI API、Supabase、Vercel）
  - データの利用目的
  - ユーザーの権利（閲覧・削除・エクスポート）
  - 免責事項
  - 準拠法・管轄裁判所

#### 2. OSSライセンス一覧作成
- **ファイル**: `docs/licenses.md`
- **内容**:
  - Frontend（Next.js、React、TailwindCSS等）
  - Backend（FastAPI、Pydantic、OpenAI等）
  - Infrastructure（Supabase、PostgreSQL等）
  - 各ライセンスの詳細説明

#### 3. .gitignore作成
- **ファイル**: `.gitignore`
- **内容**:
  - Next.js用の除外設定
  - Python用の除外設定
  - 環境変数ファイル（.env）の除外
  - IDE設定ファイルの除外

---

## ✅ Week 1: 環境セットアップ（完了）

### 実施内容

#### 1. Next.js 14プロジェクトセットアップ
- **コマンド**: `npx create-next-app@14`
- **設定**:
  - ✅ TypeScript有効
  - ✅ TailwindCSS有効
  - ✅ ESLint有効
  - ✅ App Router使用
  - ✅ Import alias設定（@/*）

#### 2. Academic Minimal UIデザイン統合
- **ファイル**: `frontend/app/globals.css`
- **内容**:
  - 既存の`ui/design-tokens.css`からデザイントークンを移植
  - CSS変数ベースのデザインシステム
  - 色、タイポグラフィ、スペーシング（8pxグリッド）
  - 7:5グリッドレイアウト対応

**デザインシステムの特徴**:
```css
/* Colors */
--bg: #F9FAFB;
--surface: #FFFFFF;
--accent: #2563EB;

/* Spacing (8px Grid) */
--g1: 8px;
--g2: 16px;
--g3: 24px;
--g4: 32px;

/* Typography */
--font-body: 'Noto Sans JP', ui-sans-serif, system-ui...
--font-size-base: 15px;
```

#### 3. Supabaseパッケージインストール
- **パッケージ**:
  - `@supabase/supabase-js` (最新版)
  - `@supabase/ssr` (最新版)
- **コマンド**: `npm install @supabase/supabase-js @supabase/ssr`

#### 4. Supabaseクライアント設定
- **ファイル**: `frontend/lib/supabase.ts`
- **内容**:
  - Supabaseクライアントの初期化
  - 環境変数の型安全な取得
  - エラーハンドリング

#### 5. 環境変数テンプレート作成
- **ファイル**: `frontend/.env.local.example`
- **内容**:
  - `NEXT_PUBLIC_SUPABASE_URL`
  - `NEXT_PUBLIC_SUPABASE_ANON_KEY`
  - `NEXT_PUBLIC_API_BASE_URL`

---

## 📄 ドキュメント作成（完了）

### 1. 要件定義書 v2.0
- **ファイル**: `docs/requirements_mvp_v2.md`
- **内容**:
  - 壁打ちセッション（1〜7）の結果を反映
  - Next.js採用への変更
  - Phase構成変更（Phase 2 → 2-A/2-B）
  - 開発期間延長（13-15週間）
  - 調整されたKPI（現実的な目標値）
  - 調整されたセキュリティ・運用要件

### 2. 技術仕様書
- **ファイル**: `docs/architecture.md`
- **内容**:
  - システムアーキテクチャ図
  - ER図とテーブル定義
  - API仕様（OpenAPI形式）
  - 認証フローのシーケンス図
  - PII検出ロジックの実装コード
  - データ暗号化方式（AES-256-GCM）
  - デプロイメント手順

### 3. 開発手順書
- **ファイル**: `docs/development_guide.md`
- **内容**:
  - Week 0〜14の段階的実装ガイド
  - 環境セットアップ手順
  - コーディング規約
  - テスト手順
  - トラブルシューティング

---

## 🎨 デザインシステム

### Academic Minimal UI

既存のStreamlit実装で使用されていたデザインシステムをNext.jsに移植しました。

**デザイン方針**:
- 学術的で落ち着いた雰囲気
- 視認性・可読性を最重視
- 温かみのある色使い

**カラーパレット**:
- Background: `#F9FAFB` (明るいグレー)
- Surface: `#FFFFFF` (白)
- Accent: `#2563EB` (青)
- Text: `#111827` (濃いグレー)

**レイアウト**:
- 7:5の2カラムグリッド（左: 入力、右: 結果）
- 8pxグリッドシステム
- 最適な読みやすさ（66文字/行）

---

## 🔧 手動設定作業（完了）

以下の手動設定作業が完了しています：

### 1. Supabaseプロジェクト作成
- ✅ プロジェクト名: `saiten-mvp`
- ✅ リージョン: Asia Pacific (Tokyo)
- ✅ 環境変数取得完了

### 2. Google OAuth設定
- ✅ Google Cloud Console でOAuth 2.0クライアント作成
- ✅ Supabase Auth でGoogle Provider設定
- ✅ リダイレクトURI設定完了

### 3. 環境変数設定
- ✅ `frontend/.env.local`ファイル作成
- ✅ Supabase URLとAPIキーを設定
- ✅ FastAPI URLを設定

---

## 📁 プロジェクト構造（現在）

```
saiten/
├── frontend/                  # Next.js 14プロジェクト ✨NEW
│   ├── app/
│   │   ├── globals.css       # Academic Minimal UI統合
│   │   ├── layout.tsx
│   │   ├── page.tsx
│   │   └── favicon.ico
│   ├── lib/
│   │   └── supabase.ts       # Supabaseクライアント
│   ├── node_modules/
│   ├── .env.local            # 環境変数（Gitignore済み）
│   ├── .env.local.example
│   ├── package.json
│   ├── tsconfig.json
│   └── tailwind.config.ts
├── api/                       # FastAPI（既存）
│   └── main.py
├── prompts/                   # プロンプトファイル（既存）
│   ├── reflection.txt
│   └── final.txt
├── data/                      # サンプルデータ（既存）
│   └── sample_comments.json
├── ui/                        # デザインシステム（既存）
│   ├── design-tokens.css
│   ├── base.css
│   └── components/
├── docs/                      # ドキュメント
│   ├── requirements_mvp_v2.md   # 要件定義書v2 ✨NEW
│   ├── architecture.md          # 技術仕様書 ✨NEW
│   ├── development_guide.md     # 開発手順書 ✨NEW
│   ├── policy.md                # 利用規約 ✨NEW
│   ├── licenses.md              # OSSライセンス ✨NEW
│   └── progress.md              # 本ファイル ✨NEW
├── .gitignore                 # Git設定 ✨NEW
└── README_START.md            # 起動手順（既存）
```

---

## ✅ Week 2: 認証実装（完了）

### 実施内容

#### 1. FastAPI JWT認証ミドルウェア実装
- **ファイル**: `api/main.py`
- **内容**:
  - `verify_jwt()` 関数の実装
  - Supabase JWT検証（HS256アルゴリズム）
  - 開発モード対応（`DISABLE_AUTH=1`）
  - すべての保護エンドポイントに適用

#### 2. フロントエンド認証ヘッダー実装
- **ファイル**: `frontend/lib/auth.ts`
- **内容**:
  - `getAccessToken()` 関数の追加
  - Supabaseセッションからトークン取得

#### 3. API通信の認証対応
- **ファイル**: `frontend/lib/api.ts`, `frontend/lib/references.ts`
- **内容**:
  - `getAuthHeaders()` ヘルパー関数
  - すべてのAPI呼び出しに Authorization ヘッダー追加

#### 4. 環境変数設定
- **ファイル**: `.env`
- **内容**:
  - `SUPABASE_URL`, `SUPABASE_ANON_KEY`, `SUPABASE_JWT_SECRET`
  - `DISABLE_AUTH=1` (開発モード)

#### 5. 認証セットアップドキュメント作成
- **ファイル**: `docs/authentication_setup.md`
- **内容**:
  - JWT検証の仕組み
  - 環境変数設定方法
  - トラブルシューティング

---

## ✅ Week 3-4: UI実装（完了）

### 実施内容

#### 1. メイン画面実装
- **ファイル**: `frontend/app/dashboard/page.tsx`
- **内容**:
  - 2カラムレイアウト（7:5比率）
  - 左カラム: レポート入力エリア
  - 右カラム: 結果表示エリア（タブ切り替え）

#### 2. タブ表示実装
- **タブ構成**:
  - タブ1: Rubric採点結果（5項目 + 理由）
  - タブ2: 要約（学生の主張を100文字程度で要約）
  - タブ3: コメント（手直し可能）

#### 3. ローディングUX実装
- 段階的な進捗表示:
  1. PII検出中...
  2. Rubric採点中...
  3. 要約生成中...
  4. 過去コメント検索中...
  5. コメント生成中...

#### 4. Academic Minimal UIの適用
- CSS変数ベースのデザインシステム
- 学術的で落ち着いた雰囲気
- 視認性・可読性を重視

---

## ✅ Week 5-6: バックエンド強化（完了）

### 実施内容

#### 1. PII検出・マスキング機能実装
- **ファイル**: `api/main.py`
- **クラス**: `PIIDetector`
- **検出対象**:
  - 氏名（日本語フルネーム）
  - 学籍番号（数字・英数字）
  - メールアドレス
  - 電話番号

- **実装方式**:
  - 正規表現パターンマッチング
  - 優先度ベースの検出（重複回避）
  - マスキング: `[氏名]`, `[学籍番号]`, `[メールアドレス]`, `[電話番号]`

#### 2. final レポート対応
- **ファイル**: `prompts/final.txt`
- `reflection.txt` をベースに調整
- final レポート特有の指示追加

#### 3. セキュリティ設定
- CORS設定（Vercelドメインのみ許可）
- セキュリティヘッダー設定
- 基本ログ記録実装

---

## ✅ Week 7-9: DB連携（完了）

### 実施内容

#### 1. データ暗号化機能実装
- **ファイル**: `api/main.py`
- **クラス**: `DataEncryption`
- **アルゴリズム**: AES-256-GCM
- **実装**:
  - `/encrypt` エンドポイント
  - `/decrypt` エンドポイント
  - 12バイトnonce使用

#### 2. フロントエンド暗号化統合
- **ファイル**: `frontend/lib/api.ts`, `frontend/lib/database.ts`
- **内容**:
  - `encryptText()`, `decryptText()` 関数
  - `saveReport()` でレポート本文を自動暗号化
  - 暗号化失敗時のグレースフルなフォールバック

#### 3. データベース操作関数
- **ファイル**: `frontend/lib/database.ts`
- **実装済み関数**:
  - `saveReport()`: レポート保存（暗号化付き）
  - `saveFeedback()`: コメント生成結果保存
  - `updateEditedComment()`: 編集されたコメント更新
  - `saveQualityRating()`: 品質評価保存
  - `getHistoryList()`: 履歴一覧取得
  - `getHistoryDetail()`: 履歴詳細取得
  - `deleteHistory()`: 履歴削除
  - `exportHistoryJSON()`: JSON形式エクスポート
  - `exportHistoryCSV()`: CSV形式エクスポート

---

## ✅ Week 10-11: 品質評価（完了）

### 実施内容

#### 1. 手直し時間測定機能
- **ファイル**: `frontend/app/dashboard/page.tsx`
- **実装**:
  - コメント生成完了時に `generateTime` を記録
  - 「保存」ボタン押下時に経過時間を計算
  - 秒単位でデータベースに保存

#### 2. 満足度アンケート機能
- **UI**: モーダル形式
- **評価**: 1-5点のボタン
- **フィードバック**: 任意のテキスト入力欄
- **実装**:
  - `handleSaveComment()`: 保存時にアンケート表示
  - `handleSubmitSurvey()`: アンケート結果をDBに保存

#### 3. 統計表示機能
- **ファイル**: `api/main.py`, `frontend/lib/api.ts`, `frontend/app/dashboard/page.tsx`
- **エンドポイント**: `/stats`
- **表示項目**:
  - 総コメント生成数
  - 平均Rubric点数（5項目別）
  - 平均手直し時間（分/秒形式）
  - 平均満足度
- **UI**: 折りたたみ可能な統計カード

#### 4. Python依存パッケージ追加
- **ファイル**: `requirements.txt`
- **追加パッケージ**:
  - `supabase>=2.0.0`
  - `pyjwt>=2.8.0`
  - `cryptography>=41.0.0`

---

## 🎯 次のステップ（Week 12）

### Week 12: 検証・改善（予定）

#### タスク一覧

1. **UAT（ユーザー受け入れテスト）実施**
   - 教授による実運用テスト（20件のレポート）
   - Rubric採点精度の確認
   - 手直し時間の測定
   - 満足度アンケートの記入

2. **ベースライン測定**
   - AI不使用時の手直し時間測定
   - 比較データの収集

3. **フィードバック収集**
   - 教授からのフィードバック
   - 改善点の洗い出し

4. **バグ修正**
   - UAT期間中に発見されたバグの修正
   - 微調整

5. **KPI達成確認**
   - Rubric採点精度 ±1.0以内 80%以上
   - 満足度 平均4.0以上
   - 手直し時間削減率 30%以上
   - システム成功率 95%以上

---

## 💾 Gitコミット履歴

### Commit 1: Week 0-1完了
- **コミットハッシュ**: `82264e0`
- **日時**: 2025-11-11
- **内容**:
  - Week 0: 利用規約、OSSライセンス、.gitignore作成
  - Week 1: Next.jsセットアップ、デザイン統合、Supabase設定
  - ドキュメント: 要件定義書v2、技術仕様書、開発手順書

### Commit 2: Week 2-11完了（予定）
- **日時**: 2025-11-14
- **内容**:
  - Week 2: FastAPI JWT認証、フロントエンド認証ヘッダー
  - Week 3-4: メイン画面UI、タブ表示、ローディングUX
  - Week 5-6: PII検出・マスキング、final対応、セキュリティ設定
  - Week 7-9: データ暗号化、データベース操作関数
  - Week 10-11: 手直し時間測定、満足度アンケート、統計表示
  - ドキュメント: 認証セットアップガイド、進捗状況更新

---

## 🎨 実装済み機能一覧

### 認証・セキュリティ
- ✅ Google OAuth認証（Supabase Auth）
- ✅ JWT認証ミドルウェア（FastAPI）
- ✅ Row Level Security（Supabase RLS）
- ✅ データ暗号化（AES-256-GCM）
- ✅ PII検出・マスキング（氏名、学籍番号、メール、電話番号）
- ✅ CORS設定
- ✅ セキュリティヘッダー設定

### コア機能
- ✅ レポート種別選択（reflection / final）
- ✅ Rubric自動採点（5項目 × 1-5点 + 理由）
- ✅ 要約生成（学生の主張を100文字程度で要約）
- ✅ 教授コメント生成（過去コメント例を参照）
- ✅ RAG検索（Jaccard類似度ベース）
- ✅ OpenAI API連携（gpt-4o-mini）

### UI/UX
- ✅ Academic Minimal UIデザインシステム
- ✅ 2カラムレイアウト（7:5比率）
- ✅ タブ切り替え（Rubric/要約/コメント）
- ✅ 段階的ローディング表示
- ✅ レスポンシブ対応（デスクトップ優先）

### データ管理
- ✅ レポート保存（暗号化付き）
- ✅ コメント生成結果保存
- ✅ 履歴一覧・詳細表示
- ✅ 履歴削除（即時削除）
- ✅ エクスポート機能（JSON/CSV）

### 品質評価
- ✅ 手直し時間測定
- ✅ 満足度アンケート（1-5点）
- ✅ フィードバックテキスト収集
- ✅ 基本統計表示（合計数、平均点、平均時間、平均満足度）

### ドキュメント
- ✅ 要件定義書v2（requirements_mvp_v2.md）
- ✅ 技術仕様書（architecture.md）
- ✅ 開発手順書（development_guide.md）
- ✅ 利用規約（policy.md）
- ✅ OSSライセンス一覧（licenses.md）
- ✅ 認証セットアップガイド（authentication_setup.md）
- ✅ 進捗状況（progress.md）

---

## 📊 リソース使用状況

### パッケージ数
- **Frontend**: 409パッケージ（脆弱性: 0件）
- **Backend**: requirements.txtに記載

### ディスクサイズ
- `frontend/node_modules/`: 約400MB
- `frontend/`: 約450MB（node_modules含む）

---

## 📝 メモ・備考

### 技術選定の理由

**なぜNext.jsを選んだか？**
- Phase 3でリアルタイムチャット機能が必要
- Streamlitではリアルタイム通信が困難
- Vercelでの簡単なデプロイ
- TypeScriptによる型安全性

**なぜAcademic Minimal UIを維持するか？**
- 既に完成度が高いデザインシステム
- 教授の好みに合致
- 学術的で落ち着いた雰囲気
- 視認性・可読性が高い

**なぜGoogle認証を残すべきか？**（2025-11-14 議論）
- セキュリティ: パスワード管理不要、Google側で多要素認証も利用可能
- 将来の拡張性: Phase 2以降で複数教員対応、Phase 3で学生チャット機能が予定
- 利便性: パスワードを覚える必要なし、大学のGoogleアカウントでログイン可能
- 既に実装済みで維持コストはほぼゼロ
- 一人利用の場合でも上記メリットがあるため、削除せず維持することを推奨

### 注意事項

1. **環境変数の管理**
   - `.env.local`はGit管理対象外
   - 本番環境では環境変数を適切に設定
   - `DISABLE_AUTH=1`は開発時のみ（本番では`0`に変更）

2. **Supabaseの無料枠**
   - Phase 1では無料枠で十分
   - Phase 2-Aでプラン検討

3. **OpenAI APIコスト**
   - 月間約¥30の想定（Phase 1）
   - コスト監視は月次で手動確認

4. **本番環境デプロイ前の必須設定**
   - `SUPABASE_JWT_SECRET`をSupabase DashboardのSettings > API > JWT Settingsから取得
   - `ENCRYPTION_KEY`を`python -c "import secrets; print(secrets.token_urlsafe(32))"`で生成
   - `DISABLE_AUTH=0`に変更

---

## 🔗 関連リンク

- [Supabase Dashboard](https://supabase.com/dashboard)
- [Google Cloud Console](https://console.cloud.google.com/)
- [Vercel Dashboard](https://vercel.com/dashboard)
- [Next.js Documentation](https://nextjs.org/docs)
- [Supabase Documentation](https://supabase.com/docs)

---

## 📌 現在の状況サマリー（2025-11-14時点）

### ✅ 完了済み（Week 0-11）
Phase 1 MVPの主要機能はほぼ実装完了（85%）

**認証・セキュリティ**:
- Google OAuth、JWT認証、データ暗号化、PII検出・マスキング

**コア機能**:
- Rubric自動採点、要約生成、コメント生成、RAG検索

**UI/UX**:
- Academic Minimal UI、2カラムレイアウト、タブ切り替え、ローディング表示

**データ管理**:
- 履歴保存・取得・削除、エクスポート機能

**品質評価**:
- 手直し時間測定、満足度アンケート、統計表示

---

## ✅ Week 12: 検証・改善（準備完了）

### 実施内容

#### 1. UAT計画書の作成
- **ファイル**: `docs/uat_plan.md`
- **内容**:
  - テスト目的とKPI（Rubric精度、満足度、削減率、成功率）
  - テスト範囲（Phase 1 MVP全機能）
  - テストシナリオ（5つのシナリオ）
  - テストケース詳細（20件のレポート）
  - データ収集項目（Rubric精度、手直し時間、満足度、エラーログ）
  - スケジュール（Week 12の1週間）
  - 報告書作成ガイド

#### 2. ベースライン測定ガイドの作成
- **ファイル**: `docs/baseline_measurement_guide.md`
- **内容**:
  - 測定目的（AI不使用時の作業時間を測定）
  - 測定方法（5件のレポートで測定）
  - 測定項目（読む時間、Rubric採点時間、コメント作成時間、推敲修正時間）
  - 測定手順（ステップバイステップガイド）
  - データ記録フォーマット（CSV形式）
  - 分析方法（削減率の計算）

#### 3. UATチェックリストの作成
- **ファイル**: `docs/uat_checklist.md`
- **内容**:
  - 認証機能（Google OAuth、セッション管理）
  - メイン画面（レイアウト、レポート入力、コメント生成）
  - Rubric採点機能（採点結果、採点精度）
  - 要約生成機能（要約表示、要約品質）
  - コメント編集機能（表示・編集、コメント品質、操作）
  - PII検出・マスキング（検出、マスキング）
  - 履歴機能（一覧、詳細、削除）
  - エクスポート機能（操作、データ確認）
  - 品質評価機能（手直し時間測定、満足度アンケート）
  - 統計表示機能（統計情報表示、データ正確性）
  - エラー処理（入力エラー、APIエラー、DBエラー）
  - パフォーマンス（レスポンスタイム、システム安定性）
  - UI/UX（デザイン、操作性、アクセシビリティ）

#### 4. 既知の問題点の洗い出し
- **ファイル**: `docs/known_issues_week12.md`
- **内容**:
  - 環境設定関連（環境変数、DB初期化）
  - セキュリティ関連（PII検出精度、鍵管理、CORS設定）
  - 機能実装関連（final対応、エラーハンドリング、参照例管理、統計表示）
  - UI/UX関連（モバイル対応、ローディング表示、コメント編集タブ）
  - パフォーマンス関連（タイムアウト設定、DBクエリ最適化）
  - ドキュメント関連（ユーザーマニュアル、管理者マニュアル）
  - UAT前確認項目（環境、機能、データ、セキュリティ、ドキュメント）

#### 5. システムの最終動作確認
- バックエンド（api/main.py）の実装確認
- フロントエンド（dashboard/page.tsx）の実装確認
- データベーススキーマ（database_schema.sql）の確認
- 主要機能の実装状況を検証

---

## 🎯 次のステップ（Week 12 実施）

### UAT実施準備（Day 1）
1. **環境確認**
   - フロントエンド・バックエンドの起動確認
   - Supabaseデータベース接続確認
   - Google OAuth認証確認
   - OpenAI APIキー確認

2. **テストデータ準備**
   - 20件のレポートサンプル準備（reflection 15件、final 5件）
   - 文字数範囲: 200〜1000文字
   - 内容カテゴリ: 戦略立案、組織変革、顧客分析等

3. **ドキュメント確認**
   - UAT計画書の最終確認
   - ベースライン測定ガイドの確認
   - UATチェックリストの印刷

### ベースライン測定（Day 2）
1. **AI不使用でのコメント作成**
   - 5件のレポートに対してコメント作成
   - 作業時間を測定（読む、採点、作成、推敲）
   - データを記録（CSV形式）

2. **データ分析**
   - 平均総作業時間を算出
   - ステップ別平均時間を算出
   - 期待削減率を試算

### UAT実施（Day 3-4）
1. **テストケース実施**
   - Day 3: テストケース1-10（前半）
   - Day 4: テストケース11-20（後半）
   - 各テストケースでデータ記録

2. **データ収集**
   - Rubric採点精度データ
   - 手直し時間データ
   - 満足度データ
   - エラーログ

### データ分析・報告書作成（Day 5）
1. **データ集計・分析**
   - KPI達成状況の確認
   - 詳細結果の分析
   - 問題点の洗い出し

2. **UAT報告書作成**
   - 実施概要
   - KPI達成状況
   - 詳細結果
   - 発見された問題点
   - 改善提案
   - 総合評価

### 📋 残タスク（Week 13-14）
- ドキュメント作成（ユーザーマニュアル、管理者マニュアル等）
- 本番環境デプロイ準備
- Phase 2-Aキックオフ

---

**次回セッション開始時**: Week 12のUAT実施（ベースライン測定またはテストケース実行）から開始
