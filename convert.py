import os
import markdown
from markdown.extensions.toc import TocExtension
from jinja2 import Environment, FileSystemLoader

env = Environment(loader=FileSystemLoader("template"))
base_template = env.get_template("base.html")
post_template = env.get_template("post.html")

os.makedirs("site", exist_ok=True)

posts = []

for filename in os.listdir("posts"):
    if filename.endswith(".md"):
        slug = os.path.splitext(filename)[0]
        with open(f"posts/{filename}", encoding="utf-8") as f:
            md_content = f.read()

        html = markdown.markdown(md_content, extensions=["extra", TocExtension(baselevel=2, title='Table of Contents')])
        toc = markdown.markdown("[TOC]", extensions=[TocExtension(baselevel=2)])
        
        post_html = post_template.render(title=slug, body=html, toc=toc)
        final_html = base_template.render(title=slug, content=post_html)

        with open(f"site/{slug}.html", "w", encoding="utf-8") as out:
            out.write(final_html)
        
        posts.append((slug, f"{slug}.html"))

# ساخت index.html
index_content = "<h1 class='text-3xl font-bold mb-4'>پست‌ها</h1><ul class='space-y-2'>"
for title, link in posts:
    index_content += f"<li><a class='text-blue-600 hover:underline' href='{link}'>{title}</a></li>"
index_content += "</ul>"

with open("site/index.html", "w", encoding="utf-8") as f:
    f.write(base_template.render(title="وبلاگ", content=index_content))
