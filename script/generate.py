import os
import markdown
from pathlib import Path
from slugify import slugify

POSTS_DIR = "posts"
SITE_DIR = "site"

HTML_TEMPLATE = """<!DOCTYPE html>
<html lang="fa">
<head>
  <meta charset="UTF-8">
  <title>{title}</title>
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <style>
    body {{ font-family: sans-serif; line-height: 1.8; max-width: 800px; margin: auto; padding: 2rem; background: #fdfdfd; direction: rtl; }}
    h1, h2, h3 {{ color: #333; }}
    a {{ color: #007acc; text-decoration: none; }}
    a:hover {{ text-decoration: underline; }}
    .toc {{ background: #f0f0f0; padding: 1em; margin-bottom: 2em; border-right: 4px solid #007acc; }}
    pre {{ background: #eee; padding: 1em; overflow-x: auto; }}
    code {{ background: #eee; padding: 0.2em 0.4em; border-radius: 4px; }}
  </style>
</head>
<body>
  <h1>{title}</h1>
  <div class="toc">
    <h2>📑 جدول محتوا</h2>
    {toc}
  </div>
  <article>
    {content}
  </article>
</body>
</html>
"""

def convert_post(filepath):
    with open(filepath, encoding="utf-8") as f:
        text = f.read()

    md = markdown.Markdown(extensions=["toc", "fenced_code", "codehilite"])
    html = md.convert(text)
    title = text.strip().splitlines()[0].replace("#", "").strip()
    toc = md.toc

    slug = slugify(title)
    output_path = Path(SITE_DIR) / slug / "index.html"
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with open(output_path, "w", encoding="utf-8") as f:
        f.write(HTML_TEMPLATE.format(title=title, content=html, toc=toc))

def main():
    Path(SITE_DIR).mkdir(exist_ok=True)
    Path(SITE_DIR, "index.html").write_text("<h1>وبلاگ</h1><p>لیست پست‌ها به‌زودی در صفحه اصلی می‌آید.</p>", encoding="utf-8")

    for mdfile in Path(POSTS_DIR).glob("*.md"):
        convert_post(mdfile)

if __name__ == "__main__":
    main()
