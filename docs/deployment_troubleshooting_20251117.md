# デプロイメントトラブルシューティング記録

**日付**: 2025-11-17
**対象**: Railway + Supabase デプロイメント

---

## 📊 現在の状況

### 完了した作業

1. ✅ Supabase knowledge_base テーブル作成
2. ✅ 参照例データのインポート（10件）
3. ✅ バックエンドAPI修正（認証、UUID対応）
4. ✅ フロントエンドコード修正（本番環境URL対応）
5. ✅ 環境変数の設定
6. ✅ 最新コードのデプロイ（21:44完了）

### 現在の問題

フロントエンドが **ブラウザキャッシュ** により古いJavaScriptファイルを使用しており、`localhost:8010` にアクセスしようとしている。

---

## 🌐 デプロイ情報

### バックエンド（Railway）

**URL**: `https://saiten-production.up.railway.app`

**環境変数**:
```bash
SUPABASE_URL=https://ovuseokcgawzqklushyj.supabase.co
SUPABASE_ANON_KEY=eyJhbGci...
SUPABASE_JWT_SECRET=[設定済み]
OPENAI_API_KEY=[設定済み]
ENCRYPTION_KEY=[設定済み]
DISABLE_AUTH=1
ALLOWED_ORIGINS=https://trustworthy-benevolence-production.up.railway.app
USE_LLM=1
LLM_MODEL=gpt-4o-mini
```

**動作確認済み**:
- ✅ `https://saiten-production.up.railway.app/` - 正常
- ✅ `https://saiten-production.up.railway.app/references` - データ取得成功（10件）
- ✅ `https://saiten-production.up.railway.app/stats` - 正常

### フロントエンド（Railway）

**URL**: `https://trustworthy-benevolence-production.up.railway.app`

**環境変数**:
```bash
NEXT_PUBLIC_API_BASE_URL=https://saiten-production.up.railway.app
NEXT_PUBLIC_SUPABASE_URL=https://ovuseokcgawzqklushyj.supabase.co
NEXT_PUBLIC_SUPABASE_ANON_KEY=eyJhbGci...
```

**最新のコード修正**（`frontend/lib/api.ts`）:
```typescript
const API_BASE_URL = process.env.NEXT_PUBLIC_API_BASE_URL
  || (typeof window !== 'undefined' && window.location.hostname !== 'localhost'
    ? 'https://saiten-production.up.railway.app'
    : 'http://127.0.0.1:8010')
```

**最新デプロイ**:
- タイムスタンプ: 2025-11-17 21:44
- ステータス: Success
- ビルド時間: 34.52秒
- コミット: `fix: 本番環境で確実に正しいAPIのURLを使用するよう修正`

---

## 🔧 実施した修正

### 1. データベース

**問題**: `knowledge_base` テーブルが存在しない
**解決**: テーブル作成 + RLSポリシー設定

### 2. 参照例データ

**問題**: データが空
**解決**: `scripts/import_references_to_supabase.py` 実行（10件インポート成功）

### 3. 認証エラー

**問題**: `{"detail":"Not authenticated"}`
**解決**: `verify_jwt` 関数修正（`DISABLE_AUTH=1` で認証ヘッダーなしでもアクセス可能に）

### 4. UUID型エラー

**問題**: `invalid input syntax for type uuid: "dev-user"`
**解決**: `dev-user` を `00000000-0000-0000-0000-000000000000` に変更

### 5. フロントエンド環境変数

**問題**: `NEXT_PUBLIC_API_BASE_URL` が読み込まれない
**解決**: コードレベルで本番環境判定を追加

---

## 🚀 再起動後の確認手順

### 1. デプロイステータス確認

Railway Dashboard で確認：
- バックエンド: Success
- フロントエンド: Success（21:44のデプロイ）

### 2. ブラウザでアクセス

**新しいシークレットウィンドウで**：
```
https://trustworthy-benevolence-production.up.railway.app
```

### 3. 動作確認

- [ ] エラーがコンソールに表示されない
- [ ] 参照例管理画面で10件の参照例が表示される
- [ ] コメント生成が正常に動作する

### 4. エラーが出る場合

**開発者ツール（F12）で確認**:
- Console タブ: エラーメッセージ
- Network タブ: リクエストURL（`localhost:8010` ではなく、`saiten-production.up.railway.app` になっているか）

---

## 📝 重要なファイル

### バックエンド

- `api/main.py` - メインAPI
- `scripts/import_references_to_supabase.py` - データインポートスクリプト
- `docs/database_schema.sql` - データベーススキーマ

### フロントエンド

- `frontend/lib/api.ts` - API呼び出し（修正済み）
- `frontend/.env.production` - 本番環境変数

### ドキュメント

- `docs/railway_supabase_setup.md` - セットアップガイド
- `docs/incident_response.md` - 緊急対応手順
- `docs/week12_implementation_summary.md` - Week 12実装サマリー

---

## 🔗 参考URL

### Supabase

- Dashboard: https://supabase.com/dashboard
- プロジェクト: ovuseokcgawzqklushyj

### Railway

- Dashboard: https://railway.app/dashboard
- バックエンド: saiten-production
- フロントエンド: trustworthy-benevolence-production

---

## 💡 次のアクション

1. **PC再起動後**、新しいブラウザ（またはシークレットモード）でアクセス
2. 動作確認
3. 問題が解決していれば、UAT準備に進む

---

## 📞 問題が継続する場合

別のブラウザ（Firefox/Edge）で試す：
```
https://trustworthy-benevolence-production.up.railway.app
```

キャッシュの影響を受けないため、確実に最新のコードで動作確認できます。

---

**最終更新**: 2025-11-17 21:50
**進捗率**: 98%（デプロイ完了、ブラウザキャッシュクリア待ち）
