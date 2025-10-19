import os
import requests
from bs4 import BeautifulSoup
from tqdm import tqdm
from transformers import pipeline

# ==========================================
# 設定
# ==========================================
BASE_URL = "https://www.aozora.gr.jp/"
SAVE_DIR = "summaries"
os.makedirs(SAVE_DIR, exist_ok=True)

# 要約モデル（日本語対応・軽量）
summarizer = pipeline("summarization", model="facebook/bart-large-cnn")

# ==========================================
# 関数群
# ==========================================

def get_author_list():
    """青空文庫の作家一覧を取得"""
    url = BASE_URL + "index_pages/person_all.html"
    res = requests.get(url)
    res.encoding = "shift_jis"
    soup = BeautifulSoup(res.text, "html.parser")

    authors = []
    for link in soup.select("ol > li > a"):
        name = link.text.strip()
        href = link.get("href")
        if href and "person" in href:
            authors.append((name, BASE_URL + href))
    return authors


def get_works_from_author(author_url):
    """作家ページから作品一覧を取得"""
    res = requests.get(author_url)
    res.encoding = "shift_jis"
    soup = BeautifulSoup(res.text, "html.parser")

    works = []
    for a in soup.select("ol > li > a"):
        title = a.text.strip()
        href = a.get("href")
        if href and "cards" in href:
            works.append((title, BASE_URL + href))
    return works


def extract_text_from_work(work_url):
    """作品ページから本文テキストを抽出"""
    res = requests.get(work_url)
    res.encoding = "shift_jis"
    soup = BeautifulSoup(res.text, "html.parser")

    link = soup.find("a", string="テキストファイル")
    if not link:
        return None

    txt_url = BASE_URL + link.get("href")
    txt_res = requests.get(txt_url)
    txt_res.encoding = "shift_jis"
    return txt_res.text


def summarize_text(text):
    """本文を要約"""
    text = text.replace("\r", "").replace("\n", "")
    if len(text) > 3000:
        text = text[:3000]  # 長すぎるテキストを切り詰め
    summary = summarizer(text, max_length=150, min_length=50, do_sample=False)
    return summary[0]["summary_text"]


def save_summary(author, title, summary):
    """要約をHTML形式で保存"""
    safe_author = author.replace(" ", "_")
    safe_title = title.replace(" ", "_")
    author_dir = os.path.join(SAVE_DIR, safe_author)
    os.makedirs(author_dir, exist_ok=True)

    file_path = os.path.join(author_dir, f"{safe_title}.html")
    with open(file_path, "w", encoding="utf-8") as f:
        f.write(f"<h1>{title}</h1>\n<p>{summary}</p>")

    return file_path


# ==========================================
# メイン処理
# ==========================================

def main():
    print("🟦 青空文庫の作家一覧を取得中...")
    authors = get_author_list()[:5]  # テスト的に上位5作家まで（調整可）

    index_entries = []

    for author, author_url in tqdm(authors, desc="Processing authors"):
        works = get_works_from_author(author_url)[:5]  # 各作家5作品まで
        author_page = os.path.join(SAVE_DIR, author.replace(" ", "_") + ".html")

        author_entries = []
        for title, work_url in works:
            try:
                text = extract_text_from_work(work_url)
                if not text:
                    continue
                summary = summarize_text(text)
                path = save_summary(author, title, summary)
                rel_path = os.path.relpath(path, SAVE_DIR)
                author_entries.append(f"<li><a href='{rel_path}'>{title}</a></li>")
            except Exception as e:
                print(f"⚠️ {title} の要約中にエラー: {e}")

        # 作家ページHTML生成
        with open(author_page, "w", encoding="utf-8") as f:
            f.write(f"<h1>{author}</h1>\n<ul>\n")
            f.write("\n".join(author_entries))
            f.write("\n</ul>")

        index_entries.append(f"<li><a href='{author.replace(' ', '_')}.html'>{author}</a></li>")

    # index.html作成
    with open("index.html", "w", encoding="utf-8") as f:
        f.write("<!DOCTYPE html><html lang='ja'><head><meta charset='UTF-8'><title>青空文庫 要約まとめ</title></head><body>")
        f.write("<h1>青空文庫 要約まとめ</h1>\n<ul>\n")
        f.write("\n".join(index_entries))
        f.write("\n</ul></body></html>")

    print("✅ すべて完了しました。index.html を確認してください。")


if __name__ == "__main__":
    main()
