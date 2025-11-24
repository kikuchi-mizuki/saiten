# Python 3.9 ベースイメージ
FROM python:3.9-slim

# 作業ディレクトリ
WORKDIR /app

# システムパッケージのインストール（ffmpeg含む）
RUN apt-get update && \
    apt-get install -y ffmpeg && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# requirements.txtをコピーして依存関係をインストール
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# アプリケーションコードをコピー
COPY . .

# ポート8080を公開
EXPOSE 8080

# Uvicornでアプリケーションを起動
CMD ["uvicorn", "api.main:app", "--host", "0.0.0.0", "--port", "8080"]
