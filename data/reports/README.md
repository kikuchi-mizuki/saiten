# 実レポート格納ディレクトリ

このディレクトリに評価用の実レポート（TXT形式）を配置してください。

## ファイル形式

- **ファイル名**: `レポートID.txt`（例: `test_001.txt`, `report_001.txt`）
- **エンコーディング**: UTF-8
- **内容**: レポート本文のみ（メタ情報不要）

## 配置方法

```bash
# 実レポート（TXT）を配置
cp <実レポート>.txt data/reports/test_001.txt
cp <実レポート>.txt data/reports/test_002.txt
# ... 5〜10件程度
```

## バッチ生成の実行

```bash
# APIが起動していることを確認（別ターミナル）
# uvicorn api.main:app --port 8010

# バッチ生成を実行
python tools/run_batch_eval.py --api http://127.0.0.1:8010

# 出力: data/eval/generated_YYYYMMDD_HHMMSS.csv
```

## 注意事項

- 実レポートには個人情報が含まれる可能性があります。必要に応じて匿名化してください。
- 評価後は`data/reports/`内のファイルを適切に管理してください（要件定義書§8-2の削除SLAに準拠）。

