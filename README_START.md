# サーバー起動手順

## 1. APIサーバーの起動

```bash
cd /Users/kikuchimizuki/Desktop/02_榎戸さん_採点システム/saiten
python3 -m uvicorn api.main:app --reload --port 8010
```

正常に起動すると、以下のメッセージが表示されます：
```
INFO:     Uvicorn running on http://127.0.0.1:8010
```

## 2. UIサーバー（Streamlit）の起動

**新しいターミナルウィンドウ**を開いて、以下を実行：

```bash
cd /Users/kikuchimizuki/Desktop/02_榎戸さん_採点システム/saiten
python3 -m streamlit run app/streamlit_app.py
```

または、起動スクリプトを使用：

```bash
cd /Users/kikuchimizuki/Desktop/02_榎戸さん_採点システム/saiten
./start_ui.sh
```

初回起動時は、メールアドレスの入力が求められる場合があります。その場合は**Enterキーを押してスキップ**してください。

正常に起動すると、ブラウザが自動的に開き、以下のURLが表示されます：
```
http://localhost:8501
```

## 3. ブラウザでアクセス

- UI: http://localhost:8501
- API: http://127.0.0.1:8010/health

## トラブルシューティング

### ポートが既に使用されている場合

- ポート8010（API）が使用中: `lsof -ti:8010 | xargs kill -9`
- ポート8501（UI）が使用中: `lsof -ti:8501 | xargs kill -9`

### Streamlitが起動しない場合

```bash
# Streamlitの設定をリセット
rm -rf ~/.streamlit
mkdir -p ~/.streamlit

# 再起動
python3 -m streamlit run app/streamlit_app.py
```

### パッケージが不足している場合

```bash
pip3 install -r requirements.txt
```

