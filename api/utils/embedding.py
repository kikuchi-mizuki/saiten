"""
Embedding生成ユーティリティ

OpenAI Embeddings APIを使用してテキストをベクトル化します。
"""

import os
from typing import List
from openai import OpenAI

# OpenAI クライアント初期化
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# 設定
EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "text-embedding-3-small")
EMBEDDING_DIMENSIONS = int(os.getenv("EMBEDDING_DIMENSIONS", "1536"))


def generate_embedding(text: str) -> List[float]:
    """
    テキストをEmbedding化する

    Args:
        text: Embedding化するテキスト

    Returns:
        List[float]: Embeddingベクトル（1536次元）

    Raises:
        Exception: Embedding生成に失敗した場合
    """
    try:
        response = client.embeddings.create(
            model=EMBEDDING_MODEL,
            input=text
        )
        return response.data[0].embedding
    except Exception as e:
        print(f"Embedding generation error: {e}")
        raise


def generate_embeddings_batch(texts: List[str]) -> List[List[float]]:
    """
    複数のテキストを一括でEmbedding化する

    Args:
        texts: Embedding化するテキストのリスト

    Returns:
        List[List[float]]: Embeddingベクトルのリスト

    Raises:
        Exception: Embedding生成に失敗した場合
    """
    try:
        response = client.embeddings.create(
            model=EMBEDDING_MODEL,
            input=texts
        )
        return [data.embedding for data in response.data]
    except Exception as e:
        print(f"Batch embedding generation error: {e}")
        raise


if __name__ == "__main__":
    # テスト
    print("=== Embedding生成テスト ===")
    test_text = "学生が起業を考えるとき、まず顧客視点を持つことが重要です。"

    try:
        embedding = generate_embedding(test_text)
        print(f"✅ Embedding生成成功")
        print(f"   次元数: {len(embedding)}")
        print(f"   最初の5値: {embedding[:5]}")
    except Exception as e:
        print(f"❌ Embedding生成失敗: {e}")
