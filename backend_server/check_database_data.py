import mysql.connector

def check_database_data():
    """データベースの状態を確認"""
    
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
        
        # ユーザー数を確認
        cursor.execute("SELECT COUNT(*) FROM users")
        user_count = cursor.fetchone()[0]
        print(f"ユーザー数: {user_count}")
        
        # 豆の数を確認
        cursor.execute("SELECT COUNT(*) FROM beans")
        bean_count = cursor.fetchone()[0]
        print(f"豆の数: {bean_count}")
        
        # レシピの数を確認
        cursor.execute("SELECT COUNT(*) FROM recipe")
        recipe_count = cursor.fetchone()[0]
        print(f"レシピの数: {recipe_count}")
        
        # 豆ごとのレシピ数を確認
        cursor.execute("""
            SELECT b.name, COUNT(r.id) as recipe_count
            FROM beans b
            LEFT JOIN recipe r ON b.id = r.bean_id
            GROUP BY b.id, b.name
            ORDER BY b.name
        """)
        
        print("\n=== 豆ごとのレシピ数 ===")
        for row in cursor.fetchall():
            bean_name, recipe_count = row
            print(f"{bean_name}: {recipe_count}件")
        
        # user1の豆とレシピを確認
        cursor.execute("""
            SELECT b.name, COUNT(r.id) as recipe_count
            FROM beans b
            LEFT JOIN recipe r ON b.id = r.bean_id
            JOIN users u ON b.user_id = u.id
            WHERE u.email = 'coffee.lover@example.com'
            GROUP BY b.id, b.name
            ORDER BY b.name
        """)
        
        print("\n=== user1の豆とレシピ数 ===")
        for row in cursor.fetchall():
            bean_name, recipe_count = row
            print(f"{bean_name}: {recipe_count}件")
        
        cursor.close()
        connection.close()
        
    except Exception as e:
        print(f"エラー: {e}")

if __name__ == "__main__":
    check_database_data()
