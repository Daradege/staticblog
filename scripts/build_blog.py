import os
import markdown
from jinja2 import Environment, FileSystemLoader
from datetime import datetime
import shutil

POSTS_DIR = 'posts'
SITE_DIR = 'site'
TEMPLATES_DIR = 'templates'

os.makedirs(SITE_DIR, exist_ok=True)

env = Environment(loader=FileSystemLoader(TEMPLATES_DIR))

def generate_toc(md_content):
    """تولید جدول محتوا از عناوین"""
    toc = []
    for line in md_content.split('\n'):
        if line.startswith('## '):
            title = line[3:].strip()
            anchor = title.lower().replace(' ', '-')
            toc.append((2, title, anchor))
        elif line.startswith('### '):
            title = line[4:].strip()
            anchor = title.lower().replace(' ', '-')
            toc.append((3, title, anchor))
    return toc

def process_posts():
    """پردازش تمام پست‌ها و تولید HTML"""
    posts_metadata = []
    
    for filename in os.listdir(POSTS_DIR):
        if filename.endswith('.md'):
            with open(os.path.join(POSTS_DIR, filename), 'r', encoding='utf-8') as f:
                md_content = f.read()
            
            metadata = {}
            lines = md_content.split('\n')
            if lines[0].startswith('---'):
                end_meta = lines[1:].index('---') + 1
                meta_lines = lines[1:end_meta]
                for line in meta_lines:
                    if ':' in line:
                        key, value = line.split(':', 1)
                        metadata[key.strip()] = value.strip()
                md_content = '\n'.join(lines[end_meta+1:])
            
            metadata.setdefault('title', filename[:-3])
            metadata.setdefault('date', datetime.now().strftime('%Y-%m-%d'))
            metadata.setdefault('author', 'علی صفامنش')
            
            html_content = markdown.markdown(md_content, extensions=['tables', 'fenced_code', 'toc'])
            
            toc = generate_toc(md_content)
            
            post_template = env.get_template('post.html')
            post_html = post_template.render(
                title=metadata['title'],
                content=html_content,
                toc=toc,
                date=metadata['date'],
                author=metadata['author'],
                post_name=filename[:-3]
            )

            output_filename = os.path.join(SITE_DIR, f"{filename[:-3]}.html")
            with open(output_filename, 'w', encoding='utf-8') as f:
                f.write(post_html)
            
            posts_metadata.append({
                'title': metadata['title'],
                'filename': f"{filename[:-3]}.html",
                'date': metadata['date'],
                'excerpt': md_content[:200] + '...' if len(md_content) > 200 else md_content
            })
    
    posts_metadata.sort(key=lambda x: x['date'], reverse=True)
    index_template = env.get_template('base.html')
    index_html = index_template.render(posts=posts_metadata)
    
    with open(os.path.join(SITE_DIR, 'index.html'), 'w', encoding='utf-8') as f:
        f.write(index_html)

if __name__ == '__main__':
    process_posts()