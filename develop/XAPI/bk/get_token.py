import requests
from flask import Flask, redirect, request
import base64

app = Flask(__name__)

CLIENT_ID = "a2ZvZFBLZnp0VkdiaEdGcGhOZ3A6MTpjaQ"
CLIENT_SECRET = "mCESQxkbf4uOqr0mGWC2GVAiWCBPRZbsfd-l6qAEe8fHilkDlo"  # ← これを追加
REDIRECT_URI = "http://localhost:8080/callback"
SCOPE = "tweet.read users.read follows.write offline.access"
CODE_CHALLENGE = "challenge"

@app.route("/")
def login():
    auth_url = (
        "https://twitter.com/i/oauth2/authorize"
        f"?response_type=code"
        f"&client_id={CLIENT_ID}"
        f"&redirect_uri={REDIRECT_URI}"
        f"&scope={SCOPE.replace(' ', '%20')}"
        f"&state=state123"
        f"&code_challenge={CODE_CHALLENGE}"
        f"&code_challenge_method=plain"
    )
    return redirect(auth_url)

@app.route("/callback")
def callback():
    code = request.args.get("code")
    print(f"=== 認可コード: {code} ===")

    token_url = "https://api.twitter.com/2/oauth2/token"
    data = {
        "grant_type": "authorization_code",
        "redirect_uri": REDIRECT_URI,
        "code_verifier": CODE_CHALLENGE,
        "code": code,
    }

    # ← ここが重要：Basic認証ヘッダーを追加
    auth_str = f"{CLIENT_ID}:{CLIENT_SECRET}"
    b64_auth = base64.b64encode(auth_str.encode()).decode()

    headers = {
        "Authorization": f"Basic {b64_auth}",
        "Content-Type": "application/x-www-form-urlencoded"
    }

    response = requests.post(token_url, data=data, headers=headers)
    print("=== トークンレスポンス ===")
    print(response.text)

    return response.text

if __name__ == "__main__":
    app.run(port=8080, debug=True)
