# 緊急対応手順書

**作成日**: 2025-11-17
**対象**: Phase 1 MVP
**目的**: セキュリティインシデント発生時の対応手順を定義

---

## 📋 目次

1. [緊急連絡先](#緊急連絡先)
2. [インシデント分類](#インシデント分類)
3. [暗号化キー漏洩時の対応](#暗号化キー漏洩時の対応)
4. [データベース侵害時の対応](#データベース侵害時の対応)
5. [OpenAI APIキー漏洩時の対応](#openai-apiキー漏洩時の対応)
6. [システム障害時の対応](#システム障害時の対応)
7. [記録と報告](#記録と報告)

---

## 📞 緊急連絡先

### 開発責任者
- **氏名**: [担当者名]
- **メール**: [メールアドレス]
- **電話**: [電話番号]

### サービスプロバイダー
- **Supabase Support**: https://supabase.com/support
- **Vercel Support**: https://vercel.com/support
- **OpenAI Support**: https://help.openai.com/

---

## 🚨 インシデント分類

### レベル1（Critical）- 即座の対応が必要
- 暗号化キーの漏洩
- データベースへの不正アクセス
- OpenAI APIキーの不正使用
- 大規模なデータ漏洩

### レベル2（High）- 24時間以内の対応が必要
- 認証システムの障害
- データベースのパフォーマンス低下
- OpenAI APIの使用量異常

### レベル3（Medium）- 48時間以内の対応が必要
- フロントエンドの部分的な障害
- バックエンドAPIの一部エンドポイント障害
- ログ記録の不具合

---

## 🔐 暗号化キー漏洩時の対応

### 概要
`ENCRYPTION_KEY`環境変数が漏洩した場合の対応手順

### 緊急度
**レベル1（Critical）** - 即座の対応が必要

### 対応手順

#### 1. 漏洩の確認（5分以内）
- [ ] 漏洩の範囲を特定（GitHub、ログ、エラーメッセージ等）
- [ ] 漏洩した鍵が現在使用中のものか確認
- [ ] 影響範囲を評価（暗号化されたデータの件数）

#### 2. 即時対応（30分以内）
1. **新しい暗号化キーの生成**
   ```bash
   python -c "import secrets; print(secrets.token_urlsafe(32))"
   ```

2. **環境変数の更新**
   - 本番環境（Vercel/Railway）:
     - Dashboard > Settings > Environment Variables
     - `ENCRYPTION_KEY`を新しい値に更新
     - アプリを再デプロイ

3. **漏洩した鍵の無効化**
   - 古い鍵を記録
   - 古い鍵での暗号化データの特定

#### 3. データ復旧（1-2時間以内）
1. **暗号化データの再暗号化**

   以下のスクリプトを実行:
   ```python
   # scripts/re_encrypt_data.py
   from api.main import DataEncryption
   from supabase import create_client
   import os

   # 旧キーと新キーを設定
   OLD_KEY = "old-encryption-key"
   NEW_KEY = os.environ.get("ENCRYPTION_KEY")

   old_encryptor = DataEncryption(OLD_KEY)
   new_encryptor = DataEncryption(NEW_KEY)

   # Supabase接続
   supabase = create_client(
       os.environ.get("SUPABASE_URL"),
       os.environ.get("SUPABASE_ANON_KEY")
   )

   # 全レコードを取得
   response = supabase.table("feedbacks").select("id, report_text_encrypted").execute()

   for record in response.data:
       try:
           # 旧キーで復号化
           decrypted = old_encryptor.decrypt(record["report_text_encrypted"])

           # 新キーで再暗号化
           re_encrypted = new_encryptor.encrypt(decrypted)

           # データベース更新
           supabase.table("feedbacks").update({
               "report_text_encrypted": re_encrypted
           }).eq("id", record["id"]).execute()

           print(f"Re-encrypted record {record['id']}")
       except Exception as e:
           print(f"Error re-encrypting {record['id']}: {e}")
   ```

2. **実行**
   ```bash
   python scripts/re_encrypt_data.py
   ```

#### 4. 検証（30分以内）
- [ ] 新しい鍵でデータが正常に復号化できることを確認
- [ ] アプリケーションの動作確認
- [ ] ログに異常がないことを確認

#### 5. 報告（24時間以内）
- [ ] インシデントレポートの作成
- [ ] 教授への報告
- [ ] 再発防止策の策定

### 再発防止策
1. `.env`ファイルを`.gitignore`に追加（確認）
2. GitHub Secretsの使用を検討
3. 定期的な鍵ローテーション（3ヶ月毎）の実施
4. 鍵管理をSupabase Vaultに移行（Phase 2-A）

---

## 🗄️ データベース侵害時の対応

### 概要
Supabaseデータベースへの不正アクセスが疑われる場合の対応手順

### 緊急度
**レベル1（Critical）** - 即座の対応が必要

### 対応手順

#### 1. 侵害の確認（5分以内）
- [ ] Supabase Dashboard > Logs で異常なアクセスを確認
- [ ] 不正なクエリの有無を確認
- [ ] データの改ざん・削除の有無を確認

#### 2. 即時対応（15分以内）
1. **アクセス制限**
   - Supabase Dashboard > Settings > API
   - 必要に応じてAPIキーを再生成
   - CORS設定を確認・更新

2. **不正アクセスのブロック**
   - IPアドレス制限の追加（可能な場合）
   - RLS（Row Level Security）ポリシーの確認

3. **システムの一時停止**（必要な場合）
   - Vercelでアプリを一時停止
   - 「メンテナンス中」ページを表示

#### 3. データ調査（1-2時間以内）
1. **影響範囲の特定**
   ```sql
   -- 最近の更新・削除を確認
   SELECT * FROM feedbacks
   WHERE updated_at > NOW() - INTERVAL '24 hours'
   ORDER BY updated_at DESC;
   ```

2. **バックアップからの復旧**
   - Supabase Dashboard > Database > Backups
   - 必要に応じてポイントインタイムリカバリを実行

#### 4. セキュリティ強化（24時間以内）
- [ ] RLSポリシーの見直し
- [ ] JWT検証の強化（`DISABLE_AUTH=0`の確認）
- [ ] アクセスログの監視強化

#### 5. 報告（24時間以内）
- [ ] インシデントレポートの作成
- [ ] 影響を受けたユーザーへの通知（該当する場合）
- [ ] 教授への報告

---

## 🔑 OpenAI APIキー漏洩時の対応

### 概要
`OPENAI_API_KEY`が漏洩した場合の対応手順

### 緊急度
**レベル1（Critical）** - 即座の対応が必要

### 対応手順

#### 1. 漏洩の確認（5分以内）
- [ ] OpenAI Dashboard > Usage で異常な使用量を確認
- [ ] 漏洩の範囲を特定（GitHub、ログ等）

#### 2. 即時対応（15分以内）
1. **APIキーの無効化**
   - OpenAI Dashboard: https://platform.openai.com/api-keys
   - 漏洩したキーを「Revoke」

2. **新しいAPIキーの生成**
   - 新しいAPIキーを生成
   - 環境変数を更新（Vercel/Railway）
   - アプリを再デプロイ

3. **不正使用の確認**
   - OpenAI Dashboard > Usage でログを確認
   - 不正な課金がないか確認

#### 3. 報告（24時間以内）
- [ ] 不正使用の金額を確認
- [ ] OpenAI Supportに連絡（必要な場合）
- [ ] インシデントレポートの作成

### 再発防止策
1. APIキーを`.env`ファイルのみで管理
2. `.env`を`.gitignore`に追加（確認）
3. 使用量アラートの設定（OpenAI Dashboard）
4. 月次コスト上限の設定

---

## ⚙️ システム障害時の対応

### 概要
フロントエンド・バックエンドの障害時の対応手順

### 緊急度
**レベル2（High）** - 24時間以内の対応が必要

### 対応手順

#### 1. 障害の特定（15分以内）
- [ ] エラーログの確認
- [ ] Vercel Dashboard > Deployments でステータス確認
- [ ] Supabase Dashboard でステータス確認

#### 2. 原因の調査（30分以内）
1. **フロントエンドの障害**
   - Vercel Dashboard > Logs でエラーログを確認
   - ビルドエラー、ランタイムエラーの特定

2. **バックエンドの障害**
   - FastAPIのログを確認
   - OpenAI APIのステータス確認: https://status.openai.com/
   - Supabaseのステータス確認: https://status.supabase.com/

#### 3. 修正・再デプロイ（1-2時間以内）
1. **コード修正**
   - バグ修正、設定変更
   - ローカル環境でテスト

2. **デプロイ**
   ```bash
   # Gitにコミット
   git add .
   git commit -m "fix: [障害の説明]"
   git push origin main

   # Vercelが自動デプロイ
   ```

#### 4. 動作確認（30分以内）
- [ ] フロントエンドの動作確認
- [ ] API エンドポイントのテスト
- [ ] データベース接続の確認

#### 5. 報告（24時間以内）
- [ ] インシデントレポートの作成
- [ ] 障害の原因と対策をドキュメント化

---

## 📝 記録と報告

### インシデントレポートフォーマット

```markdown
# インシデントレポート

**日時**: YYYY-MM-DD HH:MM
**レベル**: Critical / High / Medium
**報告者**: [氏名]

## 概要
[インシデントの概要を1-2文で記載]

## 発生時刻
- 検知時刻: YYYY-MM-DD HH:MM
- 発生時刻（推定）: YYYY-MM-DD HH:MM

## 影響範囲
- 影響を受けたユーザー数: X名
- 影響を受けたデータ: [詳細]
- ダウンタイム: X時間Y分

## 原因
[インシデントの根本原因]

## 対応内容
1. [対応手順1]
2. [対応手順2]
...

## 再発防止策
1. [防止策1]
2. [防止策2]
...

## タイムライン
| 時刻 | イベント |
|------|---------|
| HH:MM | [イベント1] |
| HH:MM | [イベント2] |
...

## 教訓
[今回のインシデントから得られた教訓]
```

### 報告先
- **教授**: [メールアドレス]
- **記録場所**: `docs/incidents/YYYY-MM-DD_incident.md`

---

## ✅ チェックリスト

### 定期的な確認項目（週次）
- [ ] `.env`ファイルが`.gitignore`に含まれていることを確認
- [ ] 環境変数が正しく設定されていることを確認
- [ ] OpenAI APIの使用量を確認
- [ ] Supabaseのストレージ使用量を確認
- [ ] アプリケーションのエラーログを確認

### 定期的な確認項目（月次）
- [ ] 暗号化キーのローテーション検討（3ヶ月毎）
- [ ] APIキーのローテーション検討（6ヶ月毎）
- [ ] セキュリティパッチの適用
- [ ] バックアップの確認

---

## 📞 サポートリソース

### ドキュメント
- [Supabase Documentation](https://supabase.com/docs)
- [Vercel Documentation](https://vercel.com/docs)
- [OpenAI API Documentation](https://platform.openai.com/docs)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)

### コミュニティ
- Supabase Discord: https://discord.supabase.com/
- FastAPI Discord: https://discord.gg/fastapi

---

**以上**
