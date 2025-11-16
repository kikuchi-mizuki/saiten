# 環境変数設定ガイド

**目的**: システムを正常に動作させるために必要な環境変数の設定方法を説明する
**対象**: 開発者、システム管理者
**最終更新**: 2025-11-16

---

## 📋 目次

1. [環境変数一覧](#環境変数一覧)
2. [フロントエンド設定](#フロントエンド設定)
3. [バックエンド設定](#バックエンド設定)
4. [セットアップ手順](#セットアップ手順)
5. [トラブルシューティング](#トラブルシューティング)

---

## 📝 環境変数一覧

### フロントエンド（Next.js）

| 環境変数 | 必須 | 説明 | 例 |
|---------|------|------|-----|
| `NEXT_PUBLIC_SUPABASE_URL` | ✅ | SupabaseプロジェクトのURL | `https://xxxxx.supabase.co` |
| `NEXT_PUBLIC_SUPABASE_ANON_KEY` | ✅ | Supabaseの匿名キー（公開キー） | `eyJhbGciOiJIUzI1...` |
| `NEXT_PUBLIC_API_BASE_URL` | ✅ | FastAPI バックエンドのURL | `http://localhost:8000` (開発)<br>`https://api.example.com` (本番) |

### バックエンド（FastAPI）

| 環境変数 | 必須 | 説明 | 例 |
|---------|------|------|-----|
| `SUPABASE_URL` | ✅ | SupabaseプロジェクトのURL | `https://xxxxx.supabase.co` |
| `SUPABASE_ANON_KEY` | ✅ | Supabaseの匿名キー | `eyJhbGciOiJIUzI1...` |
| `SUPABASE_JWT_SECRET` | ✅ | Supabase JWTの署名キー | `super-secret-jwt-token-with-at-least-32-characters-long` |
| `ENCRYPTION_KEY` | ✅ | データ暗号化用のキー（32文字以上推奨） | `your-encryption-key-here-32-chars-min` |
| `OPENAI_API_KEY` | ✅ | OpenAI APIキー | `sk-...` |
| `USE_LLM` | ✅ | LLM使用の有効化（1=有効, 0=無効） | `1` |
| `LLM_MODEL` | 推奨 | 使用するLLMモデル | `gpt-4o-mini` |
| `DISABLE_AUTH` | 開発用 | 認証を無効化（0=有効, 1=無効）<br>**本番では必ず0に設定** | `0` (本番)<br>`1` (開発) |
| `ALLOWED_ORIGINS` | 本番用 | CORS許可ドメイン（カンマ区切り） | `https://your-app.vercel.app,https://your-domain.com` |

---

## 🖥️ フロントエンド設定

### 1. .env.local ファイルの作成

フロントエンドディレクトリに `.env.local` ファイルを作成します。

```bash
cd frontend
cp .env.local.example .env.local
```

### 2. 環境変数の設定

`.env.local` ファイルを編集して、以下の内容を設定します。

#### 開発環境の例

```bash
# Supabase設定
NEXT_PUBLIC_SUPABASE_URL=https://xxxxx.supabase.co
NEXT_PUBLIC_SUPABASE_ANON_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Inh4eHh4Iiwicm9sZSI6ImFub24iLCJpYXQiOjE2Nzg4OTg0MDAsImV4cCI6MTk5NDQ3NDQwMH0.xxxxx

# API設定
NEXT_PUBLIC_API_BASE_URL=http://localhost:8000
```

#### 本番環境の例（Vercel）

Vercel のダッシュボードで環境変数を設定します。

```bash
NEXT_PUBLIC_SUPABASE_URL=https://xxxxx.supabase.co
NEXT_PUBLIC_SUPABASE_ANON_KEY=eyJhbGciOiJIUzI1...
NEXT_PUBLIC_API_BASE_URL=https://your-api-domain.com
```

### 3. Supabase URLとキーの取得方法

1. [Supabase Dashboard](https://supabase.com/dashboard)にログイン
2. プロジェクトを選択
3. 左サイドバーの「Settings」→「API」をクリック
4. 「Project URL」を`NEXT_PUBLIC_SUPABASE_URL`にコピー
5. 「Project API keys」の「anon public」を`NEXT_PUBLIC_SUPABASE_ANON_KEY`にコピー

---

## 🔧 バックエンド設定

### 1. .env ファイルの作成

プロジェクトルートディレクトリに `.env` ファイルを作成します。

```bash
cd /path/to/saiten
touch .env
```

### 2. 環境変数の設定

`.env` ファイルを編集して、以下の内容を設定します。

#### 開発環境の例

```bash
# Supabase設定
SUPABASE_URL=https://xxxxx.supabase.co
SUPABASE_ANON_KEY=eyJhbGciOiJIUzI1...
SUPABASE_JWT_SECRET=super-secret-jwt-token-with-at-least-32-characters-long

# データ暗号化設定
ENCRYPTION_KEY=your-encryption-key-here-32-chars-min

# OpenAI API設定
OPENAI_API_KEY=sk-...
USE_LLM=1
LLM_MODEL=gpt-4o-mini

# 開発モード設定
DISABLE_AUTH=1

# CORS設定（本番環境のドメインを追加する場合）
# ALLOWED_ORIGINS=https://your-app.vercel.app,https://your-domain.com
```

#### 本番環境の例

```bash
# Supabase設定
SUPABASE_URL=https://xxxxx.supabase.co
SUPABASE_ANON_KEY=eyJhbGciOiJIUzI1...
SUPABASE_JWT_SECRET=super-secret-jwt-token-with-at-least-32-characters-long

# データ暗号化設定
ENCRYPTION_KEY=your-secure-encryption-key-for-production-32-chars

# OpenAI API設定
OPENAI_API_KEY=sk-...
USE_LLM=1
LLM_MODEL=gpt-4o-mini

# 本番モード設定（認証を有効化）
DISABLE_AUTH=0

# CORS設定（本番環境のドメイン）
ALLOWED_ORIGINS=https://your-app.vercel.app,https://your-domain.com
```

### 3. 各環境変数の取得方法

#### SUPABASE_URL / SUPABASE_ANON_KEY
- フロントエンドと同じ手順で取得

#### SUPABASE_JWT_SECRET
1. [Supabase Dashboard](https://supabase.com/dashboard)にログイン
2. プロジェクトを選択
3. 左サイドバーの「Settings」→「API」をクリック
4. 「JWT Settings」セクションの「JWT Secret」をコピー

#### ENCRYPTION_KEY
以下のコマンドで安全なキーを生成できます：

```bash
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

**重要**:
- 生成したキーは安全に保管してください
- 本番環境と開発環境で異なるキーを使用してください
- キーが漏洩した場合は、すぐに再生成して更新してください

#### OPENAI_API_KEY
1. [OpenAI Platform](https://platform.openai.com/)にログイン
2. 右上のアカウントアイコンをクリック→「View API keys」
3. 「Create new secret key」をクリック
4. 生成されたキーをコピー（一度しか表示されないので注意）

#### ALLOWED_ORIGINS
本番環境のフロントエンドURLを設定します。複数ある場合はカンマ区切りで指定します。

例:
```bash
ALLOWED_ORIGINS=https://your-app.vercel.app,https://www.your-domain.com
```

---

## 📦 セットアップ手順

### 開発環境のセットアップ（ローカル）

#### 1. フロントエンドの設定

```bash
# フロントエンドディレクトリに移動
cd frontend

# .env.localファイルを作成
cp .env.local.example .env.local

# .env.localを編集（上記の「開発環境の例」を参照）
nano .env.local

# 依存パッケージをインストール
npm install

# 開発サーバーを起動
npm run dev
```

#### 2. バックエンドの設定

```bash
# プロジェクトルートディレクトリに移動
cd /path/to/saiten

# .envファイルを作成
touch .env

# .envを編集（上記の「開発環境の例」を参照）
nano .env

# 暗号化キーを生成
python -c "import secrets; print(secrets.token_urlsafe(32))"
# 生成されたキーを.envのENCRYPTION_KEYに設定

# 依存パッケージをインストール
pip install -r requirements.txt

# 開発サーバーを起動
uvicorn api.main:app --reload --host 0.0.0.0 --port 8000
```

### 本番環境のセットアップ

#### 1. Vercel（フロントエンド）

1. Vercelダッシュボードでプロジェクトを選択
2. 「Settings」→「Environment Variables」をクリック
3. 以下の環境変数を追加:
   - `NEXT_PUBLIC_SUPABASE_URL`
   - `NEXT_PUBLIC_SUPABASE_ANON_KEY`
   - `NEXT_PUBLIC_API_BASE_URL`
4. 「Save」をクリック
5. プロジェクトを再デプロイ

#### 2. バックエンドのデプロイ先（Railway / Render / Heroku など）

デプロイ先のダッシュボードで環境変数を設定します。

**必須環境変数**:
- `SUPABASE_URL`
- `SUPABASE_ANON_KEY`
- `SUPABASE_JWT_SECRET`
- `ENCRYPTION_KEY`
- `OPENAI_API_KEY`
- `USE_LLM=1`
- `LLM_MODEL=gpt-4o-mini`
- `DISABLE_AUTH=0` ← **本番では必ず0に設定**
- `ALLOWED_ORIGINS` ← VercelのURLを設定

---

## 🔍 トラブルシューティング

### 問題1: "Supabase is not configured"エラー

**原因**: Supabase関連の環境変数が未設定、または不正

**解決方法**:
1. `.env`ファイルに以下が設定されているか確認
   - `SUPABASE_URL`
   - `SUPABASE_ANON_KEY`
   - `SUPABASE_JWT_SECRET`
2. 値が正しいか確認（Supabaseダッシュボードと照合）
3. サーバーを再起動

### 問題2: "Encryption is not configured"エラー

**原因**: `ENCRYPTION_KEY`が未設定

**解決方法**:
1. 暗号化キーを生成:
   ```bash
   python -c "import secrets; print(secrets.token_urlsafe(32))"
   ```
2. `.env`ファイルに`ENCRYPTION_KEY`を追加
3. サーバーを再起動

### 問題3: "OpenAI API timeout"エラー

**原因**: OpenAI APIキーが無効、またはネットワーク接続の問題

**解決方法**:
1. APIキーが正しいか確認
2. OpenAIダッシュボードでAPIキーが有効か確認
3. API利用制限に達していないか確認
4. ネットワーク接続を確認

### 問題4: CORSエラー（本番環境）

**原因**: フロントエンドのドメインがCORS許可リストに含まれていない

**解決方法**:
1. `.env`に`ALLOWED_ORIGINS`を追加:
   ```bash
   ALLOWED_ORIGINS=https://your-app.vercel.app
   ```
2. サーバーを再起動
3. ブラウザのキャッシュをクリア

### 問題5: "Invalid token"エラー

**原因**: JWTの検証に失敗

**解決方法**:
1. `SUPABASE_JWT_SECRET`が正しいか確認（Supabaseダッシュボードと照合）
2. ログアウトして再度ログイン
3. ブラウザのキャッシュをクリア

---

## ✅ 設定チェックリスト

### フロントエンド
- [ ] `NEXT_PUBLIC_SUPABASE_URL`が設定されている
- [ ] `NEXT_PUBLIC_SUPABASE_ANON_KEY`が設定されている
- [ ] `NEXT_PUBLIC_API_BASE_URL`が設定されている
- [ ] `npm run dev`でエラーなく起動する

### バックエンド
- [ ] `SUPABASE_URL`が設定されている
- [ ] `SUPABASE_ANON_KEY`が設定されている
- [ ] `SUPABASE_JWT_SECRET`が設定されている
- [ ] `ENCRYPTION_KEY`が設定されている（32文字以上）
- [ ] `OPENAI_API_KEY`が設定されている
- [ ] `USE_LLM=1`が設定されている
- [ ] `DISABLE_AUTH=0`（本番）または`DISABLE_AUTH=1`（開発）が設定されている
- [ ] `ALLOWED_ORIGINS`が設定されている（本番環境のみ）
- [ ] `uvicorn api.main:app --reload`でエラーなく起動する

### 動作確認
- [ ] Google OAuth認証が動作する
- [ ] コメント生成が動作する
- [ ] 履歴保存・取得が動作する
- [ ] エラーが発生しない

---

## 📞 サポート

環境設定で問題が発生した場合:
1. まずトラブルシューティングを確認
2. エラーメッセージを記録
3. 開発者に連絡（エラーメッセージを添付）

---

**以上**
