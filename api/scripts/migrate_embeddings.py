"""
既存のknowledge_baseデータをEmbedding化するマイグレーションスクリプト

このスクリプトは以下を実行します:
1. knowledge_baseから全データを取得
2. OpenAI Embeddings APIで各テキストをEmbedding化
3. データベースを更新
"""

import os
import sys
from pathlib import Path
from typing import List

# プロジェクトルートをパスに追加
sys.path.append(str(Path(__file__).parent.parent.parent))

from supabase import create_client, Client
from dotenv import load_dotenv

# api/utils/embedding.pyをインポート
sys.path.append(str(Path(__file__).parent.parent))
from utils.embedding import generate_embeddings_batch

# 環境変数を読み込み
load_dotenv()

# Supabaseクライアント初期化
url = os.getenv("SUPABASE_URL")
key = os.getenv("SUPABASE_ANON_KEY")
supabase: Client = create_client(url, key)


def migrate_embeddings(batch_size: int = 50):
    """
    既存のknowledge_baseデータをEmbedding化

    Args:
        batch_size: 一度に処理する件数（OpenAI APIの制限を考慮）
    """
    print("=== Embedding マイグレーション開始 ===\n")

    # 1. 既存データ取得
    print("1. knowledge_baseから既存データを取得中...")
    try:
        result = supabase.table("knowledge_base").select("*").execute()
        knowledge_items = result.data
        total = len(knowledge_items)
        print(f"   ✅ 取得完了: {total}件\n")
    except Exception as e:
        print(f"   ❌ エラー: {e}")
        return

    if total == 0:
        print("   ⚠️  データが存在しません")
        return

    # 2. バッチ処理でEmbedding化
    print(f"2. Embedding化を開始（バッチサイズ: {batch_size}件）...")

    for i in range(0, total, batch_size):
        batch = knowledge_items[i:i+batch_size]
        batch_num = i // batch_size + 1
        batch_count = min(batch_size, total - i)

        print(f"   バッチ {batch_num} ({batch_count}件) を処理中...")

        # テキストを抽出
        texts = [item["text"] for item in batch]

        try:
            # Embedding生成
            embeddings = generate_embeddings_batch(texts)

            # データベース更新
            for item, embedding in zip(batch, embeddings):
                supabase.table("knowledge_base").update({
                    "embedding": embedding,
                    # デフォルト値を設定（既存データ用）
                    "content_type": "comment",
                    "source": "migration"
                }).eq("id", item["id"]).execute()

            print(f"   ✅ バッチ {batch_num} 完了")

        except Exception as e:
            print(f"   ❌ バッチ {batch_num} エラー: {e}")
            print(f"   続行します...")
            continue

    print(f"\n=== Embedding マイグレーション完了 ===")
    print(f"総件数: {total}件")

    # 3. 確認
    print("\n3. Embedding化されたデータを確認中...")
    try:
        result = supabase.table("knowledge_base")\
            .select("id, embedding")\
            .not_.is_("embedding", "null")\
            .execute()
        embedded_count = len(result.data)
        print(f"   ✅ Embedding化済み: {embedded_count}件 / {total}件")

        if embedded_count == total:
            print(f"   🎉 全データのEmbedding化が完了しました！")
        else:
            print(f"   ⚠️  未完了: {total - embedded_count}件")

    except Exception as e:
        print(f"   ❌ 確認エラー: {e}")


if __name__ == "__main__":
    print("\n" + "=" * 50)
    print("knowledge_base Embedding マイグレーション")
    print("=" * 50 + "\n")

    # 確認
    print("⚠️  このスクリプトは既存のknowledge_baseデータを更新します。")
    print("続行しますか？ (y/n): ", end="")

    # 自動実行モード（コマンドライン引数で-yを指定）
    if len(sys.argv) > 1 and sys.argv[1] == "-y":
        answer = "y"
        print("y (自動実行)")
    else:
        answer = input().strip().lower()

    if answer == "y":
        migrate_embeddings()
    else:
        print("キャンセルされました")
