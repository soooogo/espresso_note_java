# コーヒー抽出予測アプリケーション - Docker版

## 🚀 クイックスタート

### 前提条件
- Docker
- Docker Compose

### 起動方法

1. **自動起動スクリプトを使用**
```bash
./start-docker.sh
```

2. **手動で起動**
```bash
# イメージをビルド
docker compose build

# サービスを起動
docker compose up -d

# ログを確認
docker compose logs -f
```

3. **データ挿入タイプを指定して起動**
```bash
# 最終データ挿入（Spring Boot完了後、デフォルト）
DATA_INSERT_TYPE=final docker compose up -d

# 月別CSVデータ挿入
DATA_INSERT_TYPE=monthly docker compose up -d

# データ挿入なし
DATA_INSERT_TYPE=none docker compose up -d
```

## 📱 アクセスURL

| サービス | URL | 説明 |
|---------|-----|------|
| フロントエンド | http://localhost:8080 | Spring Bootアプリケーション |
| バックエンド | http://localhost:8081 | FastAPIアプリケーション |
| API ドキュメント | http://localhost:8081/docs | FastAPI自動生成ドキュメント |
| ヘルスチェック | http://localhost:8081/health | システム状態確認 |

## 🗄️ データベース情報

| 項目 | 値 |
|------|-----|
| ホスト | localhost:3306 |
| ユーザー | demo_user |
| パスワード | demo_password |
| データベース | demo_db |

## 🐳 Dockerサービス構成

### 1. MySQL (mysql)
- **イメージ**: mysql:8.0
- **ポート**: 3306
- **データ永続化**: Docker volume
- **初期化**: mysql_init/01-init.sql

### 2. FastAPI (fastapi)
- **ベースイメージ**: python:3.11-slim
- **ポート**: 8081
- **機能**: 機械学習予測API
- **ボリューム**: ./backend_server/model

### 3. Spring Boot (springboot)
- **ベースイメージ**: openjdk:17-jdk-slim
- **ポート**: 8080
- **機能**: Webアプリケーション
- **依存関係**: MySQL, FastAPI

## 🔧 管理コマンド

### サービスの状態確認
```bash
docker-compose ps
```

### ログの確認
```bash
# 全サービスのログ
docker-compose logs -f

# 特定サービスのログ
docker-compose logs -f fastapi
docker-compose logs -f springboot
docker-compose logs -f mysql
```

### サービスの停止
```bash
docker-compose down
```

### データベースのリセット
```bash
docker-compose down -v
docker-compose up -d
```

### イメージの再ビルド
```bash
docker-compose build --no-cache
docker-compose up -d
```

## 🔍 トラブルシューティング

### 1. ポートが既に使用されている場合
```bash
# 使用中のポートを確認
lsof -i :8080
lsof -i :8081
lsof -i :3306

# 既存のプロセスを停止
docker-compose down
```

### 2. データベース接続エラー
```bash
# MySQLコンテナの状態確認
docker-compose logs mysql

# MySQLコンテナに接続
docker-compose exec mysql mysql -u demo_user -p demo_db
```

### 3. アプリケーションが起動しない
```bash
# ログを確認
docker-compose logs -f springboot
docker-compose logs -f fastapi

# コンテナを再起動
docker-compose restart springboot
docker-compose restart fastapi
```

## 📁 ファイル構成

```
.
├── docker-compose.yml          # Docker Compose設定
├── start-docker.sh            # 起動スクリプト
├── mysql_init/                # MySQL初期化スクリプト
│   └── 01-init.sql
├── frontend_server/demo/      # Spring Bootアプリケーション
│   ├── Dockerfile
│   └── .dockerignore
└── backend_server/            # FastAPIアプリケーション
    ├── Dockerfile
    ├── .dockerignore
    └── model/                 # 機械学習モデル（ボリュームマウント）
```

## 🔄 開発環境での使用

### コード変更時の再ビルド
```bash
# 特定サービスのみ再ビルド
docker-compose build springboot
docker-compose build fastapi

# サービスを再起動
docker-compose up -d
```

### ホットリロード（開発用）
開発時は、ソースコードをボリュームマウントしてホットリロードを有効にできます：

```yaml
# docker-compose.yml に追加
volumes:
  - ./frontend_server/demo/src:/app/src
  - ./backend_server:/app
```

## 🚀 本番環境での使用

本番環境では以下の設定を推奨します：

1. **環境変数の外部化**
2. **SSL/TLS証明書の設定**
3. **ログローテーションの設定**
4. **バックアップ戦略の実装**
5. **監視・アラートの設定**

## 📞 サポート

問題が発生した場合は、以下を確認してください：

1. DockerとDocker Composeのバージョン
2. システムリソース（メモリ、ディスク容量）
3. ファイアウォール設定
4. ポートの競合
