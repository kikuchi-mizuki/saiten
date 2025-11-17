# Railway + Supabase セットアップガイド

**作成日**: 2025-11-17
**目的**: RailwayとSupabaseでシステムを構築する手順

---

## 📋 目次

1. [前提条件](#前提条件)
2. [Supabaseのセットアップ](#supabaseのセットアップ)
3. [参照例データのインポート](#参照例データのインポート)
4. [Railwayのセットアップ](#railwayのセットアップ)
5. [動作確認](#動作確認)
6. [トラブルシューティング](#トラブルシューティング)

---

## 📦 前提条件

- Supabaseアカウント（無料枠で可）
- Railwayアカウント（無料枠で可）
- Pythonがローカルにインストールされている（データインポート用）
- 環境変数が設定済み（`.env`ファイル）

---

## 🗄️ Supabaseのセットアップ

### 1. プロジェクトの作成

1. [Supabase Dashboard](https://supabase.com/dashboard)にアクセス
2. 「New Project」をクリック
3. プロジェクト情報を入力:
   - Name: `saiten-mvp`（任意）
   - Database Password: 安全なパスワードを設定
   - Region: `Asia Pacific (Tokyo)`
4. 「Create new project」をクリック

### 2. データベーススキーマの適用

1. Supabase Dashboard > SQL Editor を開く
2. 「+ New query」をクリック
3. `docs/database_schema.sql`の内容をコピー&ペースト
4. 「Run」をクリックして実行

**確認**:
- 左メニュー > Table Editor で以下のテーブルが作成されていることを確認:
  - `reports`
  - `feedbacks`
  - `knowledge_base` ← 新しく追加

### 3. 環境変数の取得

1. Supabase Dashboard > Settings > API を開く
2. 以下の値をコピー:
   - **Project URL**: `https://your-project-id.supabase.co`
   - **anon public**: `eyJhbGci...`（長い文字列）
3. Settings > API > JWT Settings を開く
4. **JWT Secret**をコピー

これらの値を`.env`ファイルに設定します（後述）。

---

## 📥 参照例データのインポート

### ローカル環境から実行

#### 1. 環境変数の設定

`.env`ファイルに以下を設定:

```bash
SUPABASE_URL=https://your-project-id.supabase.co
SUPABASE_ANON_KEY=eyJhbGci...（anon public キー）
```

#### 2. Pythonパッケージのインストール

```bash
# プロジェクトルートで実行
pip install supabase
```

または、仮想環境を使用している場合:

```bash
source .venv/bin/activate  # macOS/Linux
# または
.venv\Scripts\activate  # Windows

pip install supabase
```

#### 3. インポートスクリプトの実行

```bash
python scripts/import_references_to_supabase.py
```

**実行例**:
```
✓ Supabaseに接続しました: https://your-project-id.supabase.co
✓ /path/to/saiten/data/sample_comments.json を読み込みました（50件）
✓ 既存の参照例: 0件
  ✓ 挿入: prof_0001
  ✓ 挿入: prof_0002
  ...
============================================================
インポート完了
============================================================
  挿入: 50件
  スキップ: 0件
  エラー: 0件
  合計: 50件
============================================================

✅ すべてのデータが正常にインポートされました！
```

#### 4. データの確認

Supabase Dashboard > Table Editor > `knowledge_base`を開いて、データが正しくインポートされていることを確認します。

---

## 🚂 Railwayのセットアップ

### 1. プロジェクトの作成

1. [Railway Dashboard](https://railway.app/dashboard)にアクセス
2. 「New Project」をクリック
3. 「Deploy from GitHub repo」を選択
4. GitHubリポジトリを接続

### 2. 環境変数の設定

Railway Dashboard > プロジェクト > Variables タブで以下を設定:

```bash
# OpenAI API
OPENAI_API_KEY=sk-proj-...
USE_LLM=1
LLM_MODEL=gpt-4o-mini

# Supabase
SUPABASE_URL=https://your-project-id.supabase.co
SUPABASE_ANON_KEY=eyJhbGci...
SUPABASE_JWT_SECRET=your-jwt-secret

# データ暗号化
ENCRYPTION_KEY=your-32-byte-encryption-key

# 認証（本番環境では必ず0）
DISABLE_AUTH=0

# CORS（フロントエンドのURL）
ALLOWED_ORIGINS=https://your-frontend.vercel.app
```

**重要**:
- `DISABLE_AUTH=0`に設定してJWT認証を有効化
- `ALLOWED_ORIGINS`にフロントエンドのVercel URLを設定

### 3. デプロイ

環境変数を設定すると、自動的にデプロイが開始されます。

### 4. URLの確認

Railway Dashboard > Settings > Domains でデプロイされたURLを確認します。

例: `https://your-app.railway.app`

このURLをフロントエンドの`NEXT_PUBLIC_API_BASE_URL`に設定します。

---

## ✅ 動作確認

### 1. API の動作確認

ブラウザまたはcurlでアクセス:

```bash
curl https://your-app.railway.app/
```

**期待される結果**:
```json
{
  "message": "教授コメント自動化Bot API (MVP) is running",
  "version": "1.0.0",
  "docs_url": "/docs"
}
```

### 2. 参照例の読み込み確認

Railwayのログを確認:

```
Railway Dashboard > Deployments > 最新のデプロイ > View Logs
```

ログに以下のようなメッセージが表示されていれば成功:
- エラーなし
- 起動成功メッセージ

### 3. フロントエンドからの接続確認

1. フロントエンドで環境変数を設定:
   ```bash
   # frontend/.env.local
   NEXT_PUBLIC_API_BASE_URL=https://your-app.railway.app
   ```

2. フロントエンドを起動:
   ```bash
   cd frontend
   npm run dev
   ```

3. ブラウザで`http://localhost:3000`にアクセス
4. コメント生成をテスト

---

## 🔧 トラブルシューティング

### 問題1: "参照例の読み込みに失敗"エラー

**原因**: `knowledge_base`テーブルが存在しないか、データがインポートされていない

**解決方法**:
1. Supabaseでテーブルが作成されているか確認
2. データインポートスクリプトを再実行:
   ```bash
   python scripts/import_references_to_supabase.py
   ```

### 問題2: Railway でビルドが失敗する

**原因**: `requirements.txt`に必要なパッケージが含まれていない

**解決方法**:
1. `requirements.txt`を確認:
   ```bash
   cat requirements.txt
   ```
2. 必要なパッケージを追加:
   ```bash
   pip freeze > requirements.txt
   ```
3. Gitにコミット&プッシュ

### 問題3: CORS エラー

**原因**: `ALLOWED_ORIGINS`にフロントエンドのURLが含まれていない

**解決方法**:
1. Railway Dashboard > Variables
2. `ALLOWED_ORIGINS`にフロントエンドのVercel URLを追加:
   ```
   ALLOWED_ORIGINS=https://your-frontend.vercel.app
   ```
3. 再デプロイ

### 問題4: JWT検証エラー "Invalid token"

**原因**: `SUPABASE_JWT_SECRET`が正しく設定されていない

**解決方法**:
1. Supabase Dashboard > Settings > API > JWT Settings
2. JWT Secretをコピー
3. Railway Dashboard > Variables で`SUPABASE_JWT_SECRET`を更新
4. 再デプロイ

### 問題5: データベース接続エラー

**原因**: `SUPABASE_URL`または`SUPABASE_ANON_KEY`が正しくない

**解決方法**:
1. Supabase Dashboard > Settings > API
2. Project URLとanon publicキーを確認
3. Railway Dashboard > Variables で更新
4. 再デプロイ

---

## 📝 チェックリスト

### Supabase

- [ ] プロジェクトを作成
- [ ] データベーススキーマを適用（`database_schema.sql`）
- [ ] テーブルが作成されている（`reports`, `feedbacks`, `knowledge_base`）
- [ ] 参照例データをインポート（50件）
- [ ] 環境変数を取得（URL, anon key, JWT secret）

### Railway

- [ ] プロジェクトを作成
- [ ] 環境変数を設定
  - [ ] `OPENAI_API_KEY`
  - [ ] `SUPABASE_URL`
  - [ ] `SUPABASE_ANON_KEY`
  - [ ] `SUPABASE_JWT_SECRET`
  - [ ] `ENCRYPTION_KEY`
  - [ ] `DISABLE_AUTH=0`
  - [ ] `ALLOWED_ORIGINS`
- [ ] デプロイ成功
- [ ] URLを確認

### 動作確認

- [ ] API のルートエンドポイントにアクセス
- [ ] ログにエラーがない
- [ ] フロントエンドから接続できる
- [ ] コメント生成が正常に動作する

---

## 🔗 参考リンク

- [Supabase Documentation](https://supabase.com/docs)
- [Railway Documentation](https://docs.railway.app/)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)

---

**以上**

このガイドに従ってセットアップを完了すれば、RailwayとSupabaseでシステムが正常に動作します。
