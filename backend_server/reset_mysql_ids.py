import mysql.connector
from mysql.connector import Error

def reset_mysql_ids():
    """MySQLの各テーブルのAUTO_INCREMENTをリセット"""
    
    # MySQL接続設定
    mysql_config = {
        'host': 'localhost',
        'user': 'root',
        'password': '',
        'database': 'demo_db',
        'charset': 'utf8mb4'
    }
    
    try:
        # MySQLに接続
        connection = mysql.connector.connect(**mysql_config)
        cursor = connection.cursor()
        
        print("MySQL接続成功")
        
        # リセット対象のテーブル
        tables = ['users', 'beans', 'recipe']
        
        for table in tables:
            try:
                # テーブルのデータを削除
                cursor.execute(f"DELETE FROM {table}")
                print(f"✓ {table}テーブルのデータを削除しました")
                
                # AUTO_INCREMENTをリセット
                cursor.execute(f"ALTER TABLE {table} AUTO_INCREMENT = 1")
                print(f"✓ {table}テーブルのAUTO_INCREMENTをリセットしました")
                
            except Error as e:
                print(f"✗ {table}テーブルの処理でエラー: {e}")
                continue
        
        # 変更をコミット
        connection.commit()
        print("\n✅ すべてのテーブルのIDリセットが完了しました")
        
        # 各テーブルの現在の状態を確認
        print("\n=== テーブル状態確認 ===")
        for table in tables:
            cursor.execute(f"SELECT COUNT(*) FROM {table}")
            count = cursor.fetchone()[0]
            print(f"{table}: {count}件のレコード")
        
        cursor.close()
        connection.close()
        
    except Error as e:
        print(f"MySQL接続エラー: {e}")
    except Exception as e:
        print(f"予期しないエラー: {e}")

def check_table_structure():
    """テーブル構造を確認"""
    
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
        
        print("=== テーブル構造確認 ===")
        
        tables = ['users', 'beans', 'recipe']
        for table in tables:
            print(f"\n{table}テーブル:")
            cursor.execute(f"DESCRIBE {table}")
            columns = cursor.fetchall()
            
            for column in columns:
                print(f"  {column[0]}: {column[1]} {column[2]} {column[3]} {column[4]} {column[5]}")
        
        cursor.close()
        connection.close()
        
    except Error as e:
        print(f"テーブル構造確認エラー: {e}")

if __name__ == "__main__":
    print("MySQLのIDリセットを開始します...")
    print("注意: この操作により、すべてのテーブルのデータが削除されます")
    
    # 確認メッセージ
    response = input("続行しますか？ (y/N): ")
    if response.lower() == 'y':
        reset_mysql_ids()
        print("\nテーブル構造を確認します...")
        check_table_structure()
    else:
        print("操作をキャンセルしました")
