#!/bin/bash
# Streamlit UIサーバー起動スクリプト

cd "$(dirname "$0")"

echo "🚀 Streamlit UIサーバーを起動します..."
echo ""

# Streamlitサーバーを起動
python3 -m streamlit run app/streamlit_app.py --server.port=8501

