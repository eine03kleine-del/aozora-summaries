import requests
from bs4 import BeautifulSoup

url = "https://www.aozora.gr.jp/index_pages/person_all.html"
res = requests.get(url)

# ★ 自動判定されたエンコーディングを使用（安全）
res.encoding = res.apparent_encoding
print("検出された文字コード:", res.encoding)

html = res.text
soup = BeautifulSoup(html, "html.parser")

authors = [a.text.strip() for a in soup.select("ol > li > a")]
print("取得した作家数:", len(authors))
print("先頭5人:", authors[:5])
