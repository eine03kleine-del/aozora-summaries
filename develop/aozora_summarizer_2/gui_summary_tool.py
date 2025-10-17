import os
import tkinter as tk
from tkinter import filedialog, messagebox, scrolledtext

# HTMLテンプレート
HTML_TEMPLATE = """<!DOCTYPE html>
<html lang="ja">
<head>
    <meta charset="UTF-8">
    <title>{title}（{author}） - 要約</title>
</head>
<body>
    <h1>{title}（{author}）</h1>
    <h2>要約</h2>
    <p>{summary}</p>
    <h2>原文抜粋</h2>
    <pre>{snippet}</pre>
</body>
</html>
"""

def load_text_file():
    filepath = filedialog.askopenfilename(initialdir="texts", filetypes=[("Text files", "*.txt")])
    if not filepath:
        return

    filename = os.path.basename(filepath)
    if "_" not in filename:
        messagebox.showerror("エラー", "ファイル名は「タイトル_著者.txt」の形式にしてください。")
        return

    title, author = filename[:-4].split("_", 1)

    with open(filepath, "r", encoding="utf-8") as f:
        content = f.read()

    snippet = content[:500]

    title_var.set(title)
    author_var.set(author)
    snippet_text.delete(1.0, tk.END)
    snippet_text.insert(tk.END, snippet)

    current_file_path.set(filepath)


def save_html():
    title = title_var.get()
    author = author_var.get()
    summary = summary_text.get(1.0, tk.END).strip()
    snippet = snippet_text.get(1.0, tk.END).strip()

    if not summary:
        messagebox.showwarning("警告", "要約が空です。")
        return

    html = HTML_TEMPLATE.format(
        title=title,
        author=author,
        summary=summary,
        snippet=snippet
    )

    output_dir = "output"
    os.makedirs(output_dir, exist_ok=True)
    output_path = os.path.join(output_dir, f"{title}_{author}.html")

    with open(output_path, "w", encoding="utf-8") as f:
        f.write(html)

    messagebox.showinfo("保存完了", f"HTMLファイルを保存しました：\n{output_path}")


# GUIアプリの構築
app = tk.Tk()
app.title("青空文庫 要約HTML生成ツール")
app.geometry("800x600")

title_var = tk.StringVar()
author_var = tk.StringVar()
current_file_path = tk.StringVar()

tk.Button(app, text="📂 テキストファイルを読み込む", command=load_text_file).pack(pady=10)

tk.Label(app, text="タイトル").pack()
tk.Entry(app, textvariable=title_var, width=50).pack()

tk.Label(app, text="著者").pack()
tk.Entry(app, textvariable=author_var, width=50).pack()

tk.Label(app, text="✅ 要約を入力（ChatGPTなどで生成した文を貼り付け）").pack()
summary_text = scrolledtext.ScrolledText(app, height=10)
summary_text.pack(fill="both", expand=True)

tk.Label(app, text="📖 原文抜粋（自動で冒頭500文字）").pack()
snippet_text = scrolledtext.ScrolledText(app, height=10, state="normal")
snippet_text.pack(fill="both", expand=True)

tk.Button(app, text="💾 HTMLとして保存", command=save_html, bg="#4CAF50", fg="white").pack(pady=10)

app.mainloop()
