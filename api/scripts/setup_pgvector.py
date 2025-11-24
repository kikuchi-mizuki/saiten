"""
Supabase pgvector セットアップスクリプト

このスクリプトを実行して、pgvector拡張を有効化し、
knowledge_baseテーブルを拡張します。
"""

import os
import sys
from pathlib import Path

# プロジェクトルートをパスに追加
sys.path.append(str(Path(__file__).parent.parent.parent))

from supabase import create_client, Client
from dotenv import load_dotenv

# 環境変数を読み込み
load_dotenv()

# Supabaseクライアント初期化
url = os.getenv("SUPABASE_URL")
key = os.getenv("SUPABASE_ANON_KEY")
supabase: Client = create_client(url, key)


def run_sql_file(filepath: str):
    """
    SQLファイルを読み込んで実行

    Args:
        filepath: SQLファイルのパス
    """
    print(f"\n=== {Path(filepath).name} を実行中 ===")

    with open(filepath, 'r', encoding='utf-8') as f:
        sql = f.read()

    # コメントと空行を削除
    sql_commands = []
    for line in sql.split('\n'):
        line = line.strip()
        if line and not line.startswith('--'):
            sql_commands.append(line)

    sql_clean = ' '.join(sql_commands)

    # SQLを実行（SupabaseのRPC経由）
    # Note: Supabase Python クライアントは直接SQLを実行できないため、
    # Supabaseダッシュボードで手動実行が必要です

    print("このSQLをSupabase SQL Editorで実行してください:")
    print("-" * 50)
    print(sql)
    print("-" * 50)


def main():
    """
    メイン処理
    """
    print("=== Supabase pgvector セットアップ ===")
    print("\n注意: Supabase Python クライアントは直接SQLを実行できません。")
    print("以下のSQLファイルをSupabase SQL Editorで順番に実行してください。\n")

    # SQLファイルのパス
    scripts_dir = Path(__file__).parent
    sql_files = [
        scripts_dir / "01_enable_pgvector.sql",
        scripts_dir / "02_alter_knowledge_base.sql",
        scripts_dir / "03_create_search_function.sql"
    ]

    # 各SQLファイルを表示
    for sql_file in sql_files:
        if sql_file.exists():
            run_sql_file(sql_file)
        else:
            print(f"❌ ファイルが見つかりません: {sql_file}")

    print("\n=== 手順 ===")
    print("1. Supabaseダッシュボードにログイン")
    print("2. プロジェクトを選択")
    print("3. 左メニューから「SQL Editor」を選択")
    print("4. 「New query」をクリック")
    print("5. 上記のSQLを順番にコピー&ペーストして実行")
    print("6. 実行完了後、このスクリプトを再実行して確認")


if __name__ == "__main__":
    main()
