import pandas as pd
import numpy as np
import glob
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_squared_error, r2_score, accuracy_score
import matplotlib.pyplot as plt
import japanize_matplotlib


# --- ステップ1: データの読み込みと結合 ---
all_files = glob.glob('data/202*_*.csv')
print(all_files)
df_list = []
for filename in all_files:
    df_list.append(pd.read_csv(filename))

df = pd.concat(df_list, axis=0, ignore_index=True)
print("--- データの結合後 (最初の5行) ---")
print(df.head())
print(f"\n結合後のデータ数: {len(df)}件")


# --- ステップ2: データの前処理 ---
# 'Day'列から'Month'と'Day_of_month'を抽出
print(df)
df["Year"] = df["Day"].str.extract(r'(\d+)年').astype(int)
df['Month'] = df['Day'].str.extract(r'(\d+)月').astype(int)
df['Day'] = df['Day'].str.extract(r'(\d+)日').astype(int)



# 'Weather'列をOne-Hotエンコーディング
df = pd.get_dummies(df, columns=['Weather'], prefix='Weather')

print(df)

print("\n--- 前処理後のデータ (最初の5行) ---")
print(df.head())

# --- ステップ3: 特徴量とターゲットの分割 & 訓練/テスト分割 ---
# 予測したい3つの列をターゲット(y)に設定
y = df[['mesh', 'gram', 'extraction_time']]
# ターゲット以外の列を特徴量(X)に設定
X = df.drop(['mesh', 'gram', 'extraction_time'], axis=1)

# データを訓練データとテストデータに8:2の割合で分割
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
print(f"\n訓練データ数: {len(X_train)}件, テストデータ数: {len(X_test)}件")

# --- ステップ4: ランダムフォレストモデルの学習 ---
# n_estimatorsは決定木の数。100を初期値としてよく使われる。
model = RandomForestRegressor(n_estimators=100, random_state=42, oob_score=True)
model.fit(X_train, y_train)
print("\n--- モデルの学習完了 ---")
print(f"OOBスコア (学習データに対する予測精度): {model.oob_score_:.4f}")


# --- ステップ5: モデルの評価 ---
y_pred = model.predict(X_test)

# 正解率を確認
accuracy = accuracy_score(y_pred, y_test)
print(f"accuracy:{accyracy_score}")

# 各ターゲット変数の評価指標を計算
mse_mesh = mean_squared_error(y_test['mesh'], y_pred[:, 0])
r2_mesh = r2_score(y_test['mesh'], y_pred[:, 0])

mse_gram = mean_squared_error(y_test['gram'], y_pred[:, 1])
r2_gram = r2_score(y_test['gram'], y_pred[:, 1])

mse_ext_time = mean_squared_error(y_test['extraction_time'], y_pred[:, 2])
r2_ext_time = r2_score(y_test['extraction_time'], y_pred[:, 2])

print("\n--- モデルの評価結果 (テストデータ) ---")
print(f"Mesh - 平均二乗誤差 (MSE): {mse_mesh:.4f}, 決定係数 (R^2): {r2_mesh:.4f}")
print(f"Gram - 平均二乗誤差 (MSE): {mse_gram:.4f}, 決定係数 (R^2): {r2_gram:.4f}")
print(f"Extraction Time - 平均二乗誤差 (MSE): {mse_ext_time:.4f}, 決定係数 (R^2): {r2_ext_time:.4f}")

# --- ステップ6: 特徴量の重要度の可視化 ---
feature_importances = pd.Series(model.feature_importances_, index=X.columns)
feature_importances_sorted = feature_importances.sort_values(ascending=False)

plt.figure(figsize=(10, 6))
plt.bar(feature_importances_sorted.index, feature_importances_sorted.values)
plt.xlabel('特徴量')
plt.ylabel('重要度')
plt.title('特徴量の重要度')
plt.xticks(rotation=45, ha='right')
plt.tight_layout()
plt.savefig('feature_importance.png')

print("\n--- 特徴量の重要度 ---")
print(feature_importances_sorted)
print("\n特徴量の重要度を 'feature_importance.png' として保存しました。")