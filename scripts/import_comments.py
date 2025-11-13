#!/usr/bin/env python3
"""
スプレッドシート（CSV/Excel）から教授コメントを読み込んでsample_comments.jsonに変換するスクリプト

使い方:
    python scripts/import_comments.py data/comments.csv
    python scripts/import_comments.py data/comments.xlsx
"""

import json
import pathlib
import sys
import pandas as pd
from typing import List, Dict, Any

ROOT = pathlib.Path(__file__).resolve().parents[1]
OUTPUT_PATH = ROOT / "data" / "sample_comments.json"


def parse_tags(tags_str: str) -> List[str]:
    """タグ文字列を配列に変換（カンマ区切り or 空白区切り）"""
    if not tags_str or pd.isna(tags_str):
        return []
    tags_str = str(tags_str).strip()
    # カンマ区切り優先、なければ空白区切り
    if "," in tags_str:
        return [t.strip() for t in tags_str.split(",") if t.strip()]
    else:
        return [t.strip() for t in tags_str.split() if t.strip()]


def csv_to_json(csv_path: pathlib.Path) -> List[Dict[str, Any]]:
    """CSVファイルを読み込んでJSON形式に変換"""
    try:
        df = pd.read_csv(csv_path, encoding="utf-8-sig")
    except UnicodeDecodeError:
        df = pd.read_csv(csv_path, encoding="shift_jis")
    
    result = []
    for _, row in df.iterrows():
        item = {
            "id": str(row.get("id", "")).strip(),
            "type": str(row.get("type", "reflection")).strip(),
            "text": str(row.get("text", "")).strip(),
            "tags": parse_tags(row.get("tags", "")),
            "source": str(row.get("source", "professor_examples")).strip(),
        }
        # 必須項目チェック
        if item["id"] and item["text"]:
            result.append(item)
        else:
            print(f"⚠️  スキップ: id={item['id']}, textの長さ={len(item['text'])}")
    
    return result


def excel_to_json(excel_path: pathlib.Path, sheet_name: str = None) -> List[Dict[str, Any]]:
    """Excelファイルを読み込んでJSON形式に変換"""
    try:
        if sheet_name:
            df = pd.read_excel(excel_path, sheet_name=sheet_name)
        else:
            df = pd.read_excel(excel_path, sheet_name=0)
    except Exception as e:
        print(f"❌ Excel読み込みエラー: {e}")
        return []
    
    result = []
    for _, row in df.iterrows():
        item = {
            "id": str(row.get("id", "")).strip(),
            "type": str(row.get("type", "reflection")).strip(),
            "text": str(row.get("text", "")).strip(),
            "tags": parse_tags(row.get("tags", "")),
            "source": str(row.get("source", "professor_examples")).strip(),
        }
        # 必須項目チェック
        if item["id"] and item["text"]:
            result.append(item)
        else:
            print(f"⚠️  スキップ: id={item['id']}, textの長さ={len(item['text'])}")
    
    return result


def merge_with_existing(new_items: List[Dict[str, Any]], merge_mode: str = "replace") -> List[Dict[str, Any]]:
    """既存のJSONとマージ（追加/置換）"""
    if merge_mode == "replace":
        return new_items
    
    # 追加モード
    if not OUTPUT_PATH.exists():
        return new_items
    
    try:
        existing = json.loads(OUTPUT_PATH.read_text(encoding="utf-8"))
        existing_ids = {item["id"] for item in existing}
        # 既存IDをスキップ
        merged = [item for item in existing if item["id"] not in existing_ids]
        merged.extend(new_items)
        return merged
    except Exception as e:
        print(f"⚠️  既存ファイル読み込みエラー: {e}")
        return new_items


def main():
    if len(sys.argv) < 2:
        print("使い方:")
        print("  python scripts/import_comments.py <CSV/Excelファイルパス> [--merge|--replace]")
        print("")
        print("オプション:")
        print("  --merge  : 既存のJSONに追加（デフォルト）")
        print("  --replace: 既存のJSONを置き換える")
        print("")
        print("CSV/Excelの列:")
        print("  id      : 一意の識別子（必須）")
        print("  type    : reflection または final（デフォルト: reflection）")
        print("  text    : コメント本文（必須、改行は\\nで記述）")
        print("  tags    : タグ（カンマ区切り、例: 仮説検証,KPI,顧客価値）")
        print("  source  : 出典（デフォルト: professor_examples）")
        sys.exit(1)
    
    input_path = pathlib.Path(sys.argv[1])
    merge_mode = "merge" if "--merge" in sys.argv else "replace"
    
    if not input_path.exists():
        print(f"❌ ファイルが見つかりません: {input_path}")
        sys.exit(1)
    
    # ファイル形式判定
    suffix = input_path.suffix.lower()
    if suffix == ".csv":
        print(f"📄 CSVファイルを読み込み中: {input_path}")
        items = csv_to_json(input_path)
    elif suffix in [".xlsx", ".xls"]:
        print(f"📊 Excelファイルを読み込み中: {input_path}")
        items = excel_to_json(input_path)
    else:
        print(f"❌ サポートされていないファイル形式: {suffix}")
        print("   対応: .csv, .xlsx, .xls")
        sys.exit(1)
    
    if not items:
        print("❌ 読み込めるデータがありません")
        sys.exit(1)
    
    print(f"✅ {len(items)}件のコメントを読み込みました")
    
    # 既存データとマージ
    if merge_mode == "merge":
        items = merge_with_existing(items, merge_mode="merge")
        print(f"✅ 既存データとマージしました（合計: {len(items)}件）")
    
    # JSONに保存
    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_PATH.write_text(
        json.dumps(items, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8"
    )
    print(f"✅ {OUTPUT_PATH} に保存しました")


if __name__ == "__main__":
    main()


