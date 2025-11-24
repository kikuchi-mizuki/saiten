"""
ナレッジベース管理画面（Phase 2 Week 3-4）

教授の思考を追加・管理する画面
"""

import streamlit as st
import requests
import json
import os
from datetime import datetime

# API URL設定
try:
    API = st.secrets["API_URL"]
except Exception:
    API = os.environ.get("API_URL", "http://localhost:8010")

API_BASE = API if API else "http://localhost:8010"

# ページ設定
st.set_page_config(
    page_title="ナレッジベース管理 - 教授コメント自動化",
    page_icon="📚",
    layout="wide"
)

# セッション状態の初期化
if 'jwt_token' not in st.session_state:
    st.session_state.jwt_token = None
if 'references' not in st.session_state:
    st.session_state.references = []
if 'total_pages' not in st.session_state:
    st.session_state.total_pages = 1
if 'current_page' not in st.session_state:
    st.session_state.current_page = 1
if 'search_query' not in st.session_state:
    st.session_state.search_query = ""
if 'selected_tags' not in st.session_state:
    st.session_state.selected_tags = []
if 'selected_type' not in st.session_state:
    st.session_state.selected_type = "全て"


# ヘルパー関数
def get_headers():
    """認証ヘッダーを取得"""
    if st.session_state.jwt_token:
        return {
            "Authorization": f"Bearer {st.session_state.jwt_token}",
            "Content-Type": "application/json"
        }
    return {"Content-Type": "application/json"}


def load_references(page=1, per_page=20, search="", tags="", ref_type=""):
    """参照例を読み込む"""
    try:
        params = {
            "page": page,
            "per_page": per_page
        }
        if search:
            params["search"] = search
        if tags:
            params["tags"] = tags
        if ref_type and ref_type != "全て":
            params["type"] = ref_type

        response = requests.get(
            f"{API_BASE}/references",
            headers=get_headers(),
            params=params,
            timeout=30
        )

        if response.status_code == 200:
            data = response.json()
            st.session_state.references = data.get("references", [])
            st.session_state.total_pages = data.get("total_pages", 1)
            return True
        elif response.status_code == 401:
            st.error("認証エラー: ログインが必要です")
            return False
        else:
            st.error(f"エラー: {response.status_code} - {response.text}")
            return False

    except requests.exceptions.ConnectionError:
        st.error(f"APIサーバーに接続できません\n\nAPI URL: {API_BASE}")
        return False
    except Exception as e:
        st.error(f"予期しないエラー: {str(e)}")
        return False


def create_reference(text, ref_type, tags=None):
    """新しい参照例を作成"""
    try:
        data = {
            "text": text,
            "type": ref_type,
            "tags": tags if tags else []
        }

        response = requests.post(
            f"{API_BASE}/references",
            headers=get_headers(),
            json=data,
            timeout=60
        )

        if response.status_code == 200:
            result = response.json()
            st.success("✅ ナレッジベースに追加しました")
            if result.get("reference", {}).get("auto_tagged"):
                st.info(f"🏷️ 自動タグ付け: {', '.join(result['reference']['tags'])}")
            return True
        else:
            st.error(f"エラー: {response.status_code} - {response.text}")
            return False

    except Exception as e:
        st.error(f"予期しないエラー: {str(e)}")
        return False


def delete_reference(reference_id):
    """参照例を削除"""
    try:
        response = requests.delete(
            f"{API_BASE}/references/{reference_id}",
            headers=get_headers(),
            timeout=30
        )

        if response.status_code == 200:
            st.success("✅ 削除しました")
            return True
        else:
            st.error(f"エラー: {response.status_code} - {response.text}")
            return False

    except Exception as e:
        st.error(f"予期しないエラー: {str(e)}")
        return False


# ======================
# メインUI
# ======================

st.title("📚 ナレッジベース管理")
st.markdown("教授の思考やコメントを追加・管理します。")

# トークン入力（仮）
if not st.session_state.jwt_token:
    with st.expander("🔑 認証トークン", expanded=True):
        token = st.text_input("JWTトークンを入力してください", type="password")
        if st.button("認証"):
            if token:
                st.session_state.jwt_token = token
                st.rerun()
            else:
                st.error("トークンを入力してください")
    st.stop()

# タブでUIを分ける
tab1, tab2 = st.tabs(["📝 新規追加", "📋 一覧・管理"])

# ======================
# Tab 1: 新規追加
# ======================
with tab1:
    st.subheader("新しい思考・コメントを追加")

    col1, col2 = st.columns([3, 1])

    with col1:
        text_input = st.text_area(
            "テキスト",
            height=200,
            placeholder="教授の思考やコメントを入力してください...",
            help="ここに入力したテキストは自動的にEmbedding化され、検索可能になります。"
        )

    with col2:
        ref_type = st.selectbox(
            "レポート種別",
            options=["final", "reflection"],
            format_func=lambda x: "最終レポート" if x == "final" else "中間レポート"
        )

        auto_tag = st.checkbox("自動タグ付け", value=True, help="チェックすると、LLMが自動的にタグを生成します")

        manual_tags = st.text_input(
            "手動タグ（カンマ区切り）",
            disabled=auto_tag,
            placeholder="経営戦略, 人事政策"
        )

    if st.button("➕ 追加", type="primary", use_container_width=True):
        if not text_input:
            st.error("テキストを入力してください")
        else:
            tags = None if auto_tag else [t.strip() for t in manual_tags.split(",") if t.strip()]

            with st.spinner("追加中..."):
                if create_reference(text_input, ref_type, tags):
                    # 成功したら一覧を再読み込み
                    load_references(
                        page=st.session_state.current_page,
                        search=st.session_state.search_query,
                        ref_type=st.session_state.selected_type
                    )
                    st.rerun()

# ======================
# Tab 2: 一覧・管理
# ======================
with tab2:
    st.subheader("ナレッジベース一覧")

    # 検索・フィルタUI
    col1, col2, col3, col4 = st.columns([3, 2, 2, 1])

    with col1:
        search = st.text_input("🔍 テキスト検索", value=st.session_state.search_query, placeholder="キーワードで検索...")

    with col2:
        type_filter = st.selectbox(
            "レポート種別",
            options=["全て", "final", "reflection"],
            index=["全て", "final", "reflection"].index(st.session_state.selected_type),
            format_func=lambda x: "全て" if x == "全て" else ("最終レポート" if x == "final" else "中間レポート")
        )

    with col3:
        # タグフィルタは一旦スキップ（将来実装）
        st.text_input("🏷️ タグフィルタ", disabled=True, placeholder="（将来実装）")

    with col4:
        if st.button("検索", type="primary"):
            st.session_state.search_query = search
            st.session_state.selected_type = type_filter
            st.session_state.current_page = 1
            load_references(
                page=1,
                search=search,
                ref_type=type_filter if type_filter != "全て" else ""
            )
            st.rerun()

    # 初回読み込み
    if not st.session_state.references:
        load_references()

    # 一覧表示
    if st.session_state.references:
        st.markdown(f"**総件数**: {len(st.session_state.references)}件")

        for ref in st.session_state.references:
            with st.container():
                col1, col2 = st.columns([5, 1])

                with col1:
                    # タグ表示
                    tags_html = " ".join([f'<span style="background-color: #E5E7EB; padding: 2px 8px; border-radius: 4px; font-size: 12px; margin-right: 4px;">{tag}</span>' for tag in ref.get("tags", [])])
                    st.markdown(f"**{ref.get('type', 'unknown')}** | {tags_html}", unsafe_allow_html=True)

                    # テキスト表示
                    text_preview = ref.get("text", "")[:200] + ("..." if len(ref.get("text", "")) > 200 else "")
                    st.markdown(f"> {text_preview}")

                    # メタ情報
                    st.caption(f"ID: {ref.get('id', 'N/A')} | 作成日: {ref.get('created_at', 'N/A')}")

                with col2:
                    if st.button("🗑️ 削除", key=f"del_{ref.get('id')}", type="secondary"):
                        if delete_reference(ref.get("id")):
                            load_references(
                                page=st.session_state.current_page,
                                search=st.session_state.search_query,
                                ref_type=st.session_state.selected_type
                            )
                            st.rerun()

                st.divider()

        # ページネーション
        if st.session_state.total_pages > 1:
            col1, col2, col3 = st.columns([1, 3, 1])

            with col1:
                if st.session_state.current_page > 1:
                    if st.button("⬅️ 前へ"):
                        st.session_state.current_page -= 1
                        load_references(
                            page=st.session_state.current_page,
                            search=st.session_state.search_query,
                            ref_type=st.session_state.selected_type
                        )
                        st.rerun()

            with col2:
                st.markdown(f"<center>ページ {st.session_state.current_page} / {st.session_state.total_pages}</center>", unsafe_allow_html=True)

            with col3:
                if st.session_state.current_page < st.session_state.total_pages:
                    if st.button("次へ ➡️"):
                        st.session_state.current_page += 1
                        load_references(
                            page=st.session_state.current_page,
                            search=st.session_state.search_query,
                            ref_type=st.session_state.selected_type
                        )
                        st.rerun()
    else:
        st.info("ナレッジベースにエントリがありません。「新規追加」タブから追加してください。")
