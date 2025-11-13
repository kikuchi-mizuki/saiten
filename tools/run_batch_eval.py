#!/usr/bin/env python3
"""
実レポートをバッチ生成するスクリプト

使い方:
    # 実レポート（TXT）を data/reports/ に配置
    python tools/run_batch_eval.py --api http://127.0.0.1:8010
    
    # 出力: data/eval/generated_YYYYMMDD_HHMMSS.csv
"""

import argparse
import csv
import glob
import json
import pathlib
import sys
import time
from datetime import datetime
from typing import Dict, List, Optional

import requests

ROOT = pathlib.Path(__file__).resolve().parents[1]


def generate_comment(api_url: str, text: str, report_type: str = "reflection") -> Optional[Dict]:
    """APIを呼び出してコメント生成"""
    url = f"{api_url.rstrip('/')}/v1/generate_direct"
    
    try:
        response = requests.post(
            url,
            json={"text": text, "type": report_type},
            timeout=30
        )
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"❌ APIエラー ({url}): {e}", file=sys.stderr)
        return None


def run_batch_eval(api_url: str, reports_dir: Optional[pathlib.Path] = None, output_dir: Optional[pathlib.Path] = None):
    """バッチ生成を実行"""
    
    # ディレクトリ設定
    if reports_dir is None:
        reports_dir = ROOT / "data" / "reports"
    if output_dir is None:
        output_dir = ROOT / "data" / "eval"
    
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # レポートファイルを検索
    report_files = sorted(glob.glob(str(reports_dir / "*.txt")))
    
    if not report_files:
        print(f"❌ レポートファイルが見つかりません: {reports_dir}")
        print(f"   data/reports/*.txt に実レポートを配置してください")
        sys.exit(1)
    
    print(f"📁 レポートファイル: {len(report_files)}件見つかりました")
    print(f"🌐 API: {api_url}")
    print(f"💾 出力先: {output_dir}\n")
    
    # 生成実行
    results: List[Dict] = []
    
    for i, report_file in enumerate(report_files, 1):
        report_path = pathlib.Path(report_file)
        report_name = report_path.stem
        
        print(f"[{i}/{len(report_files)}] 処理中: {report_name}...", end=" ", flush=True)
        
        try:
            # レポート本文を読み込み
            with open(report_path, "r", encoding="utf-8") as f:
                report_text = f.read().strip()
            
            if not report_text:
                print("⚠️  空ファイル（スキップ）")
                continue
            
            # API呼び出し
            result = generate_comment(api_url, report_text)
            
            if result is None:
                print("❌ 生成失敗")
                continue
            
            # 結果を保存
            results.append({
                "report_file": report_path.name,
                "report_name": report_name,
                "report_length": len(report_text),
                "ai_comment": result.get("ai_comment", ""),
                "rubric_理解度": result.get("rubric", {}).get("理解度", 0),
                "rubric_論理性": result.get("rubric", {}).get("論理性", 0),
                "rubric_独自性": result.get("rubric", {}).get("独自性", 0),
                "rubric_実践性": result.get("rubric", {}).get("実践性", 0),
                "rubric_表現力": result.get("rubric", {}).get("表現力", 0),
                "rubric_total": sum(result.get("rubric", {}).values()),
                "llm_used": result.get("llm_used", False),
                "llm_error": result.get("llm_error", ""),
                "prompt_version": result.get("prompt_version", ""),
                "model_version": result.get("model_version", ""),
                "generated_at": datetime.now().isoformat(),
            })
            
            print("✅ 完了")
            time.sleep(0.5)  # API負荷軽減
            
        except Exception as e:
            print(f"❌ エラー: {e}")
            continue
    
    # CSV出力
    if not results:
        print("\n❌ 生成結果がありません")
        sys.exit(1)
    
    output_file = output_dir / f"generated_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
    
    fieldnames = [
        "report_file", "report_name", "report_length",
        "ai_comment", "rubric_理解度", "rubric_論理性", "rubric_独自性", 
        "rubric_実践性", "rubric_表現力", "rubric_total",
        "llm_used", "llm_error", "prompt_version", "model_version", "generated_at"
    ]
    
    with open(output_file, "w", newline="", encoding="utf-8-sig") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(results)
    
    print(f"\n✅ 完了: {len(results)}件の結果を保存しました")
    print(f"📄 {output_file}")
    print("\n次のステップ:")
    print(f"  1. 生成結果を確認: {output_file}")
    print(f"  2. 教授による手動評価: data/evaluation_sheet_template.csv をコピーして記入")
    print(f"  3. 差分分析: python scripts/compare_rubric.py --generated {output_file} --human <評価CSV>")


def main():
    parser = argparse.ArgumentParser(description="実レポートをバッチ生成")
    parser.add_argument(
        "--api",
        default="http://127.0.0.1:8010",
        help="APIベースURL (デフォルト: http://127.0.0.1:8010)"
    )
    parser.add_argument(
        "--reports-dir",
        type=pathlib.Path,
        help="レポートファイルのディレクトリ (デフォルト: data/reports)"
    )
    parser.add_argument(
        "--output-dir",
        type=pathlib.Path,
        help="出力ディレクトリ (デフォルト: data/eval)"
    )
    
    args = parser.parse_args()
    
    # API疎通確認
    try:
        health_url = f"{args.api.rstrip('/')}/v1/health"
        response = requests.get(health_url, timeout=5)
        if response.status_code != 200:
            print(f"❌ APIが応答しません: {health_url}")
            sys.exit(1)
    except requests.exceptions.RequestException as e:
        print(f"❌ APIに接続できません: {health_url}")
        print(f"   エラー: {e}")
        print(f"   APIが起動しているか確認してください")
        sys.exit(1)
    
    run_batch_eval(args.api, args.reports_dir, args.output_dir)


if __name__ == "__main__":
    main()



