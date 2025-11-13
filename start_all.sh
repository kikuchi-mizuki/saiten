#!/bin/bash
# サーバー起動スクリプト（API + UI）

cd "$(dirname "$0")"

echo "🚀 サーバーを起動します..."
echo ""

# ポートをクリア
echo "📌 既存のプロセスを停止中..."
lsof -ti:8010 | xargs kill -9 2>/dev/null
lsof -ti:8501 | xargs kill -9 2>/dev/null
sleep 2

# APIサーバーを起動
echo "🔧 APIサーバーを起動中（ポート8010）..."
python3 -m uvicorn api.main:app --reload --port 8010 > /tmp/api_server.log 2>&1 &
API_PID=$!
sleep 3

# APIサーバーの起動確認
if curl -s http://127.0.0.1:8010/health > /dev/null 2>&1; then
    echo "✅ APIサーバーが起動しました（PID: $API_PID）"
else
    echo "❌ APIサーバーの起動に失敗しました"
    exit 1
fi

# UIサーバーを起動
echo "🎨 UIサーバーを起動中（ポート8501）..."
python3 -m streamlit run app/streamlit_app.py --server.port=8501 &
UI_PID=$!

echo ""
echo "✅ サーバー起動完了！"
echo ""
echo "📱 UI: http://localhost:8501"
echo "🔧 API: http://127.0.0.1:8010"
echo ""
echo "停止するには: kill $API_PID $UI_PID"
echo ""

wait

