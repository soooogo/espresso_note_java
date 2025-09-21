#!/bin/bash

echo "🧪 Docker環境の動作確認を開始します..."

# サービスの状態確認
echo "📊 サービス状態確認..."
docker compose ps

# ヘルスチェック
echo "🔍 ヘルスチェック..."

# FastAPI ヘルスチェック
echo "FastAPI ヘルスチェック..."
curl -s http://localhost:8081/health | jq . || echo "FastAPI ヘルスチェック失敗"

# Spring Boot ヘルスチェック
echo "Spring Boot ヘルスチェック..."
curl -s http://localhost:8080/ | head -20 || echo "Spring Boot ヘルスチェック失敗"

# データベース接続確認
echo "MySQL 接続確認..."
docker compose exec mysql mysql -u demo_user -p'demo_password' -e "SELECT 'MySQL接続成功' as status;" 2>/dev/null || echo "MySQL 接続失敗"

# ログ確認
echo "📋 最近のログ確認..."
echo "=== FastAPI ログ ==="
docker compose logs --tail=10 fastapi
echo ""
echo "=== Spring Boot ログ ==="
docker compose logs --tail=10 springboot
echo ""
echo "=== MySQL ログ ==="
docker compose logs --tail=5 mysql

echo ""
echo "✅ 動作確認完了！"
echo ""
echo "📱 アクセスURL:"
echo "   - フロントエンド: http://localhost:8080"
echo "   - バックエンド: http://localhost:8081"
echo "   - API ドキュメント: http://localhost:8081/docs"
