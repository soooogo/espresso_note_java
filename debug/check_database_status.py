#!/usr/bin/env python3
"""
データベースの状態を簡単に確認するスクリプト
"""

import os
import sys
import mysql.connector
from mysql.connector import Error

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
            'host': 'localhost',
            'user': 'demo_user',
            'password': 'demo_password',
            'database': 'demo_db',
            'charset': 'utf8mb4'
        }

def check_database_status():
    """データベースの現在の状態を確認"""
    try:
        mysql_config = get_mysql_config()
        connection = mysql.connector.connect(**mysql_config)
        cursor = connection.cursor()
        
        print("=== データベースの現在の状態 ===")
        print()
        
        # ユーザー数
        cursor.execute("SELECT COUNT(*) FROM users")
        user_count = cursor.fetchone()[0]
        print(f"👥 ユーザー数: {user_count}")
        
        # 豆の数
        cursor.execute("SELECT COUNT(*) FROM beans")
        bean_count = cursor.fetchone()[0]
        print(f"☕ コーヒー豆数: {bean_count}")
        
        # レシピ数
        cursor.execute("SELECT COUNT(*) FROM recipe")
        recipe_count = cursor.fetchone()[0]
        print(f"📝 レシピ数: {recipe_count}")
        
        print()
        
        # ユーザーの詳細
        if user_count > 0:
            print("=== ユーザー一覧 ===")
            cursor.execute("SELECT id, name, email, role FROM users")
            users = cursor.fetchall()
            for user in users:
                print(f"  ID: {user[0]}, 名前: {user[1]}, メール: {user[2]}, 役割: {user[3]}")
            print()
        
        # 豆の詳細
        if bean_count > 0:
            print("=== コーヒー豆一覧 ===")
            cursor.execute("SELECT id, name, origin, user_id FROM beans")
            beans = cursor.fetchall()
            for bean in beans:
                print(f"  ID: {bean[0]}, 名前: {bean[1]}, 産地: {bean[2]}, ユーザーID: {bean[3]}")
            print()
        
        # レシピの統計
        if recipe_count > 0:
            print("=== レシピ統計 ===")
            
            # 豆別のレシピ数
            cursor.execute("""
                SELECT b.name, COUNT(r.id) as recipe_count 
                FROM beans b 
                LEFT JOIN recipe r ON b.id = r.bean_id 
                GROUP BY b.id, b.name 
                ORDER BY recipe_count DESC
            """)
            bean_stats = cursor.fetchall()
            for stat in bean_stats:
                print(f"  {stat[0]}: {stat[1]}件")
            
            print()
            
            # 最新のレシピ（5件）
            print("=== 最新のレシピ（5件） ===")
            cursor.execute("""
                SELECT r.id, b.name, r.date, r.weather, r.temperature, r.extraction_time 
                FROM recipe r 
                JOIN beans b ON r.bean_id = b.id 
                ORDER BY r.id DESC 
                LIMIT 5
            """)
            recipes = cursor.fetchall()
            for recipe in recipes:
                print(f"  ID: {recipe[0]}, 豆: {recipe[1]}, 日付: {recipe[2]}, 天気: {recipe[3]}, 気温: {recipe[4]}°C, 抽出時間: {recipe[5]}秒")
        
        cursor.close()
        connection.close()
        
        return user_count, bean_count, recipe_count
        
    except Error as e:
        print(f"❌ データベース接続エラー: {e}")
        print("Docker Composeサービスが起動しているか確認してください。")
        return 0, 0, 0

def main():
    """メイン関数"""
    print("🔍 データベース状態確認ツール")
    print("=" * 50)
    
    user_count, bean_count, recipe_count = check_database_status()
    
    print()
    print("=" * 50)
    
    if user_count == 0 and bean_count == 0 and recipe_count == 0:
        print("⚠️  データベースが空です。")
        print("Spring Bootアプリケーションを起動してDataInitializerを実行してください。")
    else:
        print("✅ データベースにデータが存在します。")
        
        if recipe_count == 0:
            print("ℹ️  レシピデータがありません。CSVデータ挿入スクリプトを実行してください。")

if __name__ == "__main__":
    main()
