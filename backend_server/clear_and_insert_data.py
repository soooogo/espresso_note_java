import mysql.connector
from datetime import datetime, timedelta
import random

def clear_and_insert_data():
    """データベースをクリアしてサンプルデータを挿入"""
    
    # MySQL接続設定
    mysql_config = {
        'host': 'localhost',
        'user': 'root',
        'password': '',
        'database': 'demo_db',
        'charset': 'utf8mb4'
    }
    
    try:
        connection = mysql.connector.connect(**mysql_config)
        cursor = connection.cursor()
        
        print("MySQL接続成功")
        
        # 1. データベースをクリア
        print("\n1. データベースのクリア...")
        cursor.execute("SET FOREIGN_KEY_CHECKS = 0")
        cursor.execute("TRUNCATE TABLE recipe")
        cursor.execute("TRUNCATE TABLE beans")
        cursor.execute("TRUNCATE TABLE users")
        cursor.execute("SET FOREIGN_KEY_CHECKS = 1")
        print("✓ すべてのテーブルをクリアしました")
        
        # 2. ユーザーを挿入
        print("\n2. ユーザーの挿入...")
        users_data = [
            ("コーヒー愛好家", "coffee.lover@example.com", "$2a$10$N.zmdr9k7uOCQb376NoUnuTJ8iAt6Z5EHsM8lE9lBOsl7iKTVEFDa", "ROLE_USER"),
            ("エスプレッソ職人", "espresso.pro@example.com", "$2a$10$N.zmdr9k7uOCQb376NoUnuTJ8iAt6Z5EHsM8lE9lBOsl7iKTVEFDa", "ROLE_USER"),
            ("ホームロースター", "home.roaster@example.com", "$2a$10$N.zmdr9k7uOCQb376NoUnuTJ8iAt6Z5EHsM8lE9lBOsl7iKTVEFDa", "ROLE_ADMIN")
        ]
        
        user_ids = []
        for user_data in users_data:
            cursor.execute(
                "INSERT INTO users (name, email, password, role) VALUES (%s, %s, %s, %s)",
                user_data
            )
            user_ids.append(cursor.lastrowid)
            print(f"✓ ユーザー '{user_data[0]}' を挿入しました (ID: {cursor.lastrowid})")
        
        # 3. 豆を挿入
        print("\n3. 豆の挿入...")
        beans_data = [
            (user_ids[0], "エチオピア イルガチェフェ", "エチオピア"),
            (user_ids[0], "グアテマラ アンティグア", "グアテマラ"),
            (user_ids[1], "ブラジル サントス", "ブラジル"),
            (user_ids[1], "コロンビア スプレモ", "コロンビア"),
            (user_ids[1], "ケニア AA", "ケニア"),
            (user_ids[2], "インドネシア マンデリン", "インドネシア"),
            (user_ids[2], "パナマ ゲイシャ", "パナマ"),
            (user_ids[2], "タンザニア キリマンジャロ", "タンザニア")
        ]
        
        bean_ids = []
        for bean_data in beans_data:
            cursor.execute(
                "INSERT INTO beans (user_id, name, from_location) VALUES (%s, %s, %s)",
                bean_data
            )
            bean_ids.append(cursor.lastrowid)
            print(f"✓ 豆 '{bean_data[1]}' を挿入しました (ID: {cursor.lastrowid})")
        
        # 4. レシピを挿入
        print("\n4. レシピの挿入...")
        
        # エチオピア イルガチェフェのレシピ（20件）
        for i in range(1, 21):
            date = datetime.now() - timedelta(days=i)
            weather = ["晴れ", "曇り", "雨", "雪"][i % 4]
            temperature = 15.0 + (i % 15)
            humidity = 50 + (i % 30)
            mesh = 17.0 + (i % 4) * 0.5
            gram = 2.0 + (i % 6) * 0.1
            extraction_time = 25.0 + (i % 10)
            days_passed = 10.0 + (i % 10)
            
            cursor.execute(
                """INSERT INTO recipe 
                   (bean_id, date, weather, temperature, humidity, gram, mesh, extraction_time, days_passed)
                   VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)""",
                (bean_ids[0], date.date(), weather, temperature, humidity, gram, mesh, extraction_time, days_passed)
            )
        
        # グアテマラ アンティグアのレシピ（20件）
        for i in range(1, 21):
            date = datetime.now() - timedelta(days=i + 20)
            weather = ["晴れ", "曇り", "雨", "雪"][i % 4]
            temperature = 16.0 + (i % 14)
            humidity = 45 + (i % 35)
            mesh = 16.5 + (i % 4) * 0.5
            gram = 2.1 + (i % 5) * 0.1
            extraction_time = 26.0 + (i % 9)
            days_passed = 12.0 + (i % 8)
            
            cursor.execute(
                """INSERT INTO recipe 
                   (bean_id, date, weather, temperature, humidity, gram, mesh, extraction_time, days_passed)
                   VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)""",
                (bean_ids[1], date.date(), weather, temperature, humidity, gram, mesh, extraction_time, days_passed)
            )
        
        # ブラジル サントスのレシピ（20件）
        for i in range(1, 21):
            date = datetime.now() - timedelta(days=i + 40)
            weather = ["晴れ", "曇り", "雨", "雪"][i % 4]
            temperature = 17.0 + (i % 13)
            humidity = 48 + (i % 32)
            mesh = 17.5 + (i % 3) * 0.5
            gram = 2.2 + (i % 4) * 0.1
            extraction_time = 27.0 + (i % 8)
            days_passed = 15.0 + (i % 5)
            
            cursor.execute(
                """INSERT INTO recipe 
                   (bean_id, date, weather, temperature, humidity, gram, mesh, extraction_time, days_passed)
                   VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)""",
                (bean_ids[2], date.date(), weather, temperature, humidity, gram, mesh, extraction_time, days_passed)
            )
        
        # その他の豆のレシピ
        additional_recipes = [
            (bean_ids[3], datetime.now() - timedelta(days=1), "晴れ", 24.0, 58, 18.2, 2.4, 29.5, 15.0),
            (bean_ids[3], datetime.now() - timedelta(days=6), "雨", 19.0, 85, 19.3, 2.8, 36.0, 12.0),
            (bean_ids[4], datetime.now() - timedelta(days=2), "曇り", 21.5, 70, 18.8, 2.6, 33.0, 18.0),
            (bean_ids[5], datetime.now() - timedelta(days=7), "雨", 18.0, 88, 19.5, 2.9, 38.0, 10.0),
            (bean_ids[5], datetime.now() - timedelta(days=8), "曇り", 20.5, 72, 18.7, 2.5, 32.5, 16.0),
            (bean_ids[6], datetime.now() - timedelta(days=1), "晴れ", 26.0, 52, 17.8, 2.1, 27.0, 14.0),
            (bean_ids[7], datetime.now() - timedelta(days=3), "雪", 2.0, 40, 19.0, 2.6, 34.0, 20.0)
        ]
        
        for recipe_data in additional_recipes:
            cursor.execute(
                """INSERT INTO recipe 
                   (bean_id, date, weather, temperature, humidity, gram, mesh, extraction_time, days_passed)
                   VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)""",
                (recipe_data[0], recipe_data[1].date(), recipe_data[2], recipe_data[3], 
                 recipe_data[4], recipe_data[5], recipe_data[6], recipe_data[7], recipe_data[8])
            )
        
        connection.commit()
        cursor.close()
        connection.close()
        
        print("\n✅ データベースのクリアとサンプルデータの挿入が完了しました！")
        print(f"ユーザー数: {len(users_data)}")
        print(f"豆の数: {len(beans_data)}")
        print(f"レシピ数: {20*3 + len(additional_recipes)}")
        
    except Exception as e:
        print(f"エラーが発生しました: {e}")

if __name__ == "__main__":
    print("データベースのクリアとサンプルデータの挿入を開始します...")
    clear_and_insert_data()
