from flask import Flask, redirect, request
import requests, json, time, os
import base64, hashlib, secrets

# === 認証情報 ===
CLIENT_ID = "WHk3N3o2b2g2NlN0OHlBaTJaN0c6MTpjaQ"
CLIENT_SECRET = "ebuCAfxLWY7E7EWpiZ3Th4WVDq5CtRQei_SjHNjRZqforyweag"
REDIRECT_URI = "http://localhost:8080/callback"

# === トークン保存先 ===
TOKENS_DIR = os.path.join(os.path.dirname(__file__), "../tokens")
ACCESS_FILE = os.path.join(TOKENS_DIR, "access_token.txt")
REFRESH_FILE = os.path.join(TOKENS_DIR, "refresh_token.txt")

# === PKCEコード生成 ===
def generate_pkce():
    verifier = secrets.token_urlsafe(64)
    challenge = base64.urlsafe_b64encode(
        hashlib.sha256(verifier.encode()).digest()
    ).rstrip(b'=').decode('utf-8')
    return verifier, challenge

# グローバル変数として保持（簡易実装）
code_verifier, code_challenge = generate_pkce()

# === Flaskアプリ起動 ===
app = Flask(__name__)

@app.route("/")
def index():
    auth_url = (
        f"https://twitter.com/i/oauth2/authorize?response_type=code"
        f"&client_id={CLIENT_ID}"
        f"&redirect_uri={REDIRECT_URI}"
        f"&scope=tweet.read%20users.read%20follows.read%20follows.write%20offline.access"
        f"&state=state123"
        f"&code_challenge={code_challenge}"
        f"&code_challenge_method=S256"
    )
    return redirect(auth_url)

@app.route("/callback")
def callback():
    code = request.args.get("code")
    print("=== 認可コード ===")
    print(code)

    token_url = "https://api.twitter.com/2/oauth2/token"
    data = {
        "code": code,
        "grant_type": "authorization_code",
        "redirect_uri": REDIRECT_URI,
        "client_id": CLIENT_ID,
        "code_verifier": code_verifier,
    }

    res = requests.post(token_url, data=data, auth=(CLIENT_ID, CLIENT_SECRET))

    if res.status_code != 200:
        return f"トークン取得失敗: {res.status_code} {res.text}", 500

    tokens = res.json()
    print("✅ アクセストークンを保存しました。")

    os.makedirs(TOKENS_DIR, exist_ok=True)
    with open(ACCESS_FILE, "w", encoding="utf-8") as f:
        f.write(tokens["access_token"])
    with open(REFRESH_FILE, "w", encoding="utf-8") as f:
        f.write(tokens["refresh_token"])

    tokens["saved_at"] = int(time.time())
    print(json.dumps(tokens, indent=2, ensure_ascii=False))
    return "✅ トークン取得完了！ このウィンドウは閉じてOKです。"

if __name__ == "__main__":
    app.run(host="127.0.0.1", port=8080, debug=False)
