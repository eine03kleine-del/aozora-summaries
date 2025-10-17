import requests
import json
import os
import time

# === 設定 ===
TOKEN_FILE = "tokens/access_token.txt"  # auto_unfollow_refresh.py が保存するトークンファイル
FOLLOW_LIMIT = 15  # 一度に処理するフォロー数

# === アクセストークン読み込み ===
if not os.path.exists(TOKEN_FILE):
    raise FileNotFoundError(f"アクセストークンが見つかりません: {TOKEN_FILE}")

with open(TOKEN_FILE, "r", encoding="utf-8") as f:
    ACCESS_TOKEN = f.read().strip()

HEADERS = {
    "Authorization": f"Bearer {ACCESS_TOKEN}",
    "Content-Type": "application/json"
}


# === 自分のユーザーID取得 ===
def get_my_user_id():
    url = "https://api.twitter.com/2/users/me"
    res = requests.get(url, headers=HEADERS)
    if res.status_code != 200:
        raise Exception(f"ユーザー情報取得失敗: {res.status_code} {res.text}")
    data = res.json()
    return data["data"]["id"], data["data"]["username"]


# === フォロー中ユーザーを取得 ===
def get_following(user_id, limit=FOLLOW_LIMIT):
    url = f"https://api.twitter.com/2/users/{user_id}/following?max_results={limit}"
    res = requests.get(url, headers=HEADERS)

    if res.status_code != 200:
        raise Exception(f"フォロー取得失敗: {res.status_code} {res.text}")

    data = res.json()
    return data.get("data", [])


# === フォロー解除 ===
def unfollow(user_id, target_id, target_name):
    url = f"https://api.twitter.com/2/users/{user_id}/following/{target_id}"
    res = requests.delete(url, headers=HEADERS)
    if res.status_code == 200:
        print(f"✅ 解除成功: {target_name} ({target_id})")
    else:
        print(f"❌ 解除失敗: {target_name} ({target_id}) {res.status_code} {res.text}")


# === メイン処理 ===
if __name__ == "__main__":
    print("=== X (Twitter) フォロー解除ツール ===")

    try:
        my_id, my_name = get_my_user_id()
        print(f"👤 ユーザー: {my_name} (ID: {my_id})")
    except Exception as e:
        print(f"ユーザー情報取得に失敗しました: {e}")
        exit()

    try:
        following = get_following(my_id, FOLLOW_LIMIT)
    except Exception as e:
        print(f"フォローリスト取得に失敗しました: {e}")
        exit()

    if not following:
        print("⚠️ フォロー中のアカウントが見つかりません。")
        exit()

    print(f"🔍 {len(following)}件のアカウントを解除します...")

    for user in following:
        target_id = user["id"]
        target_name = user["username"]
        unfollow(my_id, target_id, target_name)
        time.sleep(1)  # API制限回避のため1秒間隔

    print("✅ 完了しました。")
