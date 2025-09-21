#!/usr/bin/env python3
"""
最後に実行されるデータ挿入スクリプト
Spring BootのDataInitializerが完了した後に実行される
insert_data_to_mysql.pyと同じCSVデータのみを挿入
"""

import os
import sys
import time
import mysql.connector
from mysql.connector import Error
import pandas as pd
import glob
from datetime import datetime, timedelta

def wait_for_spring_boot_completion(max_retries=60, retry_interval=5):
    """Spring Bootの起動完了を待機"""
    print("⏳ Spring Bootの起動完了を待機中...")
    
    for attempt in range(max_retries):
        try:
            # Spring Bootのヘルスチェック
            import requests
            response = requests.get("http://springboot:8080/", timeout=5)
            if response.status_code == 200:
                print("✅ Spring Bootが起動完了しました！")
                return True
        except Exception as e:
            print(f"Spring Boot接続エラー: {e}")
        except:
            pass
        
        print(f"⏳ 試行 {attempt + 1}/{max_retries}: Spring Boot起動待機中...")
        if attempt < max_retries - 1:
            time.sleep(retry_interval)
    
    print("❌ Spring Boot起動タイムアウト")
    return False

def get_mysql_config():
    """MySQL接続設定を取得"""
    database_url = os.getenv('DATABASE_URL')
    
    if database_url:
        from urllib.parse import urlparse
        parsed = urlparse(database_url)
        
        return {
            'host': parsed.hostname,
            'port': parsed.port or 3306,
            'user': parsed.username,
            'password': parsed.password,
            'database': parsed.path.lstrip('/'),
            'charset': 'utf8mb4'
        }
    else:
        return {
            'host': 'mysql',
            'user': 'demo_user',
            'password': 'demo_password',
            'database': 'demo_db',
            'charset': 'utf8mb4'
        }

def check_existing_data():
    """既存データを確認"""
    try:
        mysql_config = get_mysql_config()
        connection = mysql.connector.connect(**mysql_config)
        cursor = connection.cursor()
        
        cursor.execute("SELECT COUNT(*) FROM users")
        user_count = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM beans")
        bean_count = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM recipe")
        recipe_count = cursor.fetchone()[0]
        
        cursor.close()
        connection.close()
        
        print(f"📊 現在のデータ数: ユーザー={user_count}, 豆={bean_count}, レシピ={recipe_count}")
        
        return user_count, bean_count, recipe_count
        
    except Error as e:
        print(f"❌ データ確認エラー: {e}")
        return 0, 0, 0

def load_monthly_csv_files():
    """月別CSVファイルを読み込んで結合"""
    all_data = []
    
    # 豆のマッピング（月別CSVは全てエチオピア イルガチェフェ）
    bean_mapping = {
        '2024_11': 'エチオピア イルガチェフェ',
        '2024_12': 'エチオピア イルガチェフェ', 
        '2025_01': 'エチオピア イルガチェフェ',
        '2025_02': 'エチオピア イルガチェフェ',
        '2025_03': 'エチオピア イルガチェフェ',
        '2025_04': 'エチオピア イルガチェフェ'
    }
    
    # ユーザーマッピング
    user_mapping = {
        '2024_11': 'コーヒー愛好家',
        '2024_12': 'コーヒー愛好家',
        '2025_01': 'コーヒー愛好家',
        '2025_02': 'コーヒー愛好家',
        '2025_03': 'コーヒー愛好家',
        '2025_04': 'コーヒー愛好家'
    }
    
    # 月別CSVファイルを取得
    csv_files = glob.glob('data/202*.csv')
    csv_files.sort()  # 日付順にソート
    
    print(f"読み込むCSVファイル: {csv_files}")
    
    for file_path in csv_files:
        try:
            # ファイル名から年月を抽出
            filename = os.path.basename(file_path)
            year_month = filename.replace('.csv', '')
            
            print(f"読み込み中: {filename}")
            
            # CSVファイルを読み込み
            df = pd.read_csv(file_path)
            
            # 日付列を解析
            df['date'] = pd.to_datetime(df['Day'], format='%Y年%m月%d日')
            df['year'] = df['date'].dt.year
            df['month'] = df['date'].dt.month
            df['day'] = df['date'].dt.day
            df['day_of_week'] = df['date'].dt.weekday
            
            # 豆名とユーザー名を追加
            df['bean_name'] = bean_mapping.get(year_month, 'エチオピア イルガチェフェ')
            df['user_name'] = user_mapping.get(year_month, 'コーヒー愛好家')
            
            # 天気の正規化
            df['weather'] = df['Weather'].map({
                '晴': '晴れ',
                'くもり': '曇り',
                '雨': '雨',
                'くもり/雨': '雨',
                '雪': '雪'
            }).fillna('晴れ')
            
            # 必要な列のみ選択
            df = df[['date', 'year', 'month', 'day', 'day_of_week', 
                    'weather', 'days_passed', 'mesh', 'gram', 'extraction_time',
                    'bean_name', 'user_name']]
            
            all_data.append(df)
            
        except Exception as e:
            print(f"エラー: {file_path}の読み込みに失敗 - {e}")
            continue
    
    if not all_data:
        raise Exception("読み込めるCSVファイルが見つかりませんでした")
    
    # 全データを結合
    combined_data = pd.concat(all_data, ignore_index=True)
    print(f"結合完了: {len(combined_data)}件のデータ")
    
    return combined_data

def load_weather_data():
    """京都の気象データを読み込み"""
    try:
        weather_df = pd.read_csv('data/kyoto_weather_data.csv')
        weather_df['date'] = pd.to_datetime(weather_df['date'])
        print(f"気象データ読み込み完了: {len(weather_df)}件")
        return weather_df
    except Exception as e:
        print(f"気象データ読み込みエラー: {e}")
        return pd.DataFrame()

def merge_data(monthly_data, weather_data):
    """月別データと気象データを結合"""
    try:
        # 日付で結合
        merged_data = monthly_data.merge(
            weather_data, 
            on='date', 
            how='left'
        )
        
        print(f"データ結合完了: {len(merged_data)}件")
        return merged_data
        
    except Exception as e:
        print(f"データ結合エラー: {e}")
        return monthly_data

def insert_csv_data():
    """CSVファイルからデータを挿入（insert_data_to_mysql.pyと同じ）"""
    try:
        mysql_config = get_mysql_config()
        connection = mysql.connector.connect(**mysql_config)
        cursor = connection.cursor()
        
        print("📊 CSVファイルからデータを読み込み中...")
        
        # 1. 月別CSVファイルを読み込み
        print("1. 月別CSVファイルの読み込み...")
        monthly_data = load_monthly_csv_files()
        
        # 2. 気象データを読み込み
        print("2. 気象データの読み込み...")
        weather_data = load_weather_data()
        
        # 3. データを結合
        print("3. データの結合...")
        merged_data = merge_data(monthly_data, weather_data)
        
        # 4. MySQLに挿入
        print("4. MySQLへの挿入...")
        insert_query = """
        INSERT INTO recipe (bean_id, date, weather, temperature, humidity, gram, mesh, extraction_time, days_passed)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        
        inserted_count = 0
        
        for _, row in merged_data.iterrows():
            try:
                # bean_idを取得
                cursor.execute("SELECT id FROM beans WHERE name = %s", (row['bean_name'],))
                bean_result = cursor.fetchone()
                
                if bean_result:
                    bean_id = bean_result[0]
                    
                    # データを挿入
                    cursor.execute(insert_query, (
                        bean_id,
                        row['date'].strftime('%Y-%m-%d'),
                        row['weather'],
                        row['temperature'],
                        row['humidity'],
                        row['gram'],
                        row['mesh'],
                        row['extraction_time'],
                        row['days_passed']
                    ))
                    inserted_count += 1
                else:
                    print(f"警告: 豆 '{row['bean_name']}' が見つかりません")
                    
            except Exception as e:
                print(f"行の挿入エラー: {e}")
                continue
        
        connection.commit()
        cursor.close()
        connection.close()
        
        print(f"CSVデータ挿入完了: {inserted_count}件")
        return inserted_count
        
    except Exception as e:
        print(f"CSVデータ読み込みエラー: {e}")
        return 0

def main():
    """メイン関数"""
    print("🚀 CSVデータ挿入スクリプトを開始...")
    
    # Spring Bootの起動完了を待機
    if not wait_for_spring_boot_completion():
        print("⚠️  Spring Bootの起動を待機できませんでしたが、続行します")
    
    # 既存データを確認
    user_count, bean_count, recipe_count = check_existing_data()
    
    # ユーザーと豆のデータが存在することを確認
    if user_count == 0 or bean_count == 0:
        print("❌ ユーザーまたはコーヒー豆のデータが存在しません。DataInitializerが実行されていることを確認してください。")
        sys.exit(1)
    
    print("✅ ユーザーとコーヒー豆のデータが確認されました")
    
    # CSVデータを挿入
    print("📝 CSVデータを挿入します...")
    inserted_count = insert_csv_data()
    
    if inserted_count > 0:
        print(f"✅ CSVデータ挿入が完了しました！ {inserted_count}件のレシピデータを挿入しました")
    else:
        print("❌ CSVデータの挿入に失敗しました")
    
    print("✅ CSVデータ挿入スクリプトが完了しました！")

if __name__ == "__main__":
    main()
