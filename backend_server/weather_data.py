import requests
import pandas as pd
from datetime import datetime, timedelta
import time
import json
import os

class WeatherDataCollector:
    def __init__(self):
        # OpenWeatherMap APIキー（無料版を使用）
        # 実際の使用時は環境変数から取得することを推奨
        self.api_key = "YOUR_API_KEY"  # OpenWeatherMap APIキーを設定してください
        self.city = "Kyoto"
        self.country = "JP"
        self.base_url = "http://api.openweathermap.org/data/2.5"
        
    def get_historical_weather(self, date_str):
        """
        指定した日付の気象データを取得
        date_str: "YYYY-MM-DD" 形式
        """
        try:
            # 日付をタイムスタンプに変換
            dt = datetime.strptime(date_str, "%Y-%m-%d")
            timestamp = int(dt.timestamp())
            
            # OpenWeatherMap Historical API
            url = f"{self.base_url}/onecall/timemachine"
            params = {
                'lat': 35.0116,  # 京都の緯度
                'lon': 135.7681,  # 京都の経度
                'dt': timestamp,
                'appid': self.api_key,
                'units': 'metric'  # 摂氏温度
            }
            
            response = requests.get(url, params=params)
            
            if response.status_code == 200:
                data = response.json()
                if 'data' in data and len(data['data']) > 0:
                    # 1日の平均値を計算
                    daily_data = data['data']
                    temps = [hour['temp'] for hour in daily_data]
                    humidities = [hour['humidity'] for hour in daily_data]
                    
                    return {
                        'temperature': sum(temps) / len(temps),
                        'humidity': sum(humidities) / len(humidities)
                    }
            
            return None
            
        except Exception as e:
            print(f"気象データ取得エラー ({date_str}): {e}")
            return None
    
    def get_weather_for_date_range(self, start_date, end_date):
        """
        日付範囲の気象データを取得
        """
        weather_data = []
        current_date = datetime.strptime(start_date, "%Y-%m-%d")
        end_dt = datetime.strptime(end_date, "%Y-%m-%d")
        
        while current_date <= end_dt:
            date_str = current_date.strftime("%Y-%m-%d")
            print(f"気象データを取得中: {date_str}")
            
            weather = self.get_historical_weather(date_str)
            if weather:
                weather_data.append({
                    'date': date_str,
                    'temperature': weather['temperature'],
                    'humidity': weather['humidity']
                })
            
            # API制限を避けるため少し待機
            time.sleep(1)
            current_date += timedelta(days=1)
        
        return pd.DataFrame(weather_data)
    
    def get_current_weather(self):
        """
        現在の気象データを取得
        """
        try:
            url = f"{self.base_url}/weather"
            params = {
                'q': f"{self.city},{self.country}",
                'appid': self.api_key,
                'units': 'metric'
            }
            
            response = requests.get(url, params=params)
            
            if response.status_code == 200:
                data = response.json()
                return {
                    'temperature': data['main']['temp'],
                    'humidity': data['main']['humidity']
                }
            
            return None
            
        except Exception as e:
            print(f"現在の気象データ取得エラー: {e}")
            return None

def create_mock_weather_data():
    """
    APIキーがない場合のモックデータ生成
    """
    print("モック気象データを生成しています...")
    
    # 2024年11月から2025年4月までの日付範囲
    start_date = datetime(2024, 11, 1)
    end_date = datetime(2025, 4, 30)
    
    weather_data = []
    current_date = start_date
    
    while current_date <= end_date:
        # 季節に応じた気温と湿度の範囲を設定
        month = current_date.month
        
        if month in [12, 1, 2]:  # 冬
            temp_range = (-5, 10)
            humidity_range = (40, 70)
        elif month in [3, 4, 5]:  # 春
            temp_range = (5, 20)
            humidity_range = (50, 80)
        elif month in [6, 7, 8]:  # 夏
            temp_range = (20, 35)
            humidity_range = (60, 90)
        else:  # 秋
            temp_range = (10, 25)
            humidity_range = (45, 75)
        
        # ランダムな気温と湿度を生成
        import random
        temperature = round(random.uniform(*temp_range), 1)
        humidity = round(random.uniform(*humidity_range), 1)
        
        weather_data.append({
            'date': current_date.strftime("%Y-%m-%d"),
            'temperature': temperature,
            'humidity': humidity
        })
        
        current_date += timedelta(days=1)
    
    df = pd.DataFrame(weather_data)
    df.to_csv('data/weather_data.csv', index=False)
    print(f"モック気象データを保存しました: {len(df)}件")
    return df

if __name__ == "__main__":
    # モックデータを生成（実際のAPIキーがない場合）
    create_mock_weather_data()
