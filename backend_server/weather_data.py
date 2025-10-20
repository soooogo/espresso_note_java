import os
import requests
from datetime import datetime
from typing import Dict, Optional


class WeatherDataCollector:
    """天気データ収集クラス（無料版OpenWeatherMap API使用）"""
    
    def __init__(self):
        self.api_key = os.getenv('OPENWEATHER_API_KEY')
        # 京都の座標（左京区付近）
        self.lat = 35.0116
        self.lon = 135.7681
        self.base_url = "http://api.openweathermap.org/data/2.5/weather"
    
    def get_current_weather(self) -> Optional[Dict[str, float]]:
        """現在の天気データを取得（無料版API）"""
        if not self.api_key or self.api_key == 'your_api_key_here':
            print("OpenWeatherMap APIキーが設定されていません")
            return None
        
        try:
            # APIリクエストのパラメータ
            params = {
                'lat': self.lat,
                'lon': self.lon,
                'appid': self.api_key,
                'units': 'metric',  # 摂氏温度
                'lang': 'ja'
            }
            
            # APIリクエスト実行
            response = requests.get(self.base_url, params=params, timeout=10)
            response.raise_for_status()
            
            # JSONレスポンスをパース
            data = response.json()
            
            # 必要なデータを抽出
            main_data = data.get('main', {})
            weather_data = {
                'temperature': main_data.get('temp', 20.0),
                'humidity': main_data.get('humidity', 60.0),
                'pressure': main_data.get('pressure', 1013.25),
                'timestamp': datetime.now().isoformat()
            }
            
            # 天候情報も追加
            weather_info = data.get('weather', [])
            if weather_info:
                weather_data['weather'] = weather_info[0].get('main', 'Clear')
                weather_data['description'] = weather_info[0].get('description', '')
            
            print(f"天気データ取得成功: 気温={weather_data['temperature']}℃, 湿度={weather_data['humidity']}%")
            return weather_data
            
        except requests.exceptions.RequestException as e:
            print(f"APIリクエストエラー: {e}")
            return None
        except KeyError as e:
            print(f"レスポンス解析エラー: {e}")
            return None
        except Exception as e:
            print(f"予期しないエラー: {e}")
            return None
    
    def get_default_weather(self) -> Dict[str, float]:
        """デフォルトの天気データを返す"""
        return {
            'temperature': 20.0,
            'humidity': 60.0,
            'pressure': 1013.25,
            'weather': 'Clear',
            'description': '晴れ',
            'timestamp': datetime.now().isoformat()
        }


# テスト用の関数
if __name__ == "__main__":
    collector = WeatherDataCollector()
    weather = collector.get_current_weather()
    
    if weather:
        print("現在の天気データ:")
        print(f"  気温: {weather['temperature']}℃")
        print(f"  湿度: {weather['humidity']}%")
        print(f"  気圧: {weather['pressure']}hPa")
        print(f"  天候: {weather.get('weather', 'N/A')}")
        print(f"  詳細: {weather.get('description', 'N/A')}")
        print(f"  取得時刻: {weather['timestamp']}")
    else:
        print("天気データの取得に失敗しました")
        default = collector.get_default_weather()
        print("デフォルト値を使用:")
        print(f"  気温: {default['temperature']}℃")
        print(f"  湿度: {default['humidity']}%")
