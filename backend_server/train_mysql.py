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

def train_model_from_mysql():
    """MySQLからデータを取得してモデルを学習"""
    
    print("=== MySQLデータベースから学習データを取得 ===")
    
    # 既に作成されたデータセットを読み込み
    try:
        df = pd.read_csv('data/mysql_training_data.csv')
        print(f"保存済みデータセットを読み込みました: {len(df)}件")
    except FileNotFoundError:
        # MySQLデータローダーを初期化
        loader = MySQLDataLoader()
        
        # 学習用データセットを準備
        df = loader.prepare_training_data()
        
        if df is None or len(df) == 0:
            print("学習データの準備に失敗しました")
            return None
    
    print("\n=== データの前処理 ===")
    print(f"データ数: {len(df)}件")
    print(f"特徴量数: {len(df.columns)}個")
    
    # データの基本情報を表示
    print("\n--- データの基本情報 ---")
    print(df.info())
    
    print("\n--- データの統計情報 ---")
    print(df.describe())
    
    # 欠損値の確認
    print("\n--- 欠損値の確認 ---")
    print(df.isnull().sum())
    
    # 欠損値を処理
    df = df.fillna(0)
    
    # 特徴量とターゲットの分割
    target_columns = ['mesh', 'gram', 'extraction_time']
    feature_columns = [col for col in df.columns if col not in target_columns + ['id', 'date', 'bean_name', 'user_name']]
    
    X = df[feature_columns]
    y = df[target_columns]
    
    print(f"\n特徴量数: {len(feature_columns)}")
    print(f"ターゲット数: {len(target_columns)}")
    
    # 訓練データとテストデータに分割
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    
    print(f"\n訓練データ数: {len(X_train)}件")
    print(f"テストデータ数: {len(X_test)}件")
    
    # モデルの学習
    print("\n=== モデルの学習 ===")
    model = RandomForestRegressor(
        n_estimators=100,
        random_state=42,
        oob_score=True,
        n_jobs=-1
    )
    
    model.fit(X_train, y_train)
    print(f"OOBスコア: {model.oob_score_:.4f}")
    
    # 予測
    y_pred = model.predict(X_test)
    
    # 評価指標の計算
    print("\n=== モデルの評価 ===")
    
    # 全体の評価
    mae = mean_absolute_error(y_test, y_pred)
    mse = mean_squared_error(y_test, y_pred)
    rmse = np.sqrt(mse)
    
    print(f"平均絶対誤差 (MAE): {mae:.4f}")
    print(f"平均二乗誤差 (MSE): {mse:.4f}")
    print(f"平均二乗誤差の平方根 (RMSE): {rmse:.4f}")
    
    # 各ターゲット変数の評価
    for i, target in enumerate(target_columns):
        r2 = r2_score(y_test.iloc[:, i], y_pred[:, i])
        mae_target = mean_absolute_error(y_test.iloc[:, i], y_pred[:, i])
        print(f"\n{target}:")
        print(f"  決定係数 (R²): {r2:.4f}")
        print(f"  平均絶対誤差 (MAE): {mae_target:.4f}")
    
    # 特徴量の重要度
    print("\n=== 特徴量の重要度 ===")
    feature_importances = pd.Series(model.feature_importances_, index=feature_columns)
    feature_importances_sorted = feature_importances.sort_values(ascending=False)
    
    print("上位10個の特徴量:")
    for i, (feature, importance) in enumerate(feature_importances_sorted.head(10).items()):
        print(f"{i+1:2d}. {feature}: {importance:.4f}")
    
    # 特徴量の重要度を可視化
    plt.figure(figsize=(12, 8))
    plt.bar(range(len(feature_importances_sorted)), feature_importances_sorted.values)
    plt.xlabel('特徴量')
    plt.ylabel('重要度')
    plt.title('特徴量の重要度 (MySQLデータ)')
    plt.xticks(range(len(feature_importances_sorted)), feature_importances_sorted.index, rotation=45, ha='right')
    plt.tight_layout()
    plt.savefig('feature_importance_mysql.png', dpi=300, bbox_inches='tight')
    print("\n特徴量の重要度を 'feature_importance_mysql.png' として保存しました")
    
    # モデルの保存
    print("\n=== モデルの保存 ===")
    if not os.path.exists('model'):
        os.makedirs('model')
    
    # モデルを保存
    with open('model/random_forest_mysql_model.pkl', 'wb') as f:
        pickle.dump(model, f)
    
    # 前処理情報を保存
    preprocessing_info = {
        'feature_names': feature_columns,
        'target_names': target_columns,
        'categorical_columns': ['weather', 'bean_origin'],
        'numerical_columns': ['year', 'month', 'day', 'day_of_week', 'temperature', 'humidity'],
        'data_source': 'mysql_demo_db'
    }
    
    with open('model/preprocessing_info_mysql.pkl', 'wb') as f:
        pickle.dump(preprocessing_info, f)
    
    print("モデルを 'model/random_forest_mysql_model.pkl' として保存しました")
    print("前処理情報を 'model/preprocessing_info_mysql.pkl' として保存しました")
    
    return model, preprocessing_info

def analyze_predictions(model, X_test, y_test, y_pred):
    """予測結果の詳細分析"""
    print("\n=== 予測結果の詳細分析 ===")
    
    # 予測値と実際の値の比較
    comparison_df = pd.DataFrame({
        'actual_mesh': y_test.iloc[:, 0],
        'predicted_mesh': y_pred[:, 0],
        'actual_gram': y_test.iloc[:, 1],
        'predicted_gram': y_pred[:, 1],
        'actual_extraction_time': y_test.iloc[:, 2],
        'predicted_extraction_time': y_pred[:, 2]
    })
    
    # 誤差の計算
    comparison_df['mesh_error'] = comparison_df['actual_mesh'] - comparison_df['predicted_mesh']
    comparison_df['gram_error'] = comparison_df['actual_gram'] - comparison_df['predicted_gram']
    comparison_df['extraction_time_error'] = comparison_df['actual_extraction_time'] - comparison_df['predicted_extraction_time']
    
    print("予測誤差の統計:")
    print(comparison_df[['mesh_error', 'gram_error', 'extraction_time_error']].describe())
    
    # 予測精度の可視化
    fig, axes = plt.subplots(1, 3, figsize=(15, 5))
    
    targets = ['mesh', 'gram', 'extraction_time']
    for i, target in enumerate(targets):
        actual = comparison_df[f'actual_{target}']
        predicted = comparison_df[f'predicted_{target}']
        
        axes[i].scatter(actual, predicted, alpha=0.6)
        axes[i].plot([actual.min(), actual.max()], [actual.min(), actual.max()], 'r--', lw=2)
        axes[i].set_xlabel(f'実際の{target}')
        axes[i].set_ylabel(f'予測{target}')
        axes[i].set_title(f'{target}の予測精度')
        
        # R²スコアを表示
        r2 = r2_score(actual, predicted)
        axes[i].text(0.05, 0.95, f'R² = {r2:.3f}', transform=axes[i].transAxes, 
                    bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.8))
    
    plt.tight_layout()
    plt.savefig('prediction_accuracy_mysql.png', dpi=300, bbox_inches='tight')
    print("予測精度の可視化を 'prediction_accuracy_mysql.png' として保存しました")

if __name__ == "__main__":
    # モデルの学習
    result = train_model_from_mysql()
    
    if result is not None:
        model, preprocessing_info = result
        
        # テストデータで予測結果を分析
        loader = MySQLDataLoader()
        df = loader.prepare_training_data()
        
        if df is not None:
            target_columns = ['mesh', 'gram', 'extraction_time']
            feature_columns = preprocessing_info['feature_names']
            
            X = df[feature_columns]
            y = df[target_columns]
            
            _, X_test, _, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
            y_pred = model.predict(X_test)
            
            analyze_predictions(model, X_test, y_test, y_pred)
        
        print("\n=== 学習完了 ===")
        print("MySQLデータベースから取得したデータでモデルの学習が完了しました！")
    else:
        print("モデルの学習に失敗しました")
