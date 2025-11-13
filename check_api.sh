#!/bin/bash
# APIサーバーの状態確認スクリプト

echo "🔍 APIサーバーの状態を確認します..."
echo ""

# ポート確認
if lsof -ti:8010 > /dev/null 2>&1; then
    echo "✅ ポート8010は使用中"
    PID=$(lsof -ti:8010 | head -1)
    echo "   PID: $PID"
else
    echo "❌ ポート8010は使用されていません"
    exit 1
fi

# ヘルスチェック
echo ""
echo "🔍 ヘルスチェックを実行..."
response=$(curl -s --max-time 5 http://127.0.0.1:8010/health 2>&1)
if [ "$response" = '{"ok":true}' ]; then
    echo "✅ APIサーバーは正常に応答しています"
else
    echo "❌ APIサーバーが応答していません"
    echo "   レスポンス: $response"
    exit 1
fi

# 実際にコメント生成をテスト
echo ""
echo "🔍 コメント生成APIをテスト..."
test_response=$(curl -s -X POST http://127.0.0.1:8010/generate_direct \
    -H "Content-Type: application/json" \
    -d '{"text": "テスト", "type": "reflection"}' \
    --max-time 10 2>&1)

if echo "$test_response" | grep -q "ai_comment"; then
    echo "✅ コメント生成APIは正常に動作しています"
    comment_length=$(echo "$test_response" | python3 -c "import sys, json; print(len(json.load(sys.stdin).get('ai_comment', '')))" 2>/dev/null || echo "N/A")
    echo "   生成されたコメント長: $comment_length 文字"
else
    echo "❌ コメント生成APIがエラーを返しました"
    echo "   レスポンス: ${test_response:0:200}..."
    exit 1
fi

echo ""
echo "✅ すべてのチェックが完了しました"

