# 本番環境セットアップガイド

**最終更新**: 2026-01-12

このドキュメントは、教授コメント自動化ボットを本番環境（Railway）にデプロイする際の設定手順を説明します。

---

## 🚨 重要な注意事項

### セキュリティ上の必須対応

1. **APIキーは絶対にGitにコミットしない**
   - `.env`ファイルは`.gitignore`で除外されています
   - 本番環境のAPIキーはRailwayの環境変数で設定してください

2. **本番環境では認証を有効化する**
   - `DISABLE_AUTH=0`に設定（開発環境のみ`1`）

3. **暗号化キーは必ず新規生成する**
   - 開発環境のキーを本番環境で使用しないでください

---

## 📋 本番環境への環境変数設定

### Railway環境変数の設定手順

Railway Dashboard > プロジェクト > Variables で以下の環境変数を設定してください。

---

### 🔑 必須環境変数

#### 1. OpenAI API設定

```bash
OPENAI_API_KEY=sk-proj-xxxxxxxxxxxxxxxxxxxxx
USE_LLM=1
LLM_MODEL=gpt-4o-mini
```

**取得方法**:
1. [OpenAI Platform](https://platform.openai.com/)にログイン
2. API Keys > Create new secret key
3. 生成されたキーをコピー（一度しか表示されません）

---

#### 2. Supabase設定

```bash
# フロントエンド用（NEXT_PUBLIC_接頭辞が必要）
NEXT_PUBLIC_SUPABASE_URL=https://your-project.supabase.co
NEXT_PUBLIC_SUPABASE_ANON_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...

# バックエンド用
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_ANON_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
SUPABASE_JWT_SECRET=your-jwt-secret-here
```

**取得方法**:
1. [Supabase Dashboard](https://supabase.com/dashboard)にログイン
2. プロジェクトを選択
3. Settings > API で以下を取得:
   - `URL`: Project URL
   - `ANON_KEY`: Project API keys > anon public
   - `JWT_SECRET`: Project API keys > JWT Settings > JWT Secret

**⚠️ 重要**: `SUPABASE_JWT_SECRET`は必ず設定してください。これがないとJWT認証が機能しません。

---

#### 3. データ暗号化設定

```bash
ENCRYPTION_KEY=新しく生成した32バイトキー
```

**生成方法**:
```bash
python3 -c "import secrets; print(secrets.token_urlsafe(32))"
```

**例**:
```bash
ENCRYPTION_KEY=7OTQRvtS7gQYr76HmLcZjyL9PE6LizumDZgZhYF3o6U
```

**⚠️ 重要**:
- 開発環境のキーを本番環境で使用しないでください
- このキーが漏洩すると、暗号化されたデータが解読される可能性があります
- キーを変更するとこれまでに暗号化したデータが復号できなくなります

---

#### 4. 認証設定

```bash
DISABLE_AUTH=0
```

**⚠️ 重要**: 本番環境では必ず`0`（認証有効）に設定してください。

---

#### 5. CORS設定

```bash
ALLOWED_ORIGINS=https://your-frontend-url.up.railway.app
```

**設定例**:
```bash
ALLOWED_ORIGINS=https://trustworthy-benevolence-production.up.railway.app
```

**複数ドメインの場合**（カンマ区切り）:
```bash
ALLOWED_ORIGINS=https://app1.railway.app,https://app2.railway.app,https://custom-domain.com
```

---

### 📊 オプション環境変数（Phase 2）

```bash
# Embedding設定
EMBEDDING_MODEL=text-embedding-3-small
EMBEDDING_DIMENSIONS=1536
```

---

## 🔍 設定確認チェックリスト

デプロイ前に以下を確認してください：

### バックエンド（API）

- [ ] `OPENAI_API_KEY`が設定されている（`sk-proj-`で始まる）
- [ ] `SUPABASE_URL`が設定されている（`https://`で始まる）
- [ ] `SUPABASE_ANON_KEY`が設定されている（`eyJ`で始まる）
- [ ] `SUPABASE_JWT_SECRET`が設定されている（空でない）
- [ ] `ENCRYPTION_KEY`が新規生成されている（32バイト以上）
- [ ] `DISABLE_AUTH=0`に設定されている
- [ ] `ALLOWED_ORIGINS`にフロントエンドURLが設定されている

### フロントエンド

- [ ] `NEXT_PUBLIC_SUPABASE_URL`が設定されている
- [ ] `NEXT_PUBLIC_SUPABASE_ANON_KEY`が設定されている
- [ ] `NEXT_PUBLIC_API_BASE_URL`がバックエンドURLを指している

---

## 🚀 デプロイ手順

### 1. 環境変数の設定

Railwayで上記の環境変数をすべて設定します。

### 2. デプロイ

```bash
git add .
git commit -m "fix: セキュリティ強化 - 環境変数の適切な設定とデバッグログの削除"
git push
```

### 3. 動作確認

1. **ヘルスチェック**
   ```
   https://your-backend-url.railway.app/health
   ```
   → `{"ok": true}`が返ればOK

2. **フロントエンドにアクセス**
   ```
   https://your-frontend-url.railway.app
   ```

3. **ログイン機能の確認**
   - Google OAuth認証が正常に動作するか確認

4. **API通信の確認**
   - レポート生成が正常に動作するか確認

---

## 🔒 セキュリティベストプラクティス

### APIキーのローテーション（推奨）

3ヶ月ごとに以下のキーをローテーションすることを推奨します：

1. **OpenAI APIキー**
   - OpenAI Platformで新しいキーを生成
   - Railwayで環境変数を更新
   - 古いキーを削除

2. **暗号化キー**
   - ⚠️ 注意: 暗号化キーを変更すると過去のデータが復号できなくなります
   - データ移行が必要な場合は別途計画が必要

### 監視とログ

- Railwayのログを定期的に確認
- エラーログに機密情報が含まれていないか確認
- 異常なアクセスパターンがないか監視

---

## 🛠 トラブルシューティング

### 問題1: JWT認証エラー

**症状**: `401 Unauthorized` エラーが発生

**解決方法**:
1. `SUPABASE_JWT_SECRET`が正しく設定されているか確認
2. Supabase Dashboard > Settings > API > JWT Settings から正しい値を取得
3. 環境変数を更新後、Railwayでデプロイを再実行

### 問題2: CORS エラー

**症状**: ブラウザコンソールに `CORS policy` エラー

**解決方法**:
1. `ALLOWED_ORIGINS`にフロントエンドURLが含まれているか確認
2. カンマ区切りで複数URLを設定している場合、スペースが入っていないか確認
3. `https://`プロトコルが含まれているか確認

### 問題3: 暗号化・復号化エラー

**症状**: `Decryption failed` エラー

**解決方法**:
1. `ENCRYPTION_KEY`が正しく設定されているか確認
2. キーが32バイト以上であることを確認
3. 開発環境と本番環境で異なるキーを使用していないか確認

---

## 📞 サポート

問題が解決しない場合は、以下の情報を含めて報告してください：

- エラーメッセージの全文
- 発生したタイミング
- 設定した環境変数の一覧（値は伏せて）
- Railwayのログ

---

## 🔄 定期メンテナンス

### 月次

- [ ] Railwayのログを確認
- [ ] エラー率を確認
- [ ] ディスク使用量を確認

### 四半期

- [ ] APIキーのローテーション
- [ ] 依存パッケージのアップデート
- [ ] セキュリティ監査

---

**最終確認日**: 2026-01-12
**担当者**: Claude
**バージョン**: 1.0
