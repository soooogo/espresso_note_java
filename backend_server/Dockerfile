FROM python:3.11-slim

WORKDIR /app

# システムの依存関係をインストール
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

# Pythonの依存関係をコピーしてインストール
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# アプリケーションコードをコピー
COPY . .

# modelディレクトリを作成
RUN mkdir -p model

# ポート8081を公開
EXPOSE 8081

# データ挿入スクリプトをコピー
COPY insert_data.py /app/insert_data.py
RUN chmod +x /app/insert_data.py

# アプリケーションを起動
CMD ["uvicorn", "app_mysql:app", "--host", "0.0.0.0", "--port", "8081"]
