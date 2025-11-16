# 認証ミドルウェアのセットアップ手順

## 概要
FastAPI backend に JWT 認証ミドルウェアを実装しました。Supabase の JWT トークンを使用してすべての保護されたエンドポイントで認証を行います。

## 実装内容

### 1. Backend (FastAPI)

#### 依存パッケージの追加
- `supabase>=2.0.0`
- `pyjwt>=2.8.0`

#### 認証ミドルウェア (`api/main.py`)
- `verify_jwt()` 関数: JWT トークンを検証し、ユーザー情報を返す
- エラーハンドリング:
  - 期限切れトークン: 401 Unauthorized
  - 無効なトークン: 401 Unauthorized
  - 認証失敗: 401 Unauthorized

#### 保護されたエンドポイント
以下のエンドポイントに JWT 認証を適用:
- `POST /generate` - コメント生成
- `POST /generate_direct` - 直接コメント生成
- `GET /references` - 参照例一覧取得
- `GET /references/{id}` - 参照例詳細取得
- `POST /references` - 参照例作成
- `PUT /references/{id}` - 参照例更新
- `DELETE /references/{id}` - 参照例削除
- `POST /references/import-csv` - CSV一括インポート

#### 非保護エンドポイント
- `GET /health` - ヘルスチェック

### 2. Frontend (Next.js)

#### 認証ヘルパー関数 (`lib/auth.ts`)
- `getAccessToken()`: Supabase セッションから JWT トークンを取得

#### API 呼び出しの更新
- `lib/api.ts`: `generateComment()` に Authorization ヘッダーを追加
- `lib/references.ts`: すべての参照例 API 呼び出しに Authorization ヘッダーを追加

## 環境変数の設定

### Backend (`.env`)
```bash
# Supabase
SUPABASE_URL=https://ovuseokcgawzqklushyj.supabase.co
SUPABASE_ANON_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
SUPABASE_JWT_SECRET=your-jwt-secret-here

# Authentication (開発時は1に設定してJWT検証を無効化、本番では0または削除)
DISABLE_AUTH=1
```

### JWT Secret の取得方法
1. Supabase ダッシュボードにアクセス
2. Settings > API > JWT Settings を開く
3. "JWT Secret" をコピーして `SUPABASE_JWT_SECRET` に設定

## 開発モード

開発時は `DISABLE_AUTH=1` を設定することで JWT 検証をスキップできます。
この場合、すべてのリクエストが `dev-user` として処理されます。

```bash
# 開発モード (JWT検証無効)
DISABLE_AUTH=1

# 本番モード (JWT検証有効)
DISABLE_AUTH=0
# または DISABLE_AUTH を削除
```

## 使用方法

### Frontend から API を呼び出す
認証が必要な API を呼び出す際、自動的に Authorization ヘッダーが付与されます:

```typescript
import { generateComment } from '@/lib/api'

// ログイン済みの場合、自動的に JWT トークンが送信される
const result = await generateComment(reportText, 'reflection')
```

### Backend で認証情報を取得する
エンドポイント内でユーザー情報にアクセスできます:

```python
@app.post("/generate_direct")
async def generate_direct(req: DirectGenRequest, user: dict = Depends(verify_jwt)):
    user_id = user["user_id"]
    email = user["email"]
    # ...
```

## トラブルシューティング

### 401 Unauthorized エラー
1. ユーザーがログインしているか確認
2. Supabase セッションが有効か確認
3. `SUPABASE_JWT_SECRET` が正しく設定されているか確認

### CORS エラー
- `api/main.py` の CORS 設定を確認
- `allow_credentials=True` が設定されているか確認

### トークンの期限切れ
- Supabase は自動的にトークンをリフレッシュします
- フロントエンドで `supabase.auth.getSession()` を使用することで最新のトークンを取得できます

## セキュリティ上の注意

1. **JWT Secret の管理**
   - `.env` ファイルを `.gitignore` に追加
   - 本番環境では環境変数として設定
   - JWT Secret を公開リポジトリにコミットしない

2. **開発モードの無効化**
   - 本番環境では必ず `DISABLE_AUTH=0` または削除
   - 開発モードのまま本番デプロイしないこと

3. **HTTPS の使用**
   - 本番環境では必ず HTTPS を使用
   - JWT トークンは平文で送信されるため、HTTPS が必須

## 次のステップ

- [ ] JWT Secret を Supabase ダッシュボードから取得して設定
- [ ] 本番環境での HTTPS 設定
- [ ] Rate limiting の実装
- [ ] ログ記録の実装
