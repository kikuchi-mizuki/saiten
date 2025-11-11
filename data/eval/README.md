# 評価結果格納ディレクトリ

このディレクトリに評価結果（生成CSV、人間評価CSV、分析レポート）を保存します。

## ファイル構成

### 生成結果CSV

- **ファイル名**: `generated_YYYYMMDD_HHMMSS.csv`
- **生成方法**: `python tools/run_batch_eval.py`
- **列**: report_file, report_name, ai_comment, rubric_理解度, rubric_論理性, ..., llm_used, prompt_version, model_version

### 人間評価CSV

- **ファイル名**: `human_scores_YYYYMMDD.csv`（任意）
- **元テンプレート**: `data/evaluation_sheet_template.csv`をコピーして記入
- **記入内容**:
  - **AI_理解度〜AI_表現力**: 生成結果CSVからコピー（自動）
  - **教授_理解度〜教授_表現力**: 教授が手動で採点（1〜5）
  - **文体の一貫性〜合計**: 出力品質の評価（1〜5）

### 分析レポート

- **生成方法**: `python scripts/compare_rubric.py --generated <生成CSV> --human <評価CSV>`
- **出力**: コンソールに表示（必要に応じてリダイレクト）

## 評価フロー

```bash
# 1. 実レポートを配置
cp <実レポート>.txt data/reports/test_001.txt
# ... 5〜10件

# 2. バッチ生成
python tools/run_batch_eval.py --api http://127.0.0.1:8010
# → data/eval/generated_YYYYMMDD_HHMMSS.csv

# 3. 生成結果を確認し、評価シートにコピー
# data/evaluation_sheet_template.csv をコピー
cp data/evaluation_sheet_template.csv data/eval/human_scores_YYYYMMDD.csv
# AI_理解度〜AI_表現力列に生成結果CSVから値をコピー

# 4. 教授が手動評価
# 教授_理解度〜教授_表現力列に手動で1〜5を記入
# 文体の一貫性〜合計も1〜5で記入

# 5. 差分分析
python scripts/compare_rubric.py \
  --generated data/eval/generated_YYYYMMDD_HHMMSS.csv \
  --human data/eval/human_scores_YYYYMMDD.csv

# 6. 改善反映
# Rubric合致率が目標（±0.5）に達していない場合
# - プロンプト調整: prompts/reflection.txt
# - 再生成・再評価
```

## 注意事項

- 評価結果CSVには個人情報が含まれる可能性があります。適切に管理してください（要件定義書§8-2の削除SLAに準拠）。
- 評価後は不要なファイルを削除するか、暗号化して保管してください。



