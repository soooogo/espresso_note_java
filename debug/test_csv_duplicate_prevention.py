#!/usr/bin/env python3
"""
CSV重複挿入防止機能のテストスクリプト
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
        
        # ユーザー数
        cursor.execute("SELECT COUNT(*) FROM users")
        user_count = cursor.fetchone()[0]
        print(f"ユーザー数: {user_count}")
        
        # 豆の数
        cursor.execute("SELECT COUNT(*) FROM beans")
        bean_count = cursor.fetchone()[0]
        print(f"コーヒー豆数: {bean_count}")
        
        # レシピ数
        cursor.execute("SELECT COUNT(*) FROM recipe")
        recipe_count = cursor.fetchone()[0]
        print(f"レシピ数: {recipe_count}")
        
        # 豆の詳細
        if bean_count > 0:
            print("\n=== コーヒー豆の詳細 ===")
            cursor.execute("SELECT id, name, origin FROM beans")
            beans = cursor.fetchall()
            for bean in beans:
                print(f"  ID: {bean[0]}, 名前: {bean[1]}, 産地: {bean[2]}")
        
        # レシピの詳細（最新5件）
        if recipe_count > 0:
            print("\n=== 最新のレシピ（5件） ===")
            cursor.execute("""
                SELECT r.id, b.name, r.date, r.extraction_time 
                FROM recipe r 
                JOIN beans b ON r.bean_id = b.id 
                ORDER BY r.id DESC 
                LIMIT 5
            """)
            recipes = cursor.fetchall()
            for recipe in recipes:
                print(f"  ID: {recipe[0]}, 豆: {recipe[1]}, 日付: {recipe[2]}, 抽出時間: {recipe[3]}秒")
        
        cursor.close()
        connection.close()
        
        return user_count, bean_count, recipe_count
        
    except Error as e:
        print(f"❌ データベース接続エラー: {e}")
        return 0, 0, 0

def test_csv_duplicate_prevention():
    """CSV重複挿入防止機能をテスト"""
    print("\n=== CSV重複挿入防止テスト ===")
    
    # 現在の状態を確認
    user_count, bean_count, recipe_count = check_database_status()
    
    if user_count == 0 or bean_count == 0:
        print("❌ ユーザーまたはコーヒー豆のデータが存在しません。")
        print("まずSpring Bootアプリケーションを起動してDataInitializerを実行してください。")
        return False
    
    print(f"\n✅ 前提条件確認完了: ユーザー={user_count}, 豆={bean_count}, レシピ={recipe_count}")
    
    # CSVデータ挿入スクリプトを実行
    print("\n📝 CSVデータ挿入スクリプトを実行中...")
    try:
        import subprocess
        result = subprocess.run([
            sys.executable, 
            "backend_server/insert_data.py"
        ], capture_output=True, text=True, cwd=os.getcwd())
        
        print("=== スクリプト出力 ===")
        print(result.stdout)
        
        if result.stderr:
            print("=== エラー出力 ===")
            print(result.stderr)
        
        # 実行後の状態を確認
        print("\n=== 実行後のデータベース状態 ===")
        new_user_count, new_bean_count, new_recipe_count = check_database_status()
        
        # 結果を分析
        recipe_increase = new_recipe_count - recipe_count
        
        if recipe_increase == 0:
            print("✅ 重複挿入防止機能が正常に動作しました（データが追加されませんでした）")
        else:
            print(f"ℹ️  {recipe_increase}件の新しいレシピが追加されました")
        
        return True
        
    except Exception as e:
        print(f"❌ スクリプト実行エラー: {e}")
        return False

def main():
    """メイン関数"""
    print("=== CSV重複挿入防止機能テスト ===")
    print("このスクリプトは、CSVデータの重複挿入防止機能をテストします。")
    print("")
    
    # データベースの状態を確認
    check_database_status()
    
    # 重複挿入防止テストを実行
    success = test_csv_duplicate_prevention()
    
    if success:
        print("\n✅ テストが完了しました！")
    else:
        print("\n❌ テストに失敗しました。")
    
    print("\n=== テスト結果の確認方法 ===")
    print("1. 上記のログ出力で重複チェックの動作を確認")
    print("2. データベースの状態変化を確認")
    print("3. 重複データが適切にスキップされていることを確認")

if __name__ == "__main__":
    main()
