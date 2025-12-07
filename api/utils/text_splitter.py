"""
テキスト分割ユーティリティ

長いテキストをLLMで意味のあるまとまり（トピック）ごとに分割します。
"""

import os
from typing import List, Dict
from openai import OpenAI

client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))


def split_text_by_topic(text: str, max_chunk_size: int = 1500) -> List[Dict[str, str]]:
    """
    テキストをLLMで意味のあるまとまり（トピック）ごとに分割する

    Args:
        text: 分割するテキスト
        max_chunk_size: 各チャンクの最大文字数（目安）

    Returns:
        List[Dict]: 分割されたセクションのリスト
        [
            {"title": "セクションタイトル", "content": "セクション内容"},
            ...
        ]
    """
    # テキストが短い場合はそのまま返す
    if len(text) <= max_chunk_size:
        return [{"title": "全文", "content": text}]

    # LLMで分割
    prompt = f"""以下のテキストを意味のあるまとまり（トピック、話題）ごとに分割してください。

# 分割のガイドライン
- 各セクションは{max_chunk_size}文字程度を目安にする（多少の前後は可）
- 話題が変わるところで区切る
- 各セクションに簡潔なタイトル（10-20文字）を付ける
- 元のテキストの内容は一切変更しない（削除、追加、要約しない）
- すべての内容を漏らさず分割する

# 出力形式
以下のJSON形式で出力してください（sectionsキーでリストを返す）：
{{"sections": [
  {{"title": "セクション1のタイトル", "content": "セクション1の内容（元のテキストそのまま）"}},
  {{"title": "セクション2のタイトル", "content": "セクション2の内容（元のテキストそのまま）"}}
]}}

# テキスト
{text}
"""

    try:
        # 日本語は1文字あたり約2-3トークン、JSON構造のオーバーヘッドも考慮
        # gpt-4oの最大出力トークン数は16,384なので、安全マージンを持って計算
        estimated_tokens = int(len(text) * 3.5)  # 日本語の文字数 × 3.5
        max_output_tokens = min(estimated_tokens, 15000)  # 最大15,000トークン

        response = client.chat.completions.create(
            model="gpt-4o",  # 高品質な分割のためgpt-4oを使用
            messages=[
                {
                    "role": "system",
                    "content": "あなたはテキストを意味のあるまとまりに分割する専門家です。元のテキストの内容を一切変更せず、適切に分割してください。必ずJSON形式で応答してください。"
                },
                {"role": "user", "content": prompt}
            ],
            temperature=0.3,
            max_tokens=max_output_tokens,
            response_format={"type": "json_object"}  # JSON形式を強制
        )

        result_text = response.choices[0].message.content.strip()

        # JSONをパース（response_format="json_object"を使用しているので直接パース可能）
        import json
        result = json.loads(result_text)

        # {"sections": [...]} 形式を期待
        if "sections" in result:
            sections = result["sections"]
        else:
            # フォールバック: 最初のリスト値を取得
            sections = result
            for value in result.values():
                if isinstance(value, list):
                    sections = value
                    break

        # セクション数のバリデーション
        if not sections or len(sections) == 0:
            raise ValueError("分割結果が空です")

        print(f"✅ LLMで{len(sections)}個のセクションに分割しました")

        return sections

    except Exception as e:
        print(f"⚠️ LLMでの分割に失敗: {e}")
        print(f"フォールバック: 文字数で機械的に分割します")

        # フォールバック: 文字数で分割
        chunks = []
        for i in range(0, len(text), max_chunk_size):
            chunk_text = text[i:i + max_chunk_size]
            chunks.append({
                "title": f"セクション{len(chunks) + 1}",
                "content": chunk_text
            })

        return chunks


def split_text_simple(text: str, chunk_size: int = 1000) -> List[str]:
    """
    テキストを単純に文字数で分割する（フォールバック用）

    Args:
        text: 分割するテキスト
        chunk_size: 各チャンクのサイズ

    Returns:
        List[str]: 分割されたテキストのリスト
    """
    chunks = []
    for i in range(0, len(text), chunk_size):
        chunks.append(text[i:i + chunk_size])

    return chunks
