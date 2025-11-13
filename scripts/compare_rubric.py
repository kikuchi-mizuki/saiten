#!/usr/bin/env python3
"""
生成Rubricと人間評価の差分を分析するスクリプト

使い方:
    python scripts/compare_rubric.py --generated data/eval/generated.csv --human data/eval/human_scores.csv
"""

import argparse
import csv
import json
import pathlib
import sys
from statistics import mean, stdev
from typing import Dict, List

ROOT = pathlib.Path(__file__).resolve().parents[1]

RUBRIC_CATEGORIES = ["理解度", "論理性", "独自性", "実践性", "表現力"]


def load_generated_csv(csv_path: pathlib.Path) -> Dict[str, Dict]:
    """生成結果CSVを読み込み"""
    results = {}
    
    with open(csv_path, encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        for row in reader:
            report_name = row.get("report_name", row.get("report_file", "")).replace(".txt", "")
            
            rubric = {}
            for cat in RUBRIC_CATEGORIES:
                key = f"rubric_{cat}"
                try:
                    rubric[cat] = int(row.get(key, 0))
                except (ValueError, TypeError):
                    rubric[cat] = 0
            
            results[report_name] = {
                "rubric": rubric,
                "rubric_total": sum(rubric.values()),
                "ai_comment": row.get("ai_comment", ""),
                "llm_used": row.get("llm_used", "False").lower() == "true",
                "prompt_version": row.get("prompt_version", ""),
                "model_version": row.get("model_version", ""),
            }
    
    return results


def load_human_scores_csv(csv_path: pathlib.Path) -> Dict[str, Dict]:
    """人間評価CSVを読み込み"""
    results = {}
    
    with open(csv_path, encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        for row in reader:
            report_id = row.get("評価対象ID", "").strip()
            
            # テンプレートの列名に対応
            rubric = {}
            for cat in RUBRIC_CATEGORIES:
                # 列名のバリエーションに対応
                key_candidates = [
                    f"AI_{cat}",
                    f"生成{cat}",
                    cat,
                    f"rubric_{cat}",
                ]
                value = None
                for key in key_candidates:
                    if key in row and row[key].strip():
                        try:
                            value = int(row[key])
                            break
                        except (ValueError, TypeError):
                            continue
                rubric[cat] = value if value is not None else 0
            
            # 手動評価（教授の修正後Rubric）も読み込み
            human_rubric = {}
            for cat in RUBRIC_CATEGORIES:
                key_candidates = [
                    f"教授_{cat}",
                    f"手動{cat}",
                    f"human_{cat}",
                ]
                value = None
                for key in key_candidates:
                    if key in row and row[key].strip():
                        try:
                            value = int(row[key])
                            break
                        except (ValueError, TypeError):
                            continue
                human_rubric[cat] = value if value is not None else None
            
            results[report_id] = {
                "rubric": rubric,
                "human_rubric": human_rubric if any(v is not None for v in human_rubric.values()) else None,
                "theme": row.get("レポートテーマ", ""),
            }
    
    return results


def calculate_diff(ai_rubric: Dict[str, int], human_rubric: Dict[str, int]) -> Dict[str, float]:
    """差分を計算"""
    diffs = {}
    for cat in RUBRIC_CATEGORIES:
        ai_val = ai_rubric.get(cat, 0)
        human_val = human_rubric.get(cat, 0)
        diffs[cat] = abs(ai_val - human_val)
    return diffs


def analyze_comparison(generated: Dict[str, Dict], human: Dict[str, Dict]):
    """比較分析を実行"""
    
    # マッチング（report_nameと評価対象IDの対応）
    matches: List[Dict] = []
    
    for report_id, human_data in human.items():
        # report_idからreport_nameを推測（test_001 -> test_001 または 001）
        candidates = [report_id, report_id.replace("test_", ""), report_id.replace("_", "")]
        
        matched_data = None
        for candidate in candidates:
            if candidate in generated:
                matched_data = generated[candidate]
                break
        
        if matched_data is None:
            # 部分マッチを試す
            for gen_name in generated.keys():
                if report_id in gen_name or gen_name in report_id:
                    matched_data = generated[gen_name]
                    break
        
        if matched_data is None:
            print(f"⚠️  マッチング失敗: {report_id}", file=sys.stderr)
            continue
        
        ai_rubric = matched_data["rubric"]
        human_rubric = human_data.get("human_rubric") or human_data["rubric"]
        
        diffs = calculate_diff(ai_rubric, human_rubric)
        
        matches.append({
            "report_id": report_id,
            "theme": human_data.get("theme", ""),
            "ai_rubric": ai_rubric,
            "human_rubric": human_rubric,
            "diffs": diffs,
            "ai_total": sum(ai_rubric.values()),
            "human_total": sum(human_rubric.values()),
            "total_diff": abs(sum(ai_rubric.values()) - sum(human_rubric.values())),
        })
    
    if not matches:
        print("❌ マッチングされたデータがありません")
        sys.exit(1)
    
    # 集計
    print("\n" + "=" * 70)
    print("📊 Rubric合致率分析")
    print("=" * 70)
    print(f"\n評価件数: {len(matches)}件\n")
    
    # 観点別平均差分
    avg_diffs = {}
    for cat in RUBRIC_CATEGORIES:
        cat_diffs = [m["diffs"][cat] for m in matches]
        avg_diffs[cat] = {
            "mean": mean(cat_diffs),
            "max": max(cat_diffs),
            "stdev": stdev(cat_diffs) if len(cat_diffs) > 1 else 0,
        }
    
    print("【観点別平均差分】")
    print(f"{'観点':<10} {'平均差分':<10} {'最大差分':<10} {'標準偏差':<10} {'判定'}")
    print("-" * 70)
    
    for cat in RUBRIC_CATEGORIES:
        d = avg_diffs[cat]
        target = 0.5  # 目標: ±0.5以内
        status = "✅" if d["mean"] <= target else "⚠️" if d["mean"] <= 1.0 else "❌"
        print(f"{cat:<10} {d['mean']:<10.2f} {d['max']:<10} {d['stdev']:<10.2f} {status}")
    
    # 全体平均差分
    overall_avg_diff = mean([m["total_diff"] / len(RUBRIC_CATEGORIES) for m in matches])
    overall_max_diff = max([m["total_diff"] / len(RUBRIC_CATEGORIES) for m in matches])
    
    print(f"\n【全体平均差分】")
    print(f"  平均: {overall_avg_diff:.2f}点（目標: ≤0.5点）")
    print(f"  最大: {overall_max_diff:.2f}点")
    
    if overall_avg_diff <= 0.5:
        print(f"  判定: ✅ 合格（目標達成）")
    elif overall_avg_diff <= 1.0:
        print(f"  判定: ⚠️  要改善（目標に近いが未達）")
    else:
        print(f"  判定: ❌ 要再調整（目標と乖離）")
    
    # 個別結果
    print(f"\n【個別結果】")
    print(f"{'ID':<15} {'AI合計':<10} {'教授合計':<10} {'差分':<10} {'判定'}")
    print("-" * 70)
    
    for m in sorted(matches, key=lambda x: x["total_diff"], reverse=True):
        status = "✅" if m["total_diff"] / len(RUBRIC_CATEGORIES) <= 0.5 else "⚠️" if m["total_diff"] / len(RUBRIC_CATEGORIES) <= 1.0 else "❌"
        print(f"{m['report_id']:<15} {m['ai_total']:<10} {m['human_total']:<10} {m['total_diff']:<10} {status}")
        print(f"  AI: {dict(m['ai_rubric'])}")
        print(f"  教授: {dict(m['human_rubric'])}")
        if m["theme"]:
            print(f"  テーマ: {m['theme']}")
        print()
    
    # 改善が必要な観点
    print("【改善が必要な観点】")
    for cat in RUBRIC_CATEGORIES:
        d = avg_diffs[cat]
        if d["mean"] > 0.5:
            print(f"  ❌ {cat}: 平均差分 {d['mean']:.2f}点（目標: ≤0.5点）")
        elif d["mean"] > 0.3:
            print(f"  ⚠️  {cat}: 平均差分 {d['mean']:.2f}点（要監視）")
        else:
            print(f"  ✅ {cat}: 平均差分 {d['mean']:.2f}点（問題なし）")


def main():
    parser = argparse.ArgumentParser(description="生成Rubricと人間評価の差分分析")
    parser.add_argument(
        "--generated",
        type=pathlib.Path,
        required=True,
        help="生成結果CSV (例: data/eval/generated_YYYYMMDD_HHMMSS.csv)"
    )
    parser.add_argument(
        "--human",
        type=pathlib.Path,
        required=True,
        help="人間評価CSV (例: data/eval/human_scores.csv)"
    )
    
    args = parser.parse_args()
    
    generated_path = args.generated
    if not generated_path.is_absolute():
        generated_path = ROOT / generated_path
    
    human_path = args.human
    if not human_path.is_absolute():
        human_path = ROOT / human_path
    
    if not generated_path.exists():
        print(f"❌ ファイルが見つかりません: {generated_path}")
        sys.exit(1)
    
    if not human_path.exists():
        print(f"❌ ファイルが見つかりません: {human_path}")
        sys.exit(1)
    
    print(f"📄 生成結果: {generated_path}")
    print(f"📄 人間評価: {human_path}")
    
    generated_data = load_generated_csv(generated_path)
    human_data = load_human_scores_csv(human_path)
    
    analyze_comparison(generated_data, human_data)


if __name__ == "__main__":
    main()



