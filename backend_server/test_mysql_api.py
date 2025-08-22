import requests
import json
from datetime import datetime, timedelta

# APIのベースURL（MySQL版はポート8081）
BASE_URL = "http://localhost:8081"

def test_health():
    """ヘルスチェックのテスト"""
    print("=== ヘルスチェック ===")
    response = requests.get(f"{BASE_URL}/health")
    print(f"Status: {response.status_code}")
    print(f"Response: {response.json()}")
    print()

def test_database_stats():
    """データベース統計のテスト"""
    print("=== データベース統計 ===")
    response = requests.get(f"{BASE_URL}/database-stats")
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2, ensure_ascii=False)}")
    print()

def test_get_beans():
    """豆情報取得のテスト"""
    print("=== 豆情報取得 ===")
    response = requests.get(f"{BASE_URL}/beans")
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2, ensure_ascii=False)}")
    print()

def test_model_info():
    """モデル情報の取得テスト"""
    print("=== モデル情報 ===")
    response = requests.get(f"{BASE_URL}/model-info")
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2, ensure_ascii=False)}")
    print()

def test_current_weather():
    """現在の気象データ取得テスト"""
    print("=== 現在の気象データ ===")
    response = requests.get(f"{BASE_URL}/current-weather")
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2, ensure_ascii=False)}")
    print()

def test_single_prediction():
    """単一予測のテスト"""
    print("=== 単一予測 ===")
    data = {
        "bean_name": "エチオピア イルガチェフェ",
        "bean_origin": "エチオピア",
        "date": "2025-03-15",
        "weather": "晴れ",
        "temperature": 18.5,
        "humidity": 65.0
    }
    response = requests.post(f"{BASE_URL}/predict", json=data)
    print(f"Status: {response.status_code}")
    print(f"Request: {data}")
    print(f"Response: {json.dumps(response.json(), indent=2, ensure_ascii=False)}")
    print()

def test_batch_prediction():
    """バッチ予測のテスト"""
    print("=== バッチ予測 ===")
    data = [
        {
            "bean_name": "エチオピア イルガチェフェ",
            "bean_origin": "エチオピア",
            "date": "2025-03-15",
            "weather": "晴れ",
            "temperature": 18.5,
            "humidity": 65.0
        },
        {
            "bean_name": "グアテマラ アンティグア",
            "bean_origin": "グアテマラ",
            "date": "2025-03-16",
            "weather": "曇り",
            "temperature": 16.0,
            "humidity": 75.0
        },
        {
            "bean_name": "ブラジル サントス",
            "bean_origin": "ブラジル",
            "date": "2025-03-17",
            "weather": "雨",
            "temperature": 14.0,
            "humidity": 85.0
        }
    ]
    response = requests.post(f"{BASE_URL}/predict-batch", json=data)
    print(f"Status: {response.status_code}")
    print(f"Request: {json.dumps(data, indent=2, ensure_ascii=False)}")
    print(f"Response: {json.dumps(response.json(), indent=2, ensure_ascii=False)}")
    print()

def test_different_beans():
    """異なる豆での予測テスト"""
    print("=== 異なる豆での予測 ===")
    
    beans = [
        {"name": "エチオピア イルガチェフェ", "origin": "エチオピア"},
        {"name": "グアテマラ アンティグア", "origin": "グアテマラ"},
        {"name": "ブラジル サントス", "origin": "ブラジル"},
        {"name": "コロンビア スプレモ", "origin": "コロンビア"},
        {"name": "ケニア AA", "origin": "ケニア"}
    ]
    
    weather_conditions = ["晴れ", "曇り", "雨"]
    
    for bean in beans:
        for weather in weather_conditions:
            data = {
                "bean_name": bean["name"],
                "bean_origin": bean["origin"],
                "date": "2025-03-15",
                "weather": weather,
                "temperature": 20.0,
                "humidity": 60.0
            }
            
            response = requests.post(f"{BASE_URL}/predict", json=data)
            if response.status_code == 200:
                result = response.json()
                print(f"{bean['name']} ({weather}): mesh={result['mesh']:.1f}, gram={result['gram']:.1f}, time={result['extraction_time']:.1f}")
            else:
                print(f"エラー: {bean['name']} ({weather}) - {response.status_code}")
    
    print()

if __name__ == "__main__":
    try:
        test_health()
        test_database_stats()
        test_get_beans()
        test_model_info()
        test_current_weather()
        test_single_prediction()
        test_batch_prediction()
        test_different_beans()
        print("✅ すべてのテストが完了しました！")
    except requests.exceptions.ConnectionError:
        print("❌ APIサーバーに接続できません。サーバーが起動しているか確認してください。")
        print("python app_mysql.py でサーバーを起動してください。")
    except Exception as e:
        print(f"❌ エラーが発生しました: {e}")
