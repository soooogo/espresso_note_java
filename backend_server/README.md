# コーヒー抽出予測API

天気、日付、気温、湿度などの条件からコーヒーの抽出結果（メッシュ、グラム、抽出時間）を予測するFastAPIアプリケーションです。

## 機能
- 京都府京都市左京区の気象データ（気温・湿度）を取得
- 気象データを含む高精度な予測
- 現在の気象データの取得
- バッチ予測対応

## セットアップ

### 1. 依存関係のインストール
```bash
pip install -r requirements.txt
```

### 2. 気象データの準備
```bash
python weather_data.py
```

### 3. モデルの学習と保存
```bash
python train.py
```

### 4. APIサーバーの起動
```bash
python app.py
```

または
```bash
uvicorn app:app --host 0.0.0.0 --port 8000 --reload
```

## API エンドポイント

### 1. ヘルスチェック
```
GET /health
```

### 2. 単一予測
```
POST /predict
```

**リクエスト例:**
```json
{
  "day": 15,
  "month": 3,
  "year": 2025,
  "weather": "晴",
  "days_passed": 12.5,
  "temperature": 18.5,
  "humidity": 65.0
}
```

**レスポンス例:**
```json
{
  "mesh": 16.2,
  "gram": 15.8,
  "extraction_time": 28.5
}
```

### 3. バッチ予測
```
POST /predict-batch
```

**リクエスト例:**
```json
[
  {
    "day": 15,
    "month": 3,
    "year": 2025,
    "weather": "晴",
    "days_passed": 12.5
  },
  {
    "day": 16,
    "month": 3,
    "year": 2025,
    "weather": "くもり",
    "days_passed": 13.0
  }
]
```

### 4. 現在の気象データ
```
GET /current-weather
```

### 5. モデル情報
```
GET /model-info
```

## 入力パラメータ

### 天気の選択肢
- 晴
- くもり
- 雨
- 雪
- 晴/くもり

### 気象データ
- **temperature**: 気温（摂氏、省略時は20.0℃）
- **humidity**: 湿度（%、省略時は60.0%）

### 注意事項
- OpenWeatherMap APIキーを設定すると、実際の気象データを取得できます
- APIキーがない場合は、季節に応じたモックデータが生成されます

## 自動生成ドキュメント
APIサーバー起動後、以下のURLで自動生成されたドキュメントを確認できます：
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc
