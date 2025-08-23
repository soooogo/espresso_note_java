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

# 豆ごとのモデルと前処理情報の読み込み（オプション）
def load_bean_specific_models():
    try:
        # 豆ごとのモデル情報を読み込み
        with open('model/bean_models_info.pkl', 'rb') as f:
            bean_models_info = pickle.load(f)
        
        bean_models = {}
        bean_preprocessing_info = {}
        
        # 各豆のモデルと前処理情報を読み込み
        for bean_name, info in bean_models_info.items():
            try:
                with open(info['model_file'], 'rb') as f:
                    bean_models[bean_name] = pickle.load(f)
                with open(info['preprocessing_file'], 'rb') as f:
                    bean_preprocessing_info[bean_name] = pickle.load(f)
                print(f"{bean_name}の保存済みモデルを読み込みました")
            except Exception as e:
                print(f"{bean_name}のモデル読み込みに失敗: {e}")
        
        print(f"保存済みモデル読み込み完了: {len(bean_models)}個のモデル")
        return bean_models, bean_preprocessing_info
    except FileNotFoundError:
        print("保存済みモデルファイルが見つかりません。動的モデル作成を使用します。")
        return {}, {}

bean_models, bean_preprocessing_info = load_bean_specific_models()

# MySQL接続設定
import os

# Railway環境変数からデータベース設定を取得
DATABASE_URL = os.getenv('DATABASE_URL')

if DATABASE_URL:
    # Railway環境の場合
    # DATABASE_URL形式: mysql://username:password@host:port/database
    from urllib.parse import urlparse
    parsed = urlparse(DATABASE_URL)
    
    mysql_config = {
        'host': parsed.hostname,
        'port': parsed.port or 3306,
        'user': parsed.username,
        'password': parsed.password,
        'database': parsed.path.lstrip('/'),
        'charset': 'utf8mb4'
    }
else:
    # ローカル環境の場合
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
    days_passed: Optional[float] = None

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
        "saved_models_loaded": len(bean_models),
        "available_saved_models": list(bean_models.keys()),
        "data_source": "mysql_demo_db",
        "prediction_mode": "dynamic" if len(bean_models) == 0 else "mixed"
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
    """単一予測（豆ごとのモデルを使用）"""
    try:
        # 指定された豆のモデルが存在するかチェック
        if input_data.bean_name not in bean_models:
            raise HTTPException(status_code=400, detail=f"豆 '{input_data.bean_name}' のモデルが見つかりません")
        
        # 日付を解析
        date_obj = datetime.strptime(input_data.date, "%Y-%m-%d")
        
        # 入力データをDataFrameに変換
        input_df = pd.DataFrame([{
            'year': date_obj.year,
            'month': date_obj.month,
            'day': date_obj.day,
            'day_of_week': date_obj.weekday(),
            'weather': input_data.weather,
            'temperature': input_data.temperature,
            'humidity': input_data.humidity,
            'days_passed': input_data.days_passed,
            'bean_origin': input_data.bean_origin
        }])
        
        # 天気のOne-Hotエンコーディング
        weather_dummies = pd.get_dummies(input_df['weather'], prefix='weather')
        input_df = pd.concat([input_df.drop('weather', axis=1), weather_dummies], axis=1)
        
        # 豆の産地のOne-Hotエンコーディング
        origin_dummies = pd.get_dummies(input_df['bean_origin'], prefix='origin')
        input_df = pd.concat([input_df.drop('bean_origin', axis=1), origin_dummies], axis=1)
        
        # 該当する豆の前処理情報を取得
        preprocessing_info = bean_preprocessing_info[input_data.bean_name]
        
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
        
        # 該当する豆のモデルで予測実行
        model = bean_models[input_data.bean_name]
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

@app.post("/predict-dynamic", response_model=PredictionOutput)
async def predict_dynamic(input_data: PredictionInput):
    """動的モデル構築による単一予測"""
    try:
        print(f"動的予測開始: {input_data.bean_name}")
        
        # 指定された豆のデータを取得
        connection = mysql.connector.connect(**mysql_config)
        cursor = connection.cursor()
        
        # その豆のレシピデータを取得
        query = """
        SELECT r.gram, r.mesh, r.extraction_time, r.date, r.weather, r.temperature, r.humidity, r.days_passed
        FROM recipe r
        JOIN beans b ON r.bean_id = b.id
        WHERE b.name = %s
        """
        
        cursor.execute(query, (input_data.bean_name,))
        rows = cursor.fetchall()
        cursor.close()
        connection.close()
        
        print(f"取得したデータ数: {len(rows)}")
        
        # データが存在しない場合
        if len(rows) == 0:
            raise HTTPException(
                status_code=400, 
                detail=f"豆 '{input_data.bean_name}' のデータが見つかりません。この豆のレシピデータを先に登録してください。"
            )
        
        # データ数チェック
        if len(rows) < 10:  # 最低10件のデータが必要
            raise HTTPException(
                status_code=400, 
                detail=f"データが少なすぎるので予測ができません。豆 '{input_data.bean_name}' のデータは {len(rows)}件しかありません。最低10件のデータが必要です。"
            )
        
        # データをDataFrameに変換
        df = pd.DataFrame(rows, columns=['gram', 'mesh', 'extraction_time', 'date', 'weather', 'temperature', 'humidity', 'days_passed'])
        
        # 日付を解析
        df['date'] = pd.to_datetime(df['date'])
        df['year'] = df['date'].dt.year
        df['month'] = df['date'].dt.month
        df['day'] = df['date'].dt.day
        df['day_of_week'] = df['date'].dt.weekday
        
        # 特徴量とターゲットを分離
        feature_columns = ['temperature', 'humidity', 'year', 'month', 'day', 'day_of_week', 'days_passed']
        X = df[feature_columns]
        y = df[['mesh', 'gram', 'extraction_time']]
        
        # 天気のOne-Hotエンコーディング
        weather_dummies = pd.get_dummies(df['weather'], prefix='weather')
        X = pd.concat([X, weather_dummies], axis=1)
        
        print(f"特徴量数: {X.shape[1]}, サンプル数: {X.shape[0]}")
        
        # モデルを学習
        from sklearn.ensemble import RandomForestRegressor
        model = RandomForestRegressor(n_estimators=100, random_state=42)
        model.fit(X, y)
        
        # モデルと前処理情報を保存
        import pickle
        import os
        
        # modelディレクトリが存在しない場合は作成
        os.makedirs('model', exist_ok=True)
        
        # モデルファイル名を生成
        bean_name_safe = input_data.bean_name.replace(' ', '_').replace('/', '_')
        model_filename = f'model/random_forest_{bean_name_safe}.pkl'
        preprocessing_filename = f'model/preprocessing_info_{bean_name_safe}.pkl'
        
        # 前処理情報を準備
        preprocessing_info = {
            'feature_names': list(X.columns),
            'target_names': ['mesh', 'gram', 'extraction_time'],
            'categorical_columns': ['weather'],
            'numerical_columns': ['temperature', 'humidity', 'year', 'month', 'day', 'day_of_week', 'days_passed'],
            'data_source': 'mysql_demo_db',
            'bean_name': input_data.bean_name,
            'training_date': datetime.now().isoformat(),
            'sample_count': len(X)
        }
        
        # モデルと前処理情報を保存
        with open(model_filename, 'wb') as f:
            pickle.dump(model, f)
        
        with open(preprocessing_filename, 'wb') as f:
            pickle.dump(preprocessing_info, f)
        
        print(f"モデルを保存しました: {model_filename}")
        print(f"前処理情報を保存しました: {preprocessing_filename}")
        
        # 入力データを準備
        date_obj = datetime.strptime(input_data.date, "%Y-%m-%d")
        input_df = pd.DataFrame([{
            'year': date_obj.year,
            'month': date_obj.month,
            'day': date_obj.day,
            'day_of_week': date_obj.weekday(),
            'weather': input_data.weather,
            'temperature': input_data.temperature,
            'humidity': input_data.humidity,
            'days_passed': input_data.days_passed
        }])
        
        print(f"入力データ: days_passed={input_data.days_passed}, temperature={input_data.temperature}, humidity={input_data.humidity}")
        
        # 天気のOne-Hotエンコーディング
        weather_dummies = pd.get_dummies(input_df['weather'], prefix='weather')
        input_df = pd.concat([input_df.drop('weather', axis=1), weather_dummies], axis=1)
        
        # 不足している天気カテゴリを追加
        for col in X.columns:
            if col.startswith('weather_') and col not in input_df.columns:
                input_df[col] = 0
        
        # 特徴量の順序を統一
        input_df = input_df[X.columns]
        
        print(f"入力データの特徴量数: {input_df.shape[1]}")
        
        # 予測実行
        prediction = model.predict(input_df)
        
        # 特徴量の重要度を確認
        feature_importance = model.feature_importances_
        feature_names = X.columns
        importance_dict = dict(zip(feature_names, feature_importance))
        print(f"特徴量重要度: {importance_dict}")
        
        # 特徴量重要度の画像を保存
        import matplotlib.pyplot as plt
        import matplotlib
        matplotlib.use('Agg')  # バックエンドを設定
        
        # 重要度を降順にソート
        sorted_indices = feature_importance.argsort()[::-1]
        sorted_features = [feature_names[i] for i in sorted_indices]
        sorted_importance = feature_importance[sorted_indices]
        
        # グラフを作成
        plt.figure(figsize=(12, 8))
        plt.bar(range(len(sorted_importance)), sorted_importance)
        plt.xlabel('特徴量')
        plt.ylabel('重要度')
        plt.title(f'{input_data.bean_name} - 特徴量重要度')
        plt.xticks(range(len(sorted_features)), sorted_features, rotation=45, ha='right')
        plt.tight_layout()
        
        # 画像を保存
        feature_importance_filename = f'model/feature_importance_{bean_name_safe}.png'
        plt.savefig(feature_importance_filename, dpi=300, bbox_inches='tight')
        plt.close()
        
        print(f"特徴量重要度画像を保存しました: {feature_importance_filename}")
        
        # モデル情報ファイルを更新
        bean_models_info = {}
        try:
            with open('model/bean_models_info.pkl', 'rb') as f:
                bean_models_info = pickle.load(f)
        except FileNotFoundError:
            bean_models_info = {}
        
        # 新しいモデル情報を追加/更新
        bean_models_info[input_data.bean_name] = {
            'model_file': model_filename,
            'preprocessing_file': preprocessing_filename,
            'feature_importance_file': feature_importance_filename,
            'last_updated': datetime.now().isoformat(),
            'sample_count': len(X)
        }
        
        # モデル情報を保存
        with open('model/bean_models_info.pkl', 'wb') as f:
            pickle.dump(bean_models_info, f)
        
        print(f"モデル情報を更新しました: {len(bean_models_info)}個のモデル")
        
        # 信頼度の計算（データ数に基づく）
        confidence = min(0.95, 0.5 + (len(rows) - 10) * 0.02)  # データ数が多いほど信頼度が高い
        
        print(f"予測完了: mesh={prediction[0][0]}, gram={prediction[0][1]}, extraction_time={prediction[0][2]}")
        
        # 結果を返す
        return PredictionOutput(
            mesh=float(prediction[0][0]),
            gram=float(prediction[0][1]),
            extraction_time=float(prediction[0][2]),
            confidence=confidence
        )
        
    except Exception as e:
        print(f"動的予測エラー: {str(e)}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=400, detail=f"動的予測エラー: {str(e)}")

@app.post("/predict-saved", response_model=PredictionOutput)
async def predict_saved(input_data: PredictionInput):
    """保存済みモデルを使用した予測"""
    try:
        print(f"保存済みモデルで予測開始: {input_data.bean_name}")
        
        # 保存済みモデルを読み込み
        bean_name_safe = input_data.bean_name.replace(' ', '_').replace('/', '_')
        model_filename = f'model/random_forest_{bean_name_safe}.pkl'
        preprocessing_filename = f'model/preprocessing_info_{bean_name_safe}.pkl'
        
        try:
            with open(model_filename, 'rb') as f:
                model = pickle.load(f)
            with open(preprocessing_filename, 'rb') as f:
                preprocessing_info = pickle.load(f)
        except FileNotFoundError:
            raise HTTPException(
                status_code=400, 
                detail=f"豆 '{input_data.bean_name}' の保存済みモデルが見つかりません。先に動的予測を実行してモデルを作成してください。"
            )
        
        # 入力データを準備
        date_obj = datetime.strptime(input_data.date, "%Y-%m-%d")
        input_df = pd.DataFrame([{
            'year': date_obj.year,
            'month': date_obj.month,
            'day': date_obj.day,
            'day_of_week': date_obj.weekday(),
            'weather': input_data.weather,
            'temperature': input_data.temperature,
            'humidity': input_data.humidity,
            'days_passed': input_data.days_passed
        }])
        
        # 天気のOne-Hotエンコーディング
        weather_dummies = pd.get_dummies(input_df['weather'], prefix='weather')
        input_df = pd.concat([input_df.drop('weather', axis=1), weather_dummies], axis=1)
        
        # 不足している天気カテゴリを追加
        for col in preprocessing_info['feature_names']:
            if col.startswith('weather_') and col not in input_df.columns:
                input_df[col] = 0
        
        # 特徴量の順序を統一
        input_df = input_df[preprocessing_info['feature_names']]
        
        # 予測実行
        prediction = model.predict(input_df)
        
        print(f"保存済みモデルで予測完了: mesh={prediction[0][0]}, gram={prediction[0][1]}, extraction_time={prediction[0][2]}")
        
        # 結果を返す
        return PredictionOutput(
            mesh=float(prediction[0][0]),
            gram=float(prediction[0][1]),
            extraction_time=float(prediction[0][2]),
            confidence=0.9  # 保存済みモデルは高信頼度
        )
        
    except Exception as e:
        print(f"保存済みモデル予測エラー: {str(e)}")
        raise HTTPException(status_code=400, detail=f"保存済みモデル予測エラー: {str(e)}")

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
