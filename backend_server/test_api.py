import requests
import json

# APIのベースURL
BASE_URL = "http://localhost:8081"

def test_health():
    """ヘルスチェックのテスト"""
    print("=== ヘルスチェック ===")
    response = requests.get(f"{BASE_URL}/health")
    print(f"Status: {response.status_code}")
    print(f"Response: {response.json()}")
    print()

def test_model_info():
    """モデル情報の取得テスト"""
    print("=== モデル情報 ===")
    response = requests.get(f"{BASE_URL}/model-info")
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2, ensure_ascii=False)}")
    print()

def test_single_prediction():
    """単一予測のテスト"""
    print("=== 単一予測 ===")
    data = {
        "day": 15,
        "month": 3,
        "year": 2025,
        "weather": "晴",
        "days_passed": 12.5,
        "temperature": 18.5,
        "humidity": 65.0
    }
    response = requests.post(f"{BASE_URL}/predict", json=data)
    print(f"Status: {response.status_code}")
    print(f"Request: {data}")
    print(f"Response: {json.dumps(response.json(), indent=2, ensure_ascii=False)}")
    print()

def test_current_weather():
    """現在の気象データ取得テスト"""
    print("=== 現在の気象データ ===")
    response = requests.get(f"{BASE_URL}/current-weather")
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2, ensure_ascii=False)}")
    print()

def test_batch_prediction():
    """バッチ予測のテスト"""
    print("=== バッチ予測 ===")
    data = [
        {
            "day": 15,
            "month": 3,
            "year": 2025,
            "weather": "晴",
            "days_passed": 12.5,
            "temperature": 18.5,
            "humidity": 65.0
        },
        {
            "day": 16,
            "month": 3,
            "year": 2025,
            "weather": "くもり",
            "days_passed": 13.0,
            "temperature": 16.0,
            "humidity": 75.0
        },
        {
            "day": 17,
            "month": 3,
            "year": 2025,
            "weather": "雨",
            "days_passed": 14.0,
            "temperature": 14.0,
            "humidity": 85.0
        }
    ]
    response = requests.post(f"{BASE_URL}/predict-batch", json=data)
    print(f"Status: {response.status_code}")
    print(f"Request: {json.dumps(data, indent=2, ensure_ascii=False)}")
    print(f"Response: {json.dumps(response.json(), indent=2, ensure_ascii=False)}")
    print()

if __name__ == "__main__":
    try:
        test_health()
        test_model_info()
        test_current_weather()
        test_single_prediction()
        test_batch_prediction()
        print("✅ すべてのテストが完了しました！")
    except requests.exceptions.ConnectionError:
        print("❌ APIサーバーに接続できません。サーバーが起動しているか確認してください。")
        print("python app.py でサーバーを起動してください。")
    except Exception as e:
        print(f"❌ エラーが発生しました: {e}")
