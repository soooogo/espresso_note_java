# コーヒー抽出予測API (MySQL版)

MySQLのdemo_dbからデータを取得して学習したモデルで、コーヒーの抽出結果（メッシュ、グラム、抽出時間）を予測するFastAPIアプリケーションです。

## 概要

このシステムは以下の流れで動作します：

1. **MySQLデータベース**からレシピデータを取得
2. **気象データ**（京都府京都市左京区）と組み合わせ
3. **機械学習モデル**で学習
4. **FastAPI**で予測APIを提供

## 機能

- MySQLのdemo_dbからリアルタイムでデータ取得
- 京都の気象データ（気温・湿度）を組み込み
- コーヒー豆の産地別予測
- 天気条件による予測調整
- バッチ予測対応
- データベース統計情報の取得

## セットアップ

### 1. 依存関係のインストール
```bash
pip install -r requirements.txt
```

### 2. MySQLデータベースの準備
- MySQLサーバーが起動していることを確認
- `demo_db`データベースが存在することを確認
- フロントエンドアプリケーションでサンプルデータが作成されていることを確認

### 3. 気象データの準備
```bash
python weather_data.py
```

### 4. MySQLデータの準備
```bash
python mysql_data_loader.py
```

### 5. モデルの学習
```bash
python train_mysql.py
```

### 6. APIサーバーの起動
```bash
python app_mysql.py
```

または
```bash
uvicorn app_mysql:app --host 0.0.0.0 --port 8001 --reload
```

## API エンドポイント

### 1. ヘルスチェック
```
GET /health
```

### 2. データベース統計
```
GET /database-stats
```

### 3. 豆情報取得
```
GET /beans
```

### 4. 単一予測
```
POST /predict
```

**リクエスト例:**
```json
{
  "bean_name": "エチオピア イルガチェフェ",
  "bean_origin": "エチオピア",
  "date": "2025-03-15",
  "weather": "晴れ",
  "temperature": 18.5,
  "humidity": 65.0
}
```

**レスポンス例:**
```json
{
  "mesh": 18.2,
  "gram": 2.4,
  "extraction_time": 28.5,
  "confidence": 0.85
}
```

### 5. バッチ予測
```
POST /predict-batch
```

### 6. モデル情報
```
GET /model-info
```

### 7. 現在の気象データ
```
GET /current-weather
```

## データベース構造

### テーブル構成
- **user**: ユーザー情報
- **beans**: コーヒー豆情報
- **recipe**: 抽出レシピ情報

### 主要な特徴量
- **日付情報**: year, month, day, day_of_week
- **気象データ**: temperature, humidity
- **天気**: weather (One-Hotエンコーディング)
- **豆の産地**: bean_origin (One-Hotエンコーディング)

## 予測対象

- **mesh**: メッシュ（粉の細かさ）
- **gram**: グラム（抽出量）
- **extraction_time**: 抽出時間

## 天気の選択肢
- 晴れ
- 曇り
- 雨
- 雪

## 豆の産地
- エチオピア
- グアテマラ
- ブラジル
- コロンビア
- ケニア
- インドネシア
- パナマ
- タンザニア

## テスト

```bash
python test_mysql_api.py
```

## 自動生成ドキュメント
APIサーバー起動後、以下のURLで自動生成されたドキュメントを確認できます：
- Swagger UI: http://localhost:8001/docs
- ReDoc: http://localhost:8001/redoc

## 注意事項

- MySQLサーバーが起動している必要があります
- demo_dbデータベースにデータが存在する必要があります
- 初回実行時はサンプルデータが自動生成されます
- OpenWeatherMap APIキーを設定すると、実際の気象データを取得できます

## ポート設定

- **MySQL版API**: ポート8001
- **従来版API**: ポート8000

両方のAPIを同時に起動して比較することも可能です。
