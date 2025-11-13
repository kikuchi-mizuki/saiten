#!/usr/bin/env python3
"""
評価結果（CSV）を集計・分析するスクリプト

使い方:
    python scripts/analyze_evaluation.py data/evaluation_results.csv
"""

import csv
import pathlib
import sys
from statistics import mean

ROOT = pathlib.Path(__file__).resolve().parents[1]


def analyze_evaluation(csv_path: pathlib.Path):
    """評価結果CSVを読み込んで集計・分析"""
    results = []
    
    try:
        with open(csv_path, encoding="utf-8-sig") as f:
            reader = csv.DictReader(f)
            for row in reader:
                try:
                    item = {
                        "id": row.get("評価対象ID", ""),
                        "theme": row.get("レポートテーマ", ""),
                        "文体": int(row.get("文体の一貫性", 0)) if row.get("文体の一貫性") else 0,
                        "次の一歩": int(row.get("次の一歩の妥当性", 0)) if row.get("次の一歩の妥当性") else 0,
                        "断定抑制": int(row.get("過度な断定・誤誘導の抑制", 0)) if row.get("過度な断定・誤誘導の抑制") else 0,
                        "文字数構成": int(row.get("文字数・構成の遵守", 0)) if row.get("文字数・構成の遵守") else 0,
                        "Rubric": int(row.get("Rubricスコアの妥当性", 0)) if row.get("Rubricスコアの妥当性") else 0,
                        "合計": int(row.get("合計", 0)) if row.get("合計") else 0,
                        "コメント": row.get("コメント", ""),
                    }
                    if item["合計"] > 0:
                        results.append(item)
                except (ValueError, KeyError) as e:
                    print(f"⚠️  スキップ: {row.get('評価対象ID', 'unknown')} - {e}")
                    continue
    except FileNotFoundError:
        print(f"❌ ファイルが見つかりません: {csv_path}")
        sys.exit(1)
    
    if not results:
        print("❌ 評価データがありません")
        sys.exit(1)
    
    # 集計
    total_items = len(results)
    avg_total = mean([r["合計"] for r in results])
    avg_style = mean([r["文体"] for r in results])
    avg_next = mean([r["次の一歩"] for r in results])
    avg_assertion = mean([r["断定抑制"] for r in results])
    avg_format = mean([r["文字数構成"] for r in results])
    avg_rubric = mean([r["Rubric"] for r in results])
    
    # 出力
    print("\n" + "=" * 60)
    print("📊 評価結果集計")
    print("=" * 60)
    print(f"\n評価件数: {total_items}件")
    print(f"\n平均点（合計）: {avg_total:.1f}点 / 25点")
    
    print("\n観点別平均点:")
    print(f"  文体の一貫性: {avg_style:.1f}点 / 5点")
    print(f"  次の一歩の妥当性: {avg_next:.1f}点 / 5点")
    print(f"  過度な断定・誤誘導の抑制: {avg_assertion:.1f}点 / 5点")
    print(f"  文字数・構成の遵守: {avg_format:.1f}点 / 5点")
    print(f"  Rubricスコアの妥当性: {avg_rubric:.1f}点 / 5点")
    
    # 評価判定
    print("\n総合評価:")
    if avg_total >= 20:
        print("  ✅ 優秀（そのまま使用可能）")
    elif avg_total >= 15:
        print("  ✅ 良好（軽微な修正で使用可能）")
    elif avg_total >= 10:
        print("  ⚠️  要改善（修正が必要）")
    else:
        print("  ❌ 要再生成（大きな見直しが必要）")
    
    # 改善が必要な観点を特定
    print("\n改善が必要な観点:")
    thresholds = {
        "文体の一貫性": avg_style,
        "次の一歩の妥当性": avg_next,
        "過度な断定・誤誘導の抑制": avg_assertion,
        "文字数・構成の遵守": avg_format,
        "Rubricスコアの妥当性": avg_rubric,
    }
    
    for aspect, score in thresholds.items():
        if score < 3.5:
            print(f"  ❌ {aspect}: {score:.1f}点（改善が必要）")
        elif score < 4.0:
            print(f"  ⚠️  {aspect}: {score:.1f}点（やや改善推奨）")
        else:
            print(f"  ✅ {aspect}: {score:.1f}点（問題なし）")
    
    # 個別評価の詳細
    print("\n" + "=" * 60)
    print("個別評価:")
    print("=" * 60)
    for r in sorted(results, key=lambda x: x["合計"], reverse=True):
        status = "✅" if r["合計"] >= 20 else "⚠️" if r["合計"] >= 15 else "❌"
        print(f"\n{status} {r['id']} ({r['theme']}): {r['合計']}点")
        print(f"  文体:{r['文体']} 次の一歩:{r['次の一歩']} 断定抑制:{r['断定抑制']} 文字数構成:{r['文字数構成']} Rubric:{r['Rubric']}")
        if r["コメント"]:
            print(f"  コメント: {r['コメント']}")


def main():
    if len(sys.argv) < 2:
        print("使い方:")
        print("  python scripts/analyze_evaluation.py <評価結果CSVファイル>")
        print("")
        print("例:")
        print("  python scripts/analyze_evaluation.py data/evaluation_results.csv")
        sys.exit(1)
    
    csv_path = pathlib.Path(sys.argv[1])
    if not csv_path.is_absolute():
        csv_path = ROOT / csv_path
    
    analyze_evaluation(csv_path)


if __name__ == "__main__":
    main()




