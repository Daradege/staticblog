import os

USERNAME = "Daradege"
REPO = "staticblog"

POSTS_DIR = "posts"
OUTPUT_FILE = "site/index.html"

def generate_post_list():
    posts = sorted(os.listdir(POSTS_DIR))
    html_items = ""
    for post in posts:
        if post.endswith(".md"):
            title = post.replace(".md", "")
            url = f"https://raw.githubusercontent.com/{USERNAME}/{REPO}/main/{POSTS_DIR}/{post}"
            html_items += f'<li><a href="{url}" target="_blank">{title}</a></li>\n'

    html_content = f"""<!DOCTYPE html>
<html lang="fa">
<head>
    <meta charset="UTF-8">
    <title>وبلاگ من</title>
    <style>
        body {{ font-family: sans-serif; direction: rtl; text-align: right; padding: 2em; background: #fdfdfd; }}
        h1 {{ color: #333; }}
        a {{ text-decoration: none; color: #007acc; }}
        a:hover {{ text-decoration: underline; }}
    </style>
</head>
<body>
    <h1>📚 پست‌های من</h1>
    <ul>
        {html_items}
    </ul>
    <p style="margin-top:2em;color:#888;">ساخته‌شده خودکار با GitHub Actions</p>
</body>
</html>
"""
    os.makedirs("site", exist_ok=True)
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        f.write(html_content)

if __name__ == "__main__":
    generate_post_list()
