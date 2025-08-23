import pandas as pd
import numpy as np
import pickle
import os
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_squared_error, r2_score, mean_absolute_error
import matplotlib.pyplot as plt
import japanize_matplotlib
from mysql_data_loader import MySQLDataLoader

def train_bean_specific_models():
    """豆ごとに個別のモデルを学習"""
    
    print("=== 豆ごとの個別モデル学習開始 ===")
    
    # MySQLデータローダーを初期化
    loader = MySQLDataLoader()
    
    # 学習用データセットを準備
    df = loader.prepare_training_data()
    
    if df is None or len(df) == 0:
        print("学習データの準備に失敗しました")
        return
    
    print(f"データ数: {len(df)}件")
    print(f"豆の種類: {df['bean_name'].unique()}")
    
    # modelディレクトリが存在しない場合は作成
    if not os.path.exists('model'):
        os.makedirs('model')
    
    # 豆ごとにモデルを学習
    bean_models = {}
    
    for bean_name in df['bean_name'].unique():
        print(f"\n=== {bean_name} のモデル学習 ===")
        
        # 特定の豆のデータのみを抽出
        bean_df = df[df['bean_name'] == bean_name].copy()
        
        if len(bean_df) < 5:  # データが少なすぎる場合はスキップ
            print(f"{bean_name}: データが少なすぎます（{len(bean_df)}件）。スキップします。")
            continue
        
        print(f"データ数: {len(bean_df)}件")
        
        # 特徴量とターゲットを分離
        feature_columns = [col for col in bean_df.columns if col not in ['id', 'bean_name', 'user_name', 'gram', 'mesh', 'extraction_time', 'date']]
        X = bean_df[feature_columns]
        y = bean_df[['mesh', 'gram', 'extraction_time']]
        
        print(f"特徴量数: {len(feature_columns)}個")
        print(f"特徴量: {feature_columns}")
        
        # データを分割
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
        
        # モデルを学習
        model = RandomForestRegressor(n_estimators=100, random_state=42)
        model.fit(X_train, y_train)
        
        # 予測
        y_pred = model.predict(X_test)
        
        # 評価指標を計算
        mse_mesh = mean_squared_error(y_test['mesh'], y_pred[:, 0])
        mse_gram = mean_squared_error(y_test['gram'], y_pred[:, 1])
        mse_extraction = mean_squared_error(y_test['extraction_time'], y_pred[:, 2])
        
        r2_mesh = r2_score(y_test['mesh'], y_pred[:, 0])
        r2_gram = r2_score(y_test['gram'], y_pred[:, 1])
        r2_extraction = r2_score(y_test['extraction_time'], y_pred[:, 2])
        
        mae_mesh = mean_absolute_error(y_test['mesh'], y_pred[:, 0])
        mae_gram = mean_absolute_error(y_test['gram'], y_pred[:, 1])
        mae_extraction = mean_absolute_error(y_test['extraction_time'], y_pred[:, 2])
        
        print(f"評価結果:")
        print(f"  Mesh - MSE: {mse_mesh:.4f}, R²: {r2_mesh:.4f}, MAE: {mae_mesh:.4f}")
        print(f"  Gram - MSE: {mse_gram:.4f}, R²: {r2_gram:.4f}, MAE: {mae_gram:.4f}")
        print(f"  Extraction Time - MSE: {mse_extraction:.4f}, R²: {r2_extraction:.4f}, MAE: {mae_extraction:.4f}")
        
        # 特徴量の重要度を表示
        feature_importances = pd.DataFrame({
            'feature': feature_columns,
            'importance': model.feature_importances_
        }).sort_values('importance', ascending=False)
        
        print(f"\n特徴量の重要度（上位5個）:")
        print(feature_importances.head())
        
        # モデルと前処理情報を保存
        bean_safe_name = bean_name.replace(' ', '_').replace('/', '_')
        model_filename = f'model/random_forest_{bean_safe_name}.pkl'
        preprocessing_filename = f'model/preprocessing_info_{bean_safe_name}.pkl'
        
        # モデルを保存
        with open(model_filename, 'wb') as f:
            pickle.dump(model, f)
        
        # 前処理情報を保存
        preprocessing_info = {
            'feature_names': feature_columns,
            'target_names': ['mesh', 'gram', 'extraction_time'],
            'bean_name': bean_name,
            'training_data_count': len(bean_df),
            'feature_importances': feature_importances.to_dict('records')
        }
        
        with open(preprocessing_filename, 'wb') as f:
            pickle.dump(preprocessing_info, f)
        
        # モデル情報を保存
        bean_models[bean_name] = {
            'model_file': model_filename,
            'preprocessing_file': preprocessing_filename,
            'feature_columns': feature_columns,
            'training_data_count': len(bean_df),
            'evaluation': {
                'mesh': {'mse': mse_mesh, 'r2': r2_mesh, 'mae': mae_mesh},
                'gram': {'mse': mse_gram, 'r2': r2_gram, 'mae': mae_gram},
                'extraction_time': {'mse': mse_extraction, 'r2': r2_extraction, 'mae': mae_extraction}
            }
        }
        
        print(f"モデルを保存しました: {model_filename}")
        print(f"前処理情報を保存しました: {preprocessing_filename}")
    
    # 全モデルの情報を保存
    with open('model/bean_models_info.pkl', 'wb') as f:
        pickle.dump(bean_models, f)
    
    print(f"\n=== 豆ごとのモデル学習完了 ===")
    print(f"生成されたモデル数: {len(bean_models)}個")
    
    # モデル一覧を表示
    print(f"\n生成されたモデル一覧:")
    for bean_name, info in bean_models.items():
        print(f"  {bean_name}: {info['training_data_count']}件のデータで学習")
    
    return bean_models

if __name__ == "__main__":
    train_bean_specific_models()
