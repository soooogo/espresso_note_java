import pandas as pd
import mysql.connector
from datetime import datetime
import os
import glob
from typing import List, Dict

class DataInserter:
    def __init__(self):
        # MySQL接続設定
        self.mysql_config = {
            'host': 'localhost',
            'user': 'root',
            'password': '',
            'database': 'demo_db',
            'charset': 'utf8mb4'
        }
        
        # 豆のマッピング（月別CSVは全てエチオピア イルガチェフェ）
        self.bean_mapping = {
            '2024_11': 'エチオピア イルガチェフェ',
            '2024_12': 'エチオピア イルガチェフェ', 
            '2025_01': 'エチオピア イルガチェフェ',
            '2025_02': 'エチオピア イルガチェフェ',
            '2025_03': 'エチオピア イルガチェフェ',
            '2025_04': 'エチオピア イルガチェフェ'
        }
        
        # ユーザーマッピング
        self.user_mapping = {
            '2024_11': 'コーヒー愛好家',
            '2024_12': 'コーヒー愛好家',
            '2025_01': 'コーヒー愛好家',
            '2025_02': 'コーヒー愛好家',
            '2025_03': 'コーヒー愛好家',
            '2025_04': 'コーヒー愛好家'
        }
    
    def load_monthly_csv_files(self) -> pd.DataFrame:
        """月別CSVファイルを読み込んで結合"""
        all_data = []
        
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
                df['bean_name'] = self.bean_mapping.get(year_month, 'エチオピア イルガチェフェ')
                df['user_name'] = self.user_mapping.get(year_month, 'コーヒー愛好家')
                
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
    
    def load_weather_data(self) -> pd.DataFrame:
        """京都の気象データを読み込み"""
        try:
            weather_df = pd.read_csv('data/kyoto_weather_data.csv')
            weather_df['date'] = pd.to_datetime(weather_df['date'])
            print(f"気象データ読み込み完了: {len(weather_df)}件")
            return weather_df
        except Exception as e:
            print(f"気象データ読み込みエラー: {e}")
            return pd.DataFrame()
    
    def merge_data(self, monthly_data: pd.DataFrame, weather_data: pd.DataFrame) -> pd.DataFrame:
        """月別データと気象データを結合"""
        try:
            # 日付で結合
            merged_data = monthly_data.merge(
                weather_data, 
                on='date', 
                how='left'
            )
            
            # 気象データがない場合はデフォルト値を設定
            merged_data['temperature'] = merged_data['temperature'].fillna(20.0)
            merged_data['humidity'] = merged_data['humidity'].fillna(60.0)
            
            print(f"データ結合完了: {len(merged_data)}件")
            return merged_data
            
        except Exception as e:
            print(f"データ結合エラー: {e}")
            return monthly_data
    
    def check_csv_data_exists(self, cursor, df):
        """CSVデータが既にデータベースに存在するかチェック"""
        print("🔍 CSVデータの重複チェックを実行中...")
        
        existing_count = 0
        total_csv_count = len(df)
        
        for _, row in df.iterrows():
            try:
                # bean_idを取得
                cursor.execute("SELECT id FROM beans WHERE name = %s", (row['bean_name'],))
                bean_result = cursor.fetchone()
                
                if bean_result:
                    bean_id = bean_result[0]
                    
                    # 重複チェック: 同じbean_id、日付、抽出時間の組み合わせが既に存在するかチェック
                    check_query = """
                    SELECT COUNT(*) FROM recipe 
                    WHERE bean_id = %s AND date = %s AND extraction_time = %s
                    """
                    cursor.execute(check_query, (
                        bean_id,
                        row['date'].strftime('%Y-%m-%d'),
                        row['extraction_time']
                    ))
                    duplicate_count = cursor.fetchone()[0]
                    
                    if duplicate_count > 0:
                        existing_count += 1
                        
            except Exception as e:
                print(f"重複チェックエラー: {e}")
                continue
        
        print(f"📊 重複チェック結果: {existing_count}/{total_csv_count} 件が既に存在")
        return existing_count, total_csv_count

    def insert_to_mysql(self, df: pd.DataFrame):
        """データをMySQLに挿入（厳密な重複チェック付き）"""
        try:
            connection = mysql.connector.connect(**self.mysql_config)
            cursor = connection.cursor()
            
            # 重複チェックを実行
            existing_count, total_count = self.check_csv_data_exists(cursor, df)
            
            # 重複率を計算
            duplicate_rate = (existing_count / total_count) * 100 if total_count > 0 else 0
            
            if existing_count == total_count:
                print(f"⚠️  CSVデータの100%が既に存在します。挿入をスキップします。")
                cursor.close()
                connection.close()
                return 0
            elif duplicate_rate > 80:
                print(f"⚠️  CSVデータの{duplicate_rate:.1f}%が既に存在します。挿入をスキップします。")
                cursor.close()
                connection.close()
                return 0
            elif existing_count > 0:
                print(f"ℹ️  CSVデータの{duplicate_rate:.1f}%が既に存在しますが、新規データを挿入します。")
            
            # データを挿入
            insert_query = """
            INSERT INTO recipe (bean_id, date, weather, temperature, humidity, gram, mesh, extraction_time, days_passed)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            """
            
            inserted_count = 0
            skipped_count = 0
            
            for _, row in df.iterrows():
                try:
                    # bean_idを取得
                    cursor.execute("SELECT id FROM beans WHERE name = %s", (row['bean_name'],))
                    bean_result = cursor.fetchone()
                    
                    if bean_result:
                        bean_id = bean_result[0]
                        
                        # 重複チェック: 同じbean_id、日付、抽出時間の組み合わせが既に存在するかチェック
                        check_query = """
                        SELECT COUNT(*) FROM recipe 
                        WHERE bean_id = %s AND date = %s AND extraction_time = %s
                        """
                        cursor.execute(check_query, (
                            bean_id,
                            row['date'].strftime('%Y-%m-%d'),
                            row['extraction_time']
                        ))
                        duplicate_count = cursor.fetchone()[0]
                        
                        if duplicate_count == 0:
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
                            skipped_count += 1
                            if skipped_count <= 5:  # 最初の5件のみログ出力
                                print(f"重複データをスキップ: {row['date'].strftime('%Y-%m-%d')} - {row['bean_name']}")
                            elif skipped_count == 6:
                                print("... (重複データのスキップログを省略)")
                    else:
                        print(f"警告: 豆 '{row['bean_name']}' が見つかりません")
                        
                except Exception as e:
                    print(f"行の挿入エラー: {e}")
                    continue
            
            connection.commit()
            cursor.close()
            connection.close()
            
            print(f"MySQL挿入完了: {inserted_count}件挿入, {skipped_count}件スキップ")
            return inserted_count
            
        except Exception as e:
            print(f"MySQL挿入エラー: {e}")
            return 0
    
    def save_merged_csv(self, df: pd.DataFrame):
        """結合したデータをCSVファイルとして保存"""
        try:
            output_file = 'data/merged_monthly_weather_data.csv'
            df.to_csv(output_file, index=False)
            print(f"結合データを保存しました: {output_file}")
            
            # 統計情報を表示
            print(f"\n=== 結合データ統計 ===")
            print(f"総レコード数: {len(df)}")
            print(f"期間: {df['date'].min()} ～ {df['date'].max()}")
            print(f"豆の種類: {df['bean_name'].nunique()}種類")
            print(f"ユーザー数: {df['user_name'].nunique()}人")
            print(f"気温範囲: {df['temperature'].min():.1f}°C - {df['temperature'].max():.1f}°C")
            print(f"湿度範囲: {df['humidity'].min():.1f}% - {df['humidity'].max():.1f}%")
            
        except Exception as e:
            print(f"CSV保存エラー: {e}")

def main():
    print("月別CSVファイルと気象データの結合・MySQL挿入を開始...")
    
    inserter = DataInserter()
    
    try:
        # 1. 月別CSVファイルを読み込み
        print("\n1. 月別CSVファイルの読み込み...")
        monthly_data = inserter.load_monthly_csv_files()
        
        # 2. 気象データを読み込み
        print("\n2. 気象データの読み込み...")
        weather_data = inserter.load_weather_data()
        
        # 3. データを結合
        print("\n3. データの結合...")
        merged_data = inserter.merge_data(monthly_data, weather_data)
        
        # 4. 結合データをCSVとして保存
        print("\n4. 結合データの保存...")
        inserter.save_merged_csv(merged_data)
        
        # 5. MySQLに挿入
        print("\n5. MySQLへの挿入...")
        inserted_count = inserter.insert_to_mysql(merged_data)
        
        if inserted_count > 0:
            print(f"\n✅ 完了！ {inserted_count}件のデータをMySQLに挿入しました")
        else:
            print("\n❌ MySQLへの挿入に失敗しました")
            
    except Exception as e:
        print(f"\n❌ エラーが発生しました: {e}")

if __name__ == "__main__":
    main()
