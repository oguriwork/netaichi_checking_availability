import os
import time
import shutil
import pandas as pd
from selenium import webdriver
from selenium.webdriver.chrome.options import Options



chrome_options.add_experimental_option("prefs", prefs)
# chrome_options.add_argument("--headless=new")  # 必要なら有効化
driver = webdriver.Chrome(options=chrome_options)

# ダウンロードページへアクセス
driver.get("https://example.com/download_page")

# アカウントIDを設定
account_id = "user123"

# ダウンロードボタンをクリック
driver.find_element("id", "download_csv").click()

# 元ファイル名（ダウンロードされる固定の名前）
original_name = "sample.csv"
original_path = os.path.join(download_dir, original_name)

# ダウンロード完了待ち（最大60秒）
timeout = 60
start = time.time()
while True:
    if os.path.exists(original_path) and not os.path.exists(original_path + ".crdownload"):
        break
    if time.time() - start > timeout:
        raise TimeoutError("ダウンロードがタイムアウトしました")
    time.sleep(1)

# 保存先（アカウントID名にリネーム）
new_name = f"{account_id}.csv"
new_path = os.path.join(download_dir, new_name)

# 上書き保存（既にあれば削除してからリネーム）
if os.path.exists(new_path):
    os.remove(new_path)

shutil.move(original_path, new_path)
print(f"保存完了: {new_path}")

# 読み込み確認（必要なら）
df = pd.read_csv(new_path)
print(df.head())

driver.quit()
