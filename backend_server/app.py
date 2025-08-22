from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Optional
import pickle
import pandas as pd
import numpy as np
import os
from datetime import datetime

app = FastAPI(title="コーヒー抽出予測API", description="天気、日付などの条件からコーヒーの抽出結果を予測するAPI")

# モデルと前処理情報の読み込み
def load_model():
    try:
        with open('model/random_forest_model.pkl', 'rb') as f:
            model = pickle.load(f)
        with open('model/preprocessing_info.pkl', 'rb') as f:
            preprocessing_info = pickle.load(f)
        return model, preprocessing_info
    except FileNotFoundError:
        raise HTTPException(status_code=500, detail="モデルファイルが見つかりません。先にtrain.pyを実行してください。")

model, preprocessing_info = load_model()

# 入力データのモデル
class PredictionInput(BaseModel):
    day: int
    month: int
    year: int
    weather: str
    days_passed: Optional[float] = None
    temperature: Optional[float] = None
    humidity: Optional[float] = None

# 予測結果のモデル
class PredictionOutput(BaseModel):
    mesh: float
    gram: float
    extraction_time: float

@app.get("/")
async def root():
    return {"message": "コーヒー抽出予測APIへようこそ！", "version": "1.0.0"}

@app.get("/health")
async def health_check():
    return {"status": "healthy", "model_loaded": model is not None}

@app.post("/predict", response_model=PredictionOutput)
async def predict(input_data: PredictionInput):
    try:
        # 入力データをDataFrameに変換
        input_df = pd.DataFrame([{
            'Day': input_data.day,
            'Month': input_data.month,
            'Year': input_data.year,
            'Weather': input_data.weather,
            'days_passed': input_data.days_passed if input_data.days_passed is not None else 15.0,
            'temperature': input_data.temperature if input_data.temperature is not None else 20.0,
            'humidity': input_data.humidity if input_data.humidity is not None else 60.0
        }])
        
        # 天気のOne-Hotエンコーディング
        weather_dummies = pd.get_dummies(input_df['Weather'], prefix='Weather')
        input_df = pd.concat([input_df.drop('Weather', axis=1), weather_dummies], axis=1)
        
        # 不足している天気カテゴリを追加（0で埋める）
        expected_weather_columns = [col for col in preprocessing_info['feature_names'] if col.startswith('Weather_')]
        for col in expected_weather_columns:
            if col not in input_df.columns:
                input_df[col] = 0
        
        # 特徴量の順序を統一
        input_df = input_df[preprocessing_info['feature_names']]
        
        # 予測実行
        prediction = model.predict(input_df)
        
        # 結果を返す
        return PredictionOutput(
            mesh=float(prediction[0][0]),
            gram=float(prediction[0][1]),
            extraction_time=float(prediction[0][2])
        )
        
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"予測エラー: {str(e)}")

@app.get("/model-info")
async def get_model_info():
    return {
        "feature_names": preprocessing_info['feature_names'],
        "target_names": preprocessing_info['target_names'],
        "model_type": "RandomForestRegressor",
        "n_estimators": model.n_estimators if hasattr(model, 'n_estimators') else None
    }

@app.get("/current-weather")
async def get_current_weather():
    """現在の京都の気象データを取得"""
    try:
        from weather_data import WeatherDataCollector
        collector = WeatherDataCollector()
        weather = collector.get_current_weather()
        
        if weather:
            return {
                "location": "京都府京都市左京区",
                "temperature": weather['temperature'],
                "humidity": weather['humidity'],
                "timestamp": datetime.now().isoformat()
            }
        else:
            return {
                "location": "京都府京都市左京区",
                "temperature": 20.0,  # デフォルト値
                "humidity": 60.0,     # デフォルト値
                "timestamp": datetime.now().isoformat(),
                "note": "APIキーが設定されていないため、デフォルト値を使用しています"
            }
    except Exception as e:
        return {
            "location": "京都府京都市左京区",
            "temperature": 20.0,
            "humidity": 60.0,
            "timestamp": datetime.now().isoformat(),
            "error": str(e)
        }

@app.post("/predict-batch")
async def predict_batch(inputs: List[PredictionInput]):
    try:
        results = []
        for input_data in inputs:
            # 個別予測と同じ処理
            input_df = pd.DataFrame([{
                'Day': input_data.day,
                'Month': input_data.month,
                'Year': input_data.year,
                'Weather': input_data.weather,
                'days_passed': input_data.days_passed if input_data.days_passed is not None else 15.0,
                'temperature': input_data.temperature if input_data.temperature is not None else 20.0,
                'humidity': input_data.humidity if input_data.humidity is not None else 60.0
            }])
            
            weather_dummies = pd.get_dummies(input_df['Weather'], prefix='Weather')
            input_df = pd.concat([input_df.drop('Weather', axis=1), weather_dummies], axis=1)
            
            expected_weather_columns = [col for col in preprocessing_info['feature_names'] if col.startswith('Weather_')]
            for col in expected_weather_columns:
                if col not in input_df.columns:
                    input_df[col] = 0
            
            input_df = input_df[preprocessing_info['feature_names']]
            prediction = model.predict(input_df)
            
            results.append({
                "mesh": float(prediction[0][0]),
                "gram": float(prediction[0][1]),
                "extraction_time": float(prediction[0][2])
            })
        
        return {"predictions": results}
        
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"バッチ予測エラー: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8081)
