# Phase 2 Week 7: PPT生成機能 実装計画書

**期間**: Week 7（7日間）
**目標**: Genspark用プロンプト生成システムの完成
**作成日**: 2025-12-08

---

## 📅 実装スケジュール

### Day 1-2: データベース＋バックエンド基盤

**タスク**：
- [ ] データベーススキーマ作成
  - `professor_profile` テーブル
  - `ppt_generations` テーブル
  - 90日自動削除のCron設定
- [ ] APIエンドポイント骨格
  - POST `/api/ppt/generate-content`
  - POST `/api/ppt/generate-genspark-prompt`
  - GET `/api/ppt/history`
- [ ] 教授プロファイルのデフォルト値設定

**成果物**：
- マイグレーションファイル
- API骨格コード

---

### Day 3-4: コア機能実装

**タスク**：
- [ ] 検索クエリ生成（gpt-4o-mini）
- [ ] ナレッジベース検索統合
- [ ] 詳細内容生成（gpt-4o）
- [ ] Gensparkプロンプト組み立て
- [ ] エラーハンドリング＋リトライ

**成果物**：
- `utils/ppt_generator.py` 完成
- エンドツーエンドテスト成功

---

### Day 5: フロントエンド実装

**タスク**：
- [ ] プロンプト入力画面
- [ ] 生成中の進捗表示
- [ ] Markdown編集画面
- [ ] プレビュー機能
- [ ] Gensparkプロンプト表示

**成果物**：
- `/ppt/generate` ページ完成
- 基本UIデザイン完了

---

### Day 6: 履歴管理＋統合テスト

**タスク**：
- [ ] 履歴一覧画面
- [ ] 履歴詳細表示
- [ ] 削除機能
- [ ] 統合テスト（3パターン）
- [ ] パフォーマンステスト

**成果物**：
- 履歴管理機能完成
- テストレポート

---

### Day 7: デプロイ＋ドキュメント

**タスク**：
- [ ] Railway デプロイ
- [ ] 本番環境での動作確認
- [ ] ユーザーマニュアル作成
- [ ] 教授による初回テスト

**成果物**：
- 本番環境稼働
- マニュアル

---

## 🎯 優先度別タスク

### P0（必須）

1. ✅ データベーススキーマ
2. ✅ 検索クエリ生成
3. ✅ 詳細内容生成
4. ✅ Gensparkプロンプト組み立て
5. ✅ プロンプト入力UI
6. ✅ 編集画面
7. ✅ プロンプト表示画面

### P1（高優先）

8. ✅ 進捗表示
9. ✅ プレビュー機能
10. ✅ 履歴保存
11. ✅ 基本エラーハンドリング

### P2（可能なら）

12. 履歴一覧
13. デザイン設定画面
14. バリデーション
15. 自動保存

---

## 📝 実装チェックリスト

### バックエンド

```python
# api/routers/ppt.py
- [ ] POST /api/ppt/generate-content
- [ ] POST /api/ppt/generate-genspark-prompt
- [ ] GET /api/ppt/history
- [ ] GET /api/ppt/history/:id
- [ ] DELETE /api/ppt/history/:id

# api/utils/ppt_generator.py
- [ ] generate_search_queries()
- [ ] search_knowledge_base()
- [ ] generate_markdown_content()
- [ ] generate_genspark_prompt()
- [ ] build_speaker_profile()
- [ ] build_design_specs()

# エラーハンドリング
- [ ] リトライ機能
- [ ] フォールバック（gpt-4o-mini）
- [ ] タイムアウト処理
```

### フロントエンド

```typescript
# frontend/app/ppt/generate/page.tsx
- [ ] プロンプト入力フォーム
- [ ] 生成中の進捗表示
- [ ] Markdown編集エリア
- [ ] プレビューモード
- [ ] Gensparkプロンプト表示
- [ ] コピーボタン

# frontend/app/ppt/history/page.tsx
- [ ] 履歴一覧表示
- [ ] 詳細表示モーダル
- [ ] 削除機能

# frontend/lib/ppt.ts
- [ ] generateContent()
- [ ] generateGensparkPrompt()
- [ ] getHistory()
```

---

## ⚠️ リスク管理

| リスク | 影響 | 対策 |
|--------|------|------|
| LLM生成が遅い | 高 | 進捗表示、タイムアウト設定 |
| Genspark仕様不明 | 中 | プロンプトフォーマット柔軟化 |
| プレビュー実装困難 | 低 | 最低限の表示のみ |

---

## ✅ 完了条件

**Week 7 完了 = 以下全て達成**：

1. ✅ プロンプト入力からGensparkプロンプト生成まで動作
2. ✅ 教授の思考がプロンプトに反映される
3. ✅ Gensparkで実際にPPTが生成できる
4. ✅ 処理時間が許容範囲内（90秒以内）
5. ✅ エラーが適切にハンドリングされる
6. ✅ 履歴が保存される

---

## 🚀 次のステップ（Week 8）

- 統合テスト
- ユーザー受け入れテスト（UAT）
- バグ修正
- パフォーマンスチューニング
- ドキュメント整備

---

**作成者**: Claude
**承認待ち**: 榎戸教授
