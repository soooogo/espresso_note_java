import mysql.connector
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import os
from weather_data import create_mock_weather_data

class MySQLDataLoader:
    def __init__(self):
        # MySQL接続設定
        self.config = {
            'host': 'localhost',
            'user': 'root',
            'password': '',
            'database': 'demo_db',
            'charset': 'utf8mb4'
        }
    
    def connect(self):
        """MySQLデータベースに接続"""
        try:
            connection = mysql.connector.connect(**self.config)
            print("MySQLデータベースに接続しました")
            return connection
        except mysql.connector.Error as err:
            print(f"MySQL接続エラー: {err}")
            return None
    
    def create_tables_if_not_exist(self):
        """テーブルが存在しない場合は作成"""
        connection = self.connect()
        if not connection:
            return False
        
        try:
            cursor = connection.cursor()
            
            # usersテーブルを作成
            create_user_table = """
            CREATE TABLE IF NOT EXISTS users (
                id INT AUTO_INCREMENT PRIMARY KEY,
                name VARCHAR(100) NOT NULL,
                email VARCHAR(100) NOT NULL UNIQUE,
                password VARCHAR(255) NOT NULL,
                role VARCHAR(20) NOT NULL DEFAULT 'ROLE_USER'
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
            """
            
            # beansテーブルを作成
            create_beans_table = """
            CREATE TABLE IF NOT EXISTS beans (
                id INT AUTO_INCREMENT PRIMARY KEY,
                user_id INT NOT NULL,
                name VARCHAR(100) NOT NULL,
                from_location VARCHAR(100) NOT NULL,
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
            """
            
            # recipeテーブルを作成
            create_recipe_table = """
            CREATE TABLE IF NOT EXISTS recipe (
                id INT AUTO_INCREMENT PRIMARY KEY,
                bean_id INT NOT NULL,
                date DATE NOT NULL,
                weather VARCHAR(50) NOT NULL,
                temperature FLOAT,
                humidity INT,
                gram FLOAT NOT NULL,
                mesh FLOAT NOT NULL,
                extraction_time FLOAT NOT NULL,
                FOREIGN KEY (bean_id) REFERENCES beans(id) ON DELETE CASCADE
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
            """
            
            cursor.execute(create_user_table)
            cursor.execute(create_beans_table)
            cursor.execute(create_recipe_table)
            
            connection.commit()
            print("テーブルの作成が完了しました")
            return True
            
        except mysql.connector.Error as err:
            print(f"テーブル作成エラー: {err}")
            return False
        finally:
            connection.close()
    
    def load_recipe_data(self):
        """レシピデータをMySQLから取得"""
        connection = self.connect()
        if not connection:
            return None
        
        try:
            # レシピ、豆、ユーザー情報を結合して取得
            query = """
            SELECT 
                r.id,
                r.date,
                r.weather,
                r.temperature,
                r.humidity,
                r.gram,
                r.mesh,
                r.extraction_time,
                b.name as bean_name,
                b.from_location as bean_origin,
                u.name as user_name
            FROM recipe r
            JOIN beans b ON r.bean_id = b.id
            JOIN users u ON b.user_id = u.id
            ORDER BY r.date DESC
            """
            
            df = pd.read_sql(query, connection)
            print(f"MySQLから{len(df)}件のレシピデータを取得しました")
            return df
            
        except mysql.connector.Error as err:
            print(f"データ取得エラー: {err}")
            return None
        finally:
            connection.close()
    
    def create_sample_data(self):
        """サンプルデータをMySQLに挿入（テスト用）"""
        connection = self.connect()
        if not connection:
            return False
        
        try:
            cursor = connection.cursor()
            
            # ユーザーデータの挿入
            users_data = [
                ("コーヒー愛好家", "coffee.lover@example.com", "$2a$10$N.zmdr9k7uOCQb376NoUnuTJ8iAt6Z5EHsM8lE9lBOsl7iKTVEFDa", "ROLE_USER"),
                ("エスプレッソ職人", "espresso.pro@example.com", "$2a$10$N.zmdr9k7uOCQb376NoUnuTJ8iAt6Z5EHsM8lE9lBOsl7iKTVEFDa", "ROLE_USER"),
                ("ホームロースター", "home.roaster@example.com", "$2a$10$N.zmdr9k7uOCQb376NoUnuTJ8iAt6Z5EHsM8lE9lBOsl7iKTVEFDa", "ROLE_ADMIN")
            ]
            
            cursor.execute("DELETE FROM recipe")
            cursor.execute("DELETE FROM beans")
            cursor.execute("DELETE FROM users")
            
            for user_data in users_data:
                cursor.execute("""
                    INSERT INTO users (name, email, password, role) 
                    VALUES (%s, %s, %s, %s)
                """, user_data)
            
            # ユーザーIDを取得
            cursor.execute("SELECT id FROM users")
            user_ids = [row[0] for row in cursor.fetchall()]
            
            # 豆データの挿入
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
            
            for bean_data in beans_data:
                cursor.execute("""
                    INSERT INTO beans (user_id, name, from_location) 
                    VALUES (%s, %s, %s)
                """, bean_data)
            
            # 豆IDを取得
            cursor.execute("SELECT id FROM beans")
            bean_ids = [row[0] for row in cursor.fetchall()]
            
            # 気象データを取得
            weather_df = create_mock_weather_data()
            
            # レシピデータの挿入（気象データと組み合わせ）
            recipes_data = []
            current_date = datetime.now()
            
            for i, bean_id in enumerate(bean_ids):
                # 各豆に対して複数のレシピを作成
                for j in range(5):
                    recipe_date = current_date - timedelta(days=j+1)
                    date_str = recipe_date.strftime("%Y-%m-%d")
                    
                    # 気象データから該当する日付のデータを取得
                    weather_row = weather_df[weather_df['date'] == date_str]
                    
                    if len(weather_row) > 0:
                        temp = weather_row.iloc[0]['temperature']
                        humidity = weather_row.iloc[0]['humidity']
                    else:
                        # デフォルト値
                        temp = 20.0
                        humidity = 60
                    
                    # 天気をランダムに選択
                    weather_options = ["晴れ", "曇り", "雨", "雪"]
                    weather = np.random.choice(weather_options)
                    
                    # 抽出パラメータを生成（気象データに基づいて調整）
                    base_mesh = 18.0
                    base_gram = 2.5
                    base_extraction_time = 30.0
                    
                    # 気温による調整
                    temp_factor = (temp - 20) / 10  # 20度を基準
                    mesh = base_mesh + temp_factor * 0.5
                    gram = base_gram + temp_factor * 0.1
                    extraction_time = base_extraction_time + temp_factor * 2
                    
                    # 湿度による調整
                    humidity_factor = (humidity - 60) / 30  # 60%を基準
                    mesh += humidity_factor * 0.3
                    gram += humidity_factor * 0.05
                    extraction_time += humidity_factor * 1.5
                    
                    recipes_data.append((
                        bean_id,
                        recipe_date,
                        weather,
                        temp,
                        humidity,
                        gram,  # gramとして保存
                        mesh,  # meshとして保存
                        extraction_time
                    ))
            
            # レシピデータを挿入
            for recipe_data in recipes_data:
                cursor.execute("""
                    INSERT INTO recipe (bean_id, date, weather, temperature, humidity, gram, mesh, extraction_time) 
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                """, recipe_data)
            
            connection.commit()
            print(f"サンプルデータを挿入しました: {len(recipes_data)}件のレシピ")
            return True
            
        except mysql.connector.Error as err:
            print(f"データ挿入エラー: {err}")
            connection.rollback()
            return False
        finally:
            connection.close()
    
    def prepare_training_data(self):
        """学習用データセットを準備"""
        # テーブルが存在しない場合は作成
        print("テーブルの存在を確認しています...")
        self.create_tables_if_not_exist()
        
        # MySQLからデータを取得
        df = self.load_recipe_data()
        if df is None or len(df) == 0:
            print("MySQLからデータを取得できませんでした。サンプルデータを作成します。")
            if self.create_sample_data():
                df = self.load_recipe_data()
            else:
                return None
        
        # 日付を文字列に変換
        df['date_str'] = df['date'].astype(str)
        
        # 気象データを読み込み
        try:
            weather_df = pd.read_csv('data/weather_data.csv')
        except FileNotFoundError:
            print("気象データファイルが見つかりません。生成します。")
            weather_df = create_mock_weather_data()
        
        # 気象データと結合
        df = pd.merge(df, weather_df, left_on='date_str', right_on='date', how='left')
        
        # 欠損値を処理（列が存在するかチェック）
        print(f"データフレームの列名: {df.columns.tolist()}")
        
        # 列名の重複を解決
        if 'temperature_x' in df.columns:
            df['temperature'] = df['temperature_x']
        elif 'temperature_y' in df.columns:
            df['temperature'] = df['temperature_y']
        else:
            df['temperature'] = 20.0
            
        if 'humidity_x' in df.columns:
            df['humidity'] = df['humidity_x']
        elif 'humidity_y' in df.columns:
            df['humidity'] = df['humidity_y']
        else:
            df['humidity'] = 60
            
        if 'date_x' in df.columns:
            df['date'] = df['date_x']
        elif 'date_y' in df.columns:
            df['date'] = df['date_y']
        
        # 不要な列を削除
        columns_to_drop = ['date_str', 'date_x', 'date_y', 'temperature_x', 'temperature_y', 'humidity_x', 'humidity_y']
        existing_columns = [col for col in columns_to_drop if col in df.columns]
        df = df.drop(existing_columns, axis=1)
        
        # 特徴量エンジニアリング
        # 日付をdatetimeに変換
        df['date'] = pd.to_datetime(df['date'])
        df['year'] = df['date'].dt.year
        df['month'] = df['date'].dt.month
        df['day'] = df['date'].dt.day
        df['day_of_week'] = df['date'].dt.dayofweek
        
        # 豆の産地をOne-Hotエンコーディング
        df = pd.get_dummies(df, columns=['bean_origin'], prefix='origin')
        
        # 天気をOne-Hotエンコーディング
        df = pd.get_dummies(df, columns=['weather'], prefix='weather')
        
        print("学習用データセットを準備しました")
        print(f"データ数: {len(df)}件")
        print(f"特徴量数: {len(df.columns)}個")
        
        return df

if __name__ == "__main__":
    loader = MySQLDataLoader()
    
    # サンプルデータを作成（初回のみ）
    print("MySQLにサンプルデータを作成しています...")
    loader.create_sample_data()
    
    # 学習用データセットを準備
    print("学習用データセットを準備しています...")
    training_data = loader.prepare_training_data()
    
    if training_data is not None:
        # CSVファイルとして保存
        training_data.to_csv('data/mysql_training_data.csv', index=False)
        print("学習用データセットを 'data/mysql_training_data.csv' に保存しました")
        
        # データの概要を表示
        print("\n=== データ概要 ===")
        print(training_data.describe())
        
        print("\n=== 特徴量一覧 ===")
        print(training_data.columns.tolist())
    else:
        print("データセットの準備に失敗しました")
