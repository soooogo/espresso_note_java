#!/bin/bash

echo "🚀 FastAPIコンテナを起動中..."

# 環境変数でデータ挿入タイプを制御
DATA_INSERT_TYPE=${DATA_INSERT_TYPE:-"final"}

case $DATA_INSERT_TYPE in
    "monthly")
        echo "📊 月別CSVデータ挿入スクリプトを実行..."
        python /app/insert_data_to_mysql.py &
        ;;
    "final")
        echo "📊 データ挿入スクリプトを実行（Spring Boot完了後）..."
        python /app/insert_data.py &
        ;;
    "none")
        echo "⏭️  データ挿入をスキップ..."
        ;;
    *)
        echo "📊 デフォルト: データ挿入スクリプトを実行..."
        python /app/insert_data.py &
        ;;
esac

# FastAPIを起動
exec uvicorn app_mysql:app --host 0.0.0.0 --port 8081
