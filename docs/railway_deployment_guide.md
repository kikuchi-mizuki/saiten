# Railway デプロイガイド

**目的**: FastAPI バックエンドを Railway にデプロイする手順
**対象**: 開発者、システム管理者
**最終更新**: 2025-11-16

---

## 📋 目次

1. [Railwayとは](#railwayとは)
2. [デプロイ前の準備](#デプロイ前の準備)
3. [Railwayでのデプロイ手順](#railwayでのデプロイ手順)
4. [環境変数の設定](#環境変数の設定)
5. [デプロイ後の確認](#デプロイ後の確認)
6. [トラブルシューティング](#トラブルシューティング)

---

## 🚂 Railwayとは

Railwayは、GitHubリポジトリと連携して自動デプロイできるPaaS（Platform as a Service）です。

**特徴**:
- GitHubとの自動連携
- 無料プランあり（月500時間まで）
- 環境変数の管理が簡単
- 自動HTTPS対応
- ログ確認が容易

---

## 📝 デプロイ前の準備

### 1. 必要なファイルの確認

以下のファイルがリポジトリに含まれていることを確認してください：

- ✅ `Procfile` - 起動コマンドを定義
  ```
  web: uvicorn api.main:app --host 0.0.0.0 --port $PORT
  ```

- ✅ `requirements.txt` - Python依存パッケージ
  ```
  fastapi>=0.104.0
  uvicorn[standard]>=0.24.0
  pydantic>=2.0.0
  requests>=2.31.0
  supabase>=2.0.0
  pyjwt>=2.8.0
  cryptography>=41.0.0
  ```

### 2. GitHubリポジトリ

- ✅ GitHubリポジトリが公開されている
  - リポジトリURL: `https://github.com/kikuchi-mizuki/saiten.git`

### 3. 環境変数の準備

以下の環境変数を事前に準備してください：

| 環境変数 | 説明 | 取得方法 |
|---------|------|---------|
| `SUPABASE_URL` | SupabaseプロジェクトのURL | Supabase Dashboard > Settings > API |
| `SUPABASE_ANON_KEY` | Supabaseの匿名キー | Supabase Dashboard > Settings > API |
| `SUPABASE_JWT_SECRET` | Supabase JWTの署名キー | Supabase Dashboard > Settings > API > JWT Secret |
| `ENCRYPTION_KEY` | データ暗号化用のキー | `python -c "import secrets; print(secrets.token_urlsafe(32))"` |
| `OPENAI_API_KEY` | OpenAI APIキー | OpenAI Platform |
| `USE_LLM` | LLM使用の有効化 | `1` |
| `LLM_MODEL` | 使用するLLMモデル | `gpt-4o-mini` |
| `DISABLE_AUTH` | 認証を無効化 | `0`（本番では必ず0） |
| `ALLOWED_ORIGINS` | CORS許可ドメイン | VercelのフロントエンドURL |

---

## 🚀 Railwayでのデプロイ手順

### ステップ1: Railwayアカウントの作成

1. [Railway](https://railway.app/)にアクセス
2. 「Login」をクリック
3. GitHubアカウントでログイン
4. Railwayへのアクセスを許可

### ステップ2: 新しいプロジェクトの作成

1. Railwayダッシュボードで「New Project」をクリック
2. 「Deploy from GitHub repo」を選択
3. GitHubリポジトリの接続を許可（初回のみ）
4. `kikuchi-mizuki/saiten`リポジトリを選択

### ステップ3: サービスの設定

1. Railwayが自動的にプロジェクトを検出します
   - Python/FastAPIプロジェクトとして認識されます
   - `Procfile`に基づいて起動コマンドが設定されます

2. 「Deploy」ボタンをクリック
   - 初回デプロイが開始されます
   - ビルドログが表示されます

### ステップ4: 環境変数の設定

1. プロジェクトダッシュボードで「Variables」タブをクリック

2. 以下の環境変数を追加:

   **Supabase設定**:
   ```
   SUPABASE_URL=https://xxxxx.supabase.co
   SUPABASE_ANON_KEY=eyJhbGciOiJIUzI1...
   SUPABASE_JWT_SECRET=super-secret-jwt-token-with-at-least-32-characters-long
   ```

   **暗号化設定**:
   ```
   ENCRYPTION_KEY=your-secure-encryption-key-for-production-32-chars
   ```

   **OpenAI設定**:
   ```
   OPENAI_API_KEY=sk-...
   USE_LLM=1
   LLM_MODEL=gpt-4o-mini
   ```

   **認証設定**:
   ```
   DISABLE_AUTH=0
   ```

   **CORS設定**:
   ```
   ALLOWED_ORIGINS=https://your-app.vercel.app
   ```

3. 「Add」をクリックして各環境変数を保存

### ステップ5: 再デプロイ

環境変数を追加した後、自動的に再デプロイされます。
手動で再デプロイする場合は、「Deployments」タブから「Redeploy」をクリックしてください。

---

## 🌐 デプロイ後の確認

### 1. デプロイURLの取得

1. プロジェクトダッシュボードで「Settings」タブをクリック
2. 「Domains」セクションで「Generate Domain」をクリック
3. 生成されたURL（例: `https://saiten-production.up.railway.app`）をコピー

### 2. APIの動作確認

ブラウザまたはcURLでAPIの動作を確認します：

```bash
# ヘルスチェック
curl https://your-app.railway.app/health

# 期待される出力
{"ok":true}
```

### 3. ログの確認

1. プロジェクトダッシュボードで「Deployments」タブをクリック
2. 最新のデプロイメントをクリック
3. ログが表示されます
   - 起動ログ: `uvicorn api.main:app --host 0.0.0.0 --port $PORT`
   - エラーがないか確認

### 4. フロントエンドの環境変数を更新

Vercelのフロントエンドで、APIのURLを更新します：

```bash
NEXT_PUBLIC_API_BASE_URL=https://your-app.railway.app
```

Vercelで環境変数を更新した後、再デプロイしてください。

---

## 🔧 トラブルシューティング

### 問題1: デプロイが失敗する

**症状**: デプロイが失敗し、エラーメッセージが表示される

**原因と解決方法**:

1. **Procfileが見つからない**
   - `Procfile`がリポジトリのルートに存在するか確認
   - ファイル名が正確に`Procfile`であるか確認（大文字小文字を区別）

2. **依存パッケージのインストールエラー**
   - `requirements.txt`が正しいか確認
   - ログで具体的なエラーメッセージを確認

3. **Python バージョンの問題**
   - `runtime.txt`を追加して、Pythonバージョンを指定
   ```
   python-3.11
   ```

### 問題2: 環境変数が反映されない

**症状**: 環境変数を設定したのに、アプリケーションで使用できない

**解決方法**:
1. Railwayダッシュボードで「Variables」タブを確認
2. 環境変数が正しく設定されているか確認
3. 環境変数を変更した後、再デプロイを実行

### 問題3: CORS エラー

**症状**: フロントエンドからAPIにアクセスすると CORS エラーが発生

**解決方法**:
1. `ALLOWED_ORIGINS`環境変数にフロントエンドのURLを追加
   ```
   ALLOWED_ORIGINS=https://your-app.vercel.app
   ```
2. 複数のドメインを許可する場合はカンマ区切り
   ```
   ALLOWED_ORIGINS=https://your-app.vercel.app,https://www.your-domain.com
   ```
3. 再デプロイ

### 問題4: "Invalid token"エラー

**症状**: 認証時に"Invalid token"エラーが発生

**解決方法**:
1. `SUPABASE_JWT_SECRET`が正しいか確認
   - Supabase Dashboard > Settings > API > JWT Secret
2. フロントエンドとバックエンドで同じSupabaseプロジェクトを使用しているか確認
3. 再デプロイ

### 問題5: OpenAI APIエラー

**症状**: コメント生成時にOpenAI APIエラーが発生

**解決方法**:
1. `OPENAI_API_KEY`が正しいか確認
2. `USE_LLM=1`が設定されているか確認
3. OpenAIダッシュボードでAPIキーが有効か確認
4. API利用制限に達していないか確認

---

## 📊 Railway の料金プラン

### Hobby Plan（無料）
- 月500時間まで無料
- $5相当のクレジット付与（超過分に使用可能）
- メモリ: 512MB
- CPU: 共有
- 十分な性能（Phase 1 MVP）

### Pro Plan（有料）
- $20/月
- より高いリソース
- Phase 2以降で検討

---

## ✅ デプロイ完了チェックリスト

- [ ] `Procfile`がリポジトリに存在する
- [ ] `requirements.txt`が最新である
- [ ] GitHubリポジトリがRailwayと連携されている
- [ ] すべての環境変数が設定されている
- [ ] デプロイが成功している
- [ ] `/health`エンドポイントが正常に応答する
- [ ] フロントエンドの`NEXT_PUBLIC_API_BASE_URL`が更新されている
- [ ] フロントエンドからAPIにアクセスできる
- [ ] 認証が動作する
- [ ] コメント生成が動作する

---

## 📞 サポート

デプロイで問題が発生した場合:
1. Railwayのログを確認
2. エラーメッセージをコピー
3. 開発者に連絡（エラーメッセージを添付）

---

**以上**

Railway へのデプロイが完了すれば、FastAPI バックエンドが本番環境で動作します。
