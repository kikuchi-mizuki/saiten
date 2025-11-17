#!/usr/bin/env python3
"""
参照例をSupabaseのknowledge_baseテーブルにインポートするスクリプト

使用方法:
    python scripts/import_references_to_supabase.py

前提条件:
    - .envファイルにSUPABASE_URLとSUPABASE_ANON_KEYが設定されていること
    - Supabaseでknowledge_baseテーブルが作成されていること
    - data/sample_comments.jsonが存在すること
"""

import json
import os
import sys
from pathlib import Path

# プロジェクトルートをPythonパスに追加
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

# 環境変数の読み込み
def load_env():
    env_path = ROOT / ".env"
    if not env_path.exists():
        print("警告: .envファイルが見つかりません")
        return
    for line in env_path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        if "=" in line:
            k, v = line.split("=", 1)
            k = k.strip()
            v = v.strip().strip('"').strip("'")
            os.environ.setdefault(k, v)

load_env()

from supabase import create_client, Client

def main():
    """メイン処理"""

    # 環境変数の確認
    supabase_url = os.environ.get("SUPABASE_URL")
    supabase_key = os.environ.get("SUPABASE_ANON_KEY")

    if not supabase_url or not supabase_key:
        print("エラー: SUPABASE_URLまたはSUPABASE_ANON_KEYが設定されていません")
        print("  .envファイルを確認してください")
        sys.exit(1)

    # Supabaseクライアントの初期化
    try:
        supabase: Client = create_client(supabase_url, supabase_key)
        print(f"✓ Supabaseに接続しました: {supabase_url}")
    except Exception as e:
        print(f"エラー: Supabaseへの接続に失敗しました: {e}")
        sys.exit(1)

    # sample_comments.jsonの読み込み
    sample_path = ROOT / "data" / "sample_comments.json"
    if not sample_path.exists():
        print(f"エラー: {sample_path} が見つかりません")
        sys.exit(1)

    try:
        with open(sample_path, "r", encoding="utf-8") as f:
            samples = json.load(f)
        print(f"✓ {sample_path} を読み込みました（{len(samples)}件）")
    except Exception as e:
        print(f"エラー: JSONファイルの読み込みに失敗しました: {e}")
        sys.exit(1)

    # 既存データの確認
    try:
        response = supabase.table("knowledge_base").select("reference_id").execute()
        existing_ids = set(item["reference_id"] for item in response.data)
        print(f"✓ 既存の参照例: {len(existing_ids)}件")
    except Exception as e:
        print(f"警告: 既存データの確認に失敗しました: {e}")
        existing_ids = set()

    # データのインポート
    inserted_count = 0
    skipped_count = 0
    error_count = 0

    for sample in samples:
        reference_id = sample.get("id")

        if not reference_id:
            print(f"警告: IDがないデータをスキップしました: {sample}")
            skipped_count += 1
            continue

        # 既に存在する場合はスキップ
        if reference_id in existing_ids:
            print(f"  スキップ: {reference_id}（既に存在）")
            skipped_count += 1
            continue

        # データの挿入
        try:
            data = {
                "reference_id": reference_id,
                "type": sample.get("type"),
                "text": sample.get("text"),
                "tags": sample.get("tags", []),
                "source": sample.get("source", "professor_examples")
            }

            supabase.table("knowledge_base").insert(data).execute()
            print(f"  ✓ 挿入: {reference_id}")
            inserted_count += 1

        except Exception as e:
            print(f"  ✗ エラー: {reference_id} - {e}")
            error_count += 1

    # 結果のサマリー
    print("\n" + "="*60)
    print("インポート完了")
    print("="*60)
    print(f"  挿入: {inserted_count}件")
    print(f"  スキップ: {skipped_count}件")
    print(f"  エラー: {error_count}件")
    print(f"  合計: {len(samples)}件")
    print("="*60)

    if error_count > 0:
        print("\n⚠️  エラーが発生したデータがあります。上記のログを確認してください。")
        sys.exit(1)
    else:
        print("\n✅ すべてのデータが正常にインポートされました！")

if __name__ == "__main__":
    main()
