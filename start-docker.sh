#!/bin/bash

echo "🚀 コーヒー抽出予測アプリケーションをDockerで起動します..."

# 既存のコンテナを停止・削除
echo "📦 既存のコンテナをクリーンアップ..."
docker compose down -v

# イメージをビルド
echo "🔨 Dockerイメージをビルド..."
docker compose build --no-cache

# サービスを起動
echo "🌟 サービスを起動..."
docker compose up -d

# 起動状況を確認
echo "⏳ サービス起動を待機中..."
sleep 30

# ヘルスチェック
echo "🔍 サービスヘルスチェック..."
docker compose ps

echo ""
echo "✅ アプリケーションが起動しました！"
echo ""
echo "📱 アクセスURL:"
echo "   - フロントエンド (Spring Boot): http://localhost:8080"
echo "   - バックエンド (FastAPI): http://localhost:8081"
echo "   - FastAPI ドキュメント: http://localhost:8081/docs"
echo ""
echo "🗄️  データベース:"
echo "   - MySQL: localhost:3306"
echo "   - ユーザー: demo_user"
echo "   - パスワード: demo_password"
echo "   - データベース: demo_db"
echo ""
echo "📋 ログを確認するには:"
echo "   docker compose logs -f"
echo ""
echo "🛑 停止するには:"
echo "   docker compose down"
