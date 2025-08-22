import mysql.connector
from mysql.connector import Error

def create_database_tables():
    """MySQLデータベースにテーブルを作成"""
    
    # MySQL接続設定
    config = {
        'host': 'localhost',
        'user': 'root',
        'password': '',
        'charset': 'utf8mb4'
    }
    
    try:
        # データベースに接続
        connection = mysql.connector.connect(**config)
        cursor = connection.cursor()
        
        # demo_dbデータベースを作成（存在しない場合）
        cursor.execute("CREATE DATABASE IF NOT EXISTS demo_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci")
        cursor.execute("USE demo_db")
        
        print("demo_dbデータベースに接続しました")
        
        # userテーブルを作成
        create_user_table = """
        CREATE TABLE IF NOT EXISTS user (
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
            `from` VARCHAR(100) NOT NULL,
            FOREIGN KEY (user_id) REFERENCES user(id) ON DELETE CASCADE
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
        
        # テーブルを作成
        cursor.execute(create_user_table)
        print("userテーブルを作成しました")
        
        cursor.execute(create_beans_table)
        print("beansテーブルを作成しました")
        
        cursor.execute(create_recipe_table)
        print("recipeテーブルを作成しました")
        
        # 変更をコミット
        connection.commit()
        
        # テーブルの存在確認
        cursor.execute("SHOW TABLES")
        tables = cursor.fetchall()
        print(f"作成されたテーブル: {[table[0] for table in tables]}")
        
        cursor.close()
        connection.close()
        
        print("データベースとテーブルの作成が完了しました！")
        return True
        
    except Error as e:
        print(f"データベース作成エラー: {e}")
        return False

if __name__ == "__main__":
    create_database_tables()
