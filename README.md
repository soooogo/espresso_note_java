# Espresso Note Java - コーヒー抽出予測アプリケーション

## 概要

Espresso Note Javaは、機械学習を使用してコーヒーの抽出パラメータ（粉量、挽き目、抽出時間）を予測するWebアプリケーションです。Spring Boot（フロントエンド）とFastAPI（バックエンド）を組み合わせたマイクロサービス構成で構築されています。

## 主な機能

- **ユーザー認証**: ログイン・新規登録機能
- **コーヒー豆管理**: ユーザーごとのコーヒー豆登録・管理
- **抽出予測**: 機械学習モデルによる抽出パラメータの予測
- **レシピ管理**: 過去の抽出レシピの記録・参照
- **多言語対応**: 日本語UI対応

## 技術スタック

### フロントエンド
- **Spring Boot 3.4.8** - Webアプリケーションフレームワーク
- **Thymeleaf** - テンプレートエンジン
- **Spring Security** - 認証・認可
- **Spring Data JPA** - データアクセス層
- **MySQL Connector** - データベース接続

### バックエンド
- **FastAPI 0.104.1** - REST API フレームワーク
- **scikit-learn** - 機械学習ライブラリ
- **pandas** - データ処理
- **numpy** - 数値計算
- **mysql-connector-python** - データベース接続

### インフラ
- **Docker & Docker Compose** - コンテナ化
- **MySQL 8.0** - データベース
- **Maven** - Java依存関係管理

## アーキテクチャ

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Spring Boot   │    │     FastAPI     │    │      MySQL      │
│   (Frontend)    │◄──►│   (Backend)     │◄──►│   (Database)    │
│   Port: 8080    │    │   Port: 8081    │    │   Port: 3306    │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

## セットアップ

### 前提条件

- Docker & Docker Compose
- Git

### インストール・起動

1. **リポジトリのクローン**
```bash
git clone https://github.com/soooogo/espresso_note_java.git
cd espresso_note_java
```

2. **Docker Composeで起動**
```bash
docker compose up -d
```

3. **アプリケーションアクセス**
- フロントエンド: http://localhost:8080
- バックエンドAPI: http://localhost:8081
- データベース: localhost:3306

### 初期データ

アプリケーション起動時に以下のデータが自動挿入されます：

- **ユーザー**: 3名（管理者、コーヒー愛好家、ホームロースター）
- **コーヒー豆**: 8種類（エチオピア、グアテマラ、ケニアなど）
- **レシピデータ**: 195件（CSVファイルから読み込み）

## 使用方法

### 1. ログイン
- デフォルトユーザーでログイン
- 新規登録も可能

### 2. 予測機能
1. `/predict` ページにアクセス
2. コーヒー豆を選択
3. 気象条件を入力（気温、湿度、経過日数）
4. 予測結果を確認

### 3. レシピ管理
- `/recipes` ページで過去のレシピを確認
- 抽出パラメータの履歴を参照

## API仕様

### 認証エンドポイント
- `POST /api/users/register` - ユーザー登録
- `POST /login` - ログイン

### 予測エンドポイント
- `GET /api/predict/user-beans` - ユーザーのコーヒー豆一覧
- `POST /api/predict/coffee` - 抽出パラメータ予測

### レシピエンドポイント
- `GET /api/recipes` - レシピ一覧
- `POST /api/recipes` - レシピ登録

## データベース設計

### 主要テーブル
- **users**: ユーザー情報
- **beans**: コーヒー豆情報
- **recipes**: 抽出レシピデータ
- **weather_data**: 気象データ

### 文字エンコーディング
- MySQL: `utf8mb4` (日本語対応)
- Spring Boot: `characterEncoding=utf8&useUnicode=true`

## 機械学習モデル

### 特徴量
- 気温 (temperature)
- 湿度 (humidity)
- 経過日数 (days_passed)
- 日付情報 (年、月、日、曜日)
- コーヒー豆情報

### 予測対象
- 粉量 (gram)
- 挽き目 (mesh)
- 抽出時間 (extraction_time)

### モデル
- RandomForestRegressor
- 豆種別の個別モデル対応

## 開発

### ローカル開発環境

1. **バックエンド開発**
```bash
cd backend_server
pip install -r requirements.txt
python app_mysql.py
```

2. **フロントエンド開発**
```bash
cd frontend_server/demo
./mvnw spring-boot:run
```

### データベース接続
```bash
mysql -h localhost -P 3306 -u demo_user -p demo_db
# パスワード: demo_password
```

## トラブルシューティング

### よくある問題

1. **データベース接続エラー**
   - MySQLサービスが起動しているか確認
   - ポート3306が使用可能か確認

2. **日本語文字化け**
   - MySQLの文字セット設定を確認
   - Spring Bootの接続URL設定を確認

3. **予測API接続エラー**
   - FastAPIサービスが起動しているか確認
   - ポート8081が使用可能か確認

### ログ確認
```bash
# Spring Bootログ
docker logs coffee_springboot

# FastAPIログ
docker logs coffee_fastapi

# MySQLログ
docker logs coffee_mysql
```

## ライセンス

このプロジェクトはMITライセンスの下で公開されています。

## 貢献

プルリクエストやイシューの報告を歓迎します。

## 更新履歴

- v1.0.0: 初回リリース
  - 基本的な予測機能
  - ユーザー認証
  - レシピ管理
  - Docker対応
