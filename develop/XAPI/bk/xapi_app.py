import base64
import requests
from flask import Flask, redirect, request

app = Flask(__name__)

CLIENT_ID = "a2ZvZFBLZnp0VkdiaEdGcGhOZ3A6MTpjaQ"
CLIENT_SECRET = "mCESQxkbf4uOqr0mGWC2GVAiWCBPRZbsfd-l6qAEe8fHilkDlo"
REDIRECT_URI = "http://localhost:8080/callback"
SCOPE = "tweet.read users.read follows.read follows.write offline.access"

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

@app.route('/callback')
def callback():
    code = request.args.get("code")
    print("DEBUG: code =", code)

    # Basic認証用ヘッダー（client_id + client_secret）
    credentials = f"{CLIENT_ID}:{CLIENT_SECRET}"
    b64_credentials = base64.b64encode(credentials.encode()).decode()

    token_url = "https://api.twitter.com/2/oauth2/token"
    data = {
        "grant_type": "authorization_code",
        "code": code,
        "redirect_uri": REDIRECT_URI,
        "code_verifier": "challenge",
    }

    headers = {
        "Content-Type": "application/x-www-form-urlencoded",
        "Authorization": f"Basic {b64_credentials}",  # ← これが重要！
    }

    response = requests.post(token_url, data=data, headers=headers)
    print("DEBUG: token response:", response.text)

    if response.status_code != 200:
        return f"トークン取得失敗: {response.text}"

    token_info = response.json()
    print("=== トークン取得成功 ===")
    print(token_info)
    return token_info

if __name__ == "__main__":
    app.run(host="127.0.0.1", port=8080, debug=True)
