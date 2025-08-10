import pandas as pd


df = pd.read_csv('2024_11.csv', encoding='shift-jis') 


cleaned_df = df.dropna(subset=['Weather'])

print(cleaned_df)

# 結果を新しいCSVファイルとして保存する
cleaned_df.to_csv("cleaned_2024_11.csv", index=False)