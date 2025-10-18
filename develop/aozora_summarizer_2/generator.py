import os
import requests
from bs4 import BeautifulSoup
from transformers import pipeline
from tqdm import tqdm

# === ディレクトリ準備 ===
os.makedirs("summaries", exist_ok=True)
os.makedirs("data/texts", exist_ok=True)

# === 要約モデルの初期化（Hugging Face） ===
summarizer = pipeline("summarization", model="facebook/bart-large-cnn")

def get_works_list():
    """夏目漱石など人気作家から100作品取得"""
    author_urls = [
        "https://www.aozora.gr.jp/index_pages/person148.html",  # 夏目漱石
        "https://www.aozora.gr.jp/index_pages/person35.html",   # 芥川龍之介
        "https://www.aozora.gr.jp/index_pages/person879.html",  # 太宰治
    ]
    works = []
    for url in author_urls:
        html = requests.get(url).text
        soup = BeautifulSoup(html, "html.parser")
        for li in soup.select("ol li a[href*='cards/']"):
            title = li.text.strip()
            href = li["href"]
            full_url = "https://www.aozora.gr.jp/" + href
            works.append((title, full_url))
            if len(works) >= 100:
                return works
    return works

def get_text_url(work_url):
    """作品ページからテキストファイルURLを取得"""
    html = requests.get(work_url).text
    soup = BeautifulSoup(html, "html.parser")
    link = soup.find("a", href=lambda x: x and x.endswith(".txt"))
    if link:
        return "https://www.aozora.gr.jp" + link["href"]
    return None

def summarize_text(text):
    """長文を分割して要約"""
    chunks = [text[i:i+3000] for i in range(0, len(text), 3000)]
    summaries = []
    for chunk in chunks:
        try:
            summary = summarizer(chunk, max_length=200, min_length=100, do_sample=False)[0]["summary_text"]
            summaries.append(summary)
        except Exception:
            continue
    return " ".join(summaries)

def generate_html(title, summary, source_url, filename):
    html = f"""<!DOCTYPE html>
<html lang="ja">
<head>
  <meta charset="UTF-8">
  <title>{title} - 要約</title>
</head>
<body>
  <h1>{title}</h1>
  <h2>要約</h2>
  <p>{summary}</p>
  <h2>原文リンク</h2>
  <a href="{source_url}" target="_blank">青空文庫で読む</a>
</body>
</html>"""
    with open(f"summaries/{filename}.html", "w", encoding="utf-8") as f:
        f.write(html)

def update_index(works):
    links = "\n".join(
        [f'<li><a href="summaries/{slug}.html">{title}</a></li>' for slug, title in works]
    )
    index = f"""<!DOCTYPE html>
<html lang="ja">
<head>
  <meta charset="UTF-8">
  <title>青空文庫 要約サイト</title>
</head>
<body>
  <h1>青空文庫 要約まとめ</h1>
  <ul>
    {links}
  </ul>
  <footer>
    本サイトの要約はAIによって生成されたものであり、出典は
    <a href="https://www.aozora.gr.jp/" target="_blank" rel="noopener noreferrer">
      青空文庫
    </a>
    です。
  </footer>
</body>
</html>"""
    with open("index.html", "w", encoding="utf-8") as f:
        f.write(index)

def main():
    works_list = get_works_list()
    generated = []

    for title, url in tqdm(works_list, desc="Processing works"):
        slug = title.replace(" ", "_").replace("　", "_").replace("/", "_")
        txt_url = get_text_url(url)
        if not txt_url:
            continue

        txt_path = f"data/texts/{slug}.txt"
        if not os.path.exists(txt_path):
            txt = requests.get(txt_url).content.decode("shift_jis", errors="ignore")
            open(txt_path, "w", encoding="utf-8").write(txt)

        text = open(txt_path, encoding="utf-8").read()
        summary = summarize_text(text[:8000]) or "要約の生成に失敗しました。"
        generate_html(title, summary, url, slug)
        generated.append((slug, title))

    update_index(generated)
    print(f"✅ {len(generated)}作品を生成しました。")

if __name__ == "__main__":
    main()
