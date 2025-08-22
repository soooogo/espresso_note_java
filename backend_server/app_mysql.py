from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Optional
import pickle
import pandas as pd
import numpy as np
import os
from datetime import datetime
import mysql.connector

app = FastAPI(title="コーヒー抽出予測API (MySQL版)", description="MySQLのdemo_dbから学習したモデルでコーヒーの抽出結果を予測するAPI")

# モデルと前処理情報の読み込み
def load_mysql_model():
    try:
        with open('model/random_forest_mysql_model.pkl', 'rb') as f:
            model = pickle.load(f)
        with open('model/preprocessing_info_mysql.pkl', 'rb') as f:
            preprocessing_info = pickle.load(f)
        return model, preprocessing_info
    except FileNotFoundError:
        raise HTTPException(status_code=500, detail="MySQLモデルファイルが見つかりません。先にtrain_mysql.pyを実行してください。")

model, preprocessing_info = load_mysql_model()

# MySQL接続設定
mysql_config = {
    'host': 'localhost',
    'user': 'root',
    'password': '',
    'database': 'demo_db',
    'charset': 'utf8mb4'
}

# 入力データのモデル
class PredictionInput(BaseModel):
    bean_name: str
    bean_origin: str
    date: str  # YYYY-MM-DD形式
    weather: str
    temperature: Optional[float] = None
    humidity: Optional[float] = None

# 予測結果のモデル
class PredictionOutput(BaseModel):
    mesh: float
    gram: float
    extraction_time: float
    confidence: float

# 豆情報のモデル
class BeanInfo(BaseModel):
    id: int
    name: str
    origin: str
    user_name: str

@app.get("/")
async def root():
    return {
        "message": "コーヒー抽出予測API (MySQL版)へようこそ！", 
        "version": "2.0.0",
        "data_source": "mysql_demo_db"
    }

@app.get("/health")
async def health_check():
    return {
        "status": "healthy", 
        "model_loaded": model is not None,
        "data_source": "mysql_demo_db"
    }

@app.get("/beans", response_model=List[BeanInfo])
async def get_beans():
    """利用可能なコーヒー豆の一覧を取得"""
    try:
        connection = mysql.connector.connect(**mysql_config)
        cursor = connection.cursor()
        
        query = """
        SELECT b.id, b.name, b.from_location, u.name as user_name
        FROM beans b
        JOIN users u ON b.user_id = u.id
        ORDER BY b.name
        """
        
        cursor.execute(query)
        beans = []
        for row in cursor.fetchall():
            beans.append(BeanInfo(
                id=row[0],
                name=row[1],
                origin=row[2],
                user_name=row[3]
            ))
        
        cursor.close()
        connection.close()
        
        return beans
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"豆情報の取得エラー: {str(e)}")

@app.get("/user-beans", response_model=List[BeanInfo])
async def get_user_beans():
    """現在のユーザーのコーヒー豆の一覧を取得（全ユーザー）"""
    try:
        connection = mysql.connector.connect(**mysql_config)
        cursor = connection.cursor()
        
        # 現在は全ユーザーの豆を返す（認証機能が実装されていないため）
        # 将来的には認証情報からユーザーIDを取得する
        query = """
        SELECT b.id, b.name, b.from_location, u.name as user_name
        FROM beans b
        JOIN users u ON b.user_id = u.id
        ORDER BY b.name
        """
        
        cursor.execute(query)
        beans = []
        for row in cursor.fetchall():
            beans.append(BeanInfo(
                id=row[0],
                name=row[1],
                origin=row[2],
                user_name=row[3]
            ))
        
        cursor.close()
        connection.close()
        
        return beans
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"ユーザー豆情報の取得エラー: {str(e)}")

@app.get("/user-beans/{user_id}", response_model=List[BeanInfo])
async def get_user_beans_by_id(user_id: int):
    """指定されたユーザーIDのコーヒー豆の一覧を取得"""
    try:
        connection = mysql.connector.connect(**mysql_config)
        cursor = connection.cursor()
        
        query = """
        SELECT b.id, b.name, b.from_location, u.name as user_name
        FROM beans b
        JOIN users u ON b.user_id = u.id
        WHERE b.user_id = %s
        ORDER BY b.name
        """
        
        cursor.execute(query, (user_id,))
        beans = []
        for row in cursor.fetchall():
            beans.append(BeanInfo(
                id=row[0],
                name=row[1],
                origin=row[2],
                user_name=row[3]
            ))
        
        cursor.close()
        connection.close()
        
        return beans
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"ユーザー豆情報の取得エラー: {str(e)}")

@app.post("/predict", response_model=PredictionOutput)
async def predict(input_data: PredictionInput):
    """単一予測"""
    try:
        # 日付を解析
        date_obj = datetime.strptime(input_data.date, "%Y-%m-%d")
        
        # 入力データをDataFrameに変換
        input_df = pd.DataFrame([{
            'year': date_obj.year,
            'month': date_obj.month,
            'day': date_obj.day,
            'day_of_week': date_obj.weekday(),
            'weather': input_data.weather,
            'temperature': input_data.temperature if input_data.temperature is not None else 20.0,
            'humidity': input_data.humidity if input_data.humidity is not None else 60.0,
            'bean_origin': input_data.bean_origin
        }])
        
        # 天気のOne-Hotエンコーディング
        weather_dummies = pd.get_dummies(input_df['weather'], prefix='weather')
        input_df = pd.concat([input_df.drop('weather', axis=1), weather_dummies], axis=1)
        
        # 豆の産地のOne-Hotエンコーディング
        origin_dummies = pd.get_dummies(input_df['bean_origin'], prefix='origin')
        input_df = pd.concat([input_df.drop('bean_origin', axis=1), origin_dummies], axis=1)
        
        # 不足しているカテゴリを追加（0で埋める）
        expected_weather_columns = [col for col in preprocessing_info['feature_names'] if col.startswith('weather_')]
        expected_origin_columns = [col for col in preprocessing_info['feature_names'] if col.startswith('origin_')]
        
        for col in expected_weather_columns:
            if col not in input_df.columns:
                input_df[col] = 0
        
        for col in expected_origin_columns:
            if col not in input_df.columns:
                input_df[col] = 0
        
        # 特徴量の順序を統一
        input_df = input_df[preprocessing_info['feature_names']]
        
        # 予測実行
        prediction = model.predict(input_df)
        
        # 信頼度の計算（簡易版）
        confidence = 0.85  # 実際のモデルでは予測の不確実性を計算
        
        # 結果を返す
        return PredictionOutput(
            mesh=float(prediction[0][0]),
            gram=float(prediction[0][1]),
            extraction_time=float(prediction[0][2]),
            confidence=confidence
        )
        
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"予測エラー: {str(e)}")

@app.post("/predict-batch")
async def predict_batch(inputs: List[PredictionInput]):
    """バッチ予測"""
    try:
        results = []
        for input_data in inputs:
            # 個別予測と同じ処理
            date_obj = datetime.strptime(input_data.date, "%Y-%m-%d")
            
            input_df = pd.DataFrame([{
                'year': date_obj.year,
                'month': date_obj.month,
                'day': date_obj.day,
                'day_of_week': date_obj.weekday(),
                'weather': input_data.weather,
                'temperature': input_data.temperature if input_data.temperature is not None else 20.0,
                'humidity': input_data.humidity if input_data.humidity is not None else 60.0,
                'bean_origin': input_data.bean_origin
            }])
            
            weather_dummies = pd.get_dummies(input_df['weather'], prefix='weather')
            input_df = pd.concat([input_df.drop('weather', axis=1), weather_dummies], axis=1)
            
            origin_dummies = pd.get_dummies(input_df['bean_origin'], prefix='origin')
            input_df = pd.concat([input_df.drop('bean_origin', axis=1), origin_dummies], axis=1)
            
            expected_weather_columns = [col for col in preprocessing_info['feature_names'] if col.startswith('weather_')]
            expected_origin_columns = [col for col in preprocessing_info['feature_names'] if col.startswith('origin_')]
            
            for col in expected_weather_columns:
                if col not in input_df.columns:
                    input_df[col] = 0
            
            for col in expected_origin_columns:
                if col not in input_df.columns:
                    input_df[col] = 0
            
            input_df = input_df[preprocessing_info['feature_names']]
            prediction = model.predict(input_df)
            
            results.append({
                "bean_name": input_data.bean_name,
                "bean_origin": input_data.bean_origin,
                "date": input_data.date,
                "weather": input_data.weather,
                "temperature": input_data.temperature,
                "humidity": input_data.humidity,
                "mesh": float(prediction[0][0]),
                "gram": float(prediction[0][1]),
                "extraction_time": float(prediction[0][2]),
                "confidence": 0.85
            })
        
        return {"predictions": results}
        
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"バッチ予測エラー: {str(e)}")

@app.get("/model-info")
async def get_model_info():
    """モデル情報の取得"""
    return {
        "feature_names": preprocessing_info['feature_names'],
        "target_names": preprocessing_info['target_names'],
        "model_type": "RandomForestRegressor",
        "n_estimators": model.n_estimators if hasattr(model, 'n_estimators') else None,
        "data_source": preprocessing_info.get('data_source', 'mysql_demo_db'),
        "categorical_columns": preprocessing_info.get('categorical_columns', []),
        "numerical_columns": preprocessing_info.get('numerical_columns', [])
    }

@app.get("/database-stats")
async def get_database_stats():
    """データベースの統計情報を取得"""
    try:
        connection = mysql.connector.connect(**mysql_config)
        cursor = connection.cursor()
        
        # 各テーブルのレコード数を取得
        cursor.execute("SELECT COUNT(*) FROM users")
        user_count = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM beans")
        bean_count = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM recipe")
        recipe_count = cursor.fetchone()[0]
        
        cursor.close()
        connection.close()
        
        return {
            "user_count": user_count,
            "bean_count": bean_count,
            "recipe_count": recipe_count,
            "total_records": user_count + bean_count + recipe_count
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"データベース統計の取得エラー: {str(e)}")

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
                "temperature": 20.0,
                "humidity": 60.0,
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

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8081)
