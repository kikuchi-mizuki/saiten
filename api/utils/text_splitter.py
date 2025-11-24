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
以下のJSON形式で出力してください：
```json
[
  {{"title": "セクション1のタイトル", "content": "セクション1の内容（元のテキストそのまま）"}},
  {{"title": "セクション2のタイトル", "content": "セクション2の内容（元のテキストそのまま）"}},
  ...
]
```

# テキスト
{text}

# 出力
"""

    try:
        response = client.chat.completions.create(
            model="gpt-4o",  # 高品質な分割のためgpt-4oを使用
            messages=[
                {
                    "role": "system",
                    "content": "あなたはテキストを意味のあるまとまりに分割する専門家です。元のテキストの内容を一切変更せず、適切に分割してください。"
                },
                {"role": "user", "content": prompt}
            ],
            temperature=0.3,
            max_tokens=len(text) + 1000,  # 十分なトークン数を確保
            response_format={"type": "json_object"} if "gpt-4" in "gpt-4o" else None
        )

        result_text = response.choices[0].message.content.strip()

        # JSONを抽出（```json ... ```の場合に対応）
        if "```json" in result_text:
            import re
            json_match = re.search(r'```json\s*(.*?)\s*```', result_text, re.DOTALL)
            if json_match:
                result_text = json_match.group(1)

        # JSONをパース
        import json
        sections = json.loads(result_text)

        # リスト形式でない場合（辞書でラップされている場合）
        if isinstance(sections, dict):
            # {"sections": [...]} のような形式の場合
            if "sections" in sections:
                sections = sections["sections"]
            # {"result": [...]} のような形式の場合
            elif "result" in sections:
                sections = sections["result"]
            else:
                # 最初のリスト値を取得
                for value in sections.values():
                    if isinstance(value, list):
                        sections = value
                        break

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
