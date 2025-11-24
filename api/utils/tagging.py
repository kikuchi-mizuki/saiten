"""
ナレッジベースのLLM自動タグ付け機能

教授の思考やコメントを分析して、適切なタグを自動生成します。
"""

import os
from typing import List
from openai import OpenAI

client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))


def generate_tags(text: str, existing_tags: List[str] = None) -> List[str]:
    """
    テキストを分析して適切なタグを自動生成する

    Args:
        text: タグ付けするテキスト
        existing_tags: 既存のタグリスト（参考用）

    Returns:
        生成されたタグのリスト（3-5個）
    """
    # 既存のタグ例を提示
    existing_tags_str = ""
    if existing_tags and len(existing_tags) > 0:
        existing_tags_str = f"\n\n既存のタグ例: {', '.join(existing_tags[:20])}"

    prompt = f"""以下のテキストを分析して、適切なタグを3-5個生成してください。

# タグ生成のガイドライン
- 主要なテーマやトピックを抽出
- 具体的かつ簡潔な単語を使用
- 重複を避ける
- 日本語で記述{existing_tags_str}

# テキスト
{text}

# 出力形式
タグをカンマ区切りで出力してください（例: 経営戦略, 人事政策, イノベーション）
タグのみを出力し、説明や補足は不要です。"""

    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "あなたは教授の思考やコメントを分析し、適切なタグを生成する専門家です。"},
                {"role": "user", "content": prompt}
            ],
            temperature=0.3,
            max_tokens=100
        )

        # レスポンスからタグを抽出
        tags_text = response.choices[0].message.content.strip()

        # カンマ区切りで分割してリストに変換
        tags = [tag.strip() for tag in tags_text.split(',') if tag.strip()]

        # 最大5個に制限
        return tags[:5]

    except Exception as e:
        print(f"⚠️ タグ生成エラー: {e}")
        # エラー時はデフォルトタグを返す
        return ["教授コメント"]


def suggest_content_type(text: str) -> str:
    """
    テキストを分析してコンテンツタイプ（comment/thought/lecture）を推奨する

    Args:
        text: 分析するテキスト

    Returns:
        推奨されるコンテンツタイプ
    """
    prompt = f"""以下のテキストを分析して、最も適切なコンテンツタイプを判定してください。

# コンテンツタイプ
- comment: 学生レポートへのフィードバックコメント
- thought: 教授の思考や考察、メモ
- lecture: 講義資料や講演内容

# テキスト
{text}

# 出力
以下のいずれか1つを出力してください: comment, thought, lecture"""

    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "あなたはテキストの性質を分析し、適切なカテゴリーに分類する専門家です。"},
                {"role": "user", "content": prompt}
            ],
            temperature=0,
            max_tokens=10
        )

        content_type = response.choices[0].message.content.strip().lower()

        # 有効な値のみを返す
        if content_type in ["comment", "thought", "lecture"]:
            return content_type
        else:
            return "thought"  # デフォルト

    except Exception as e:
        print(f"⚠️ コンテンツタイプ推定エラー: {e}")
        return "thought"  # デフォルト
