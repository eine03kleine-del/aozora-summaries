import os
import requests
from flask import Flask, redirect, request
import subprocess

# ====== 設定 ======
CLIENT_ID = "a2ZvZFBLZnp0VkdiaEdGcGhOZ3A6MTpjaQ"
REDIRECT_URI = "http://localhost:8080/callback"
SCOPE = "tweet.read users.read follows.read follows.write offline.access"

app = Flask(__name__)

# ==== 認証URL ====
@app.route('/')
def login():
    auth_url = (
        "https://twitter.com/i/oauth2/authorize"
        f"?response_type=code"
        f"&client_id={CLIENT_ID}"
        f"&redirect_uri={REDIRECT_URI}"
        f"&scope={SCOPE}"
        f"&state=state123"
        f"&code_challenge=challenge"
        f"&code_challenge_method=plain"
    )
    return redirect(auth_url)

# ==== コールバック ====
@app.route('/callback')
def callback():
    code = request.args.get("code")
    print("=== 認可コード ===")
    print(code)

    token_url = "https://api.twitter.com/2/oauth2/token"
    data = {
        "grant_type": "authorization_code",
        "code": code,
        "redirect_uri": REDIRECT_URI,
        "code_verifier": "challenge",
        "client_id": CLIENT_ID,
    }
    headers = {"Content-Type": "application/x-www-form-urlencoded"}

    response = requests.post(token_url, data=data, headers=headers)
    if response.status_code != 200:
        return f"トークン取得失敗: {response.text}"

    token_info = response.json()
    access_token = token_info["access_token"]

    # === 保存 ===
    with open("access_token.txt", "w", encoding="utf-8") as f:
        f.write(access_token)
    print("✅ アクセストークンを保存しました。")

    # === フォロー解除スクリプト実行 ===
    subprocess.Popen(["python", "unfollow_15.py"])

    return "✅ 認証完了！このウィンドウは閉じてOKです。"

if __name__ == "__main__":
    app.run(host="127.0.0.1", port=8080, debug=True)
