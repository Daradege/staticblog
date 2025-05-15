#!/usr/bin/env python3
import os
import re
import markdown
import frontmatter
import shutil
import yaml
from datetime import datetime
from pathlib import Path
from bs4 import BeautifulSoup

# Constants
POSTS_DIR = "posts"
SITE_DIR = "site"
TEMPLATES_DIR = "templates"
ASSETS_DIR = "assets"

# Create necessary directories
os.makedirs(SITE_DIR, exist_ok=True)

# Copy assets to site directory if not already present
if os.path.exists(ASSETS_DIR):
    site_assets_dir = os.path.join(SITE_DIR, "assets")
    os.makedirs(site_assets_dir, exist_ok=True)
    for item in os.listdir(ASSETS_DIR):
        source = os.path.join(ASSETS_DIR, item)
        destination = os.path.join(site_assets_dir, item)
        if os.path.isdir(source):
            shutil.copytree(source, destination, dirs_exist_ok=True)
        else:
            shutil.copy2(source, destination)

# Load template files
def load_template(filename):
    with open(os.path.join(TEMPLATES_DIR, filename), 'r', encoding='utf-8') as file:
        return file.read()

try:
    base_template = load_template("base.html")
    post_template = load_template("post.html")
    index_template = load_template("index.html")
except FileNotFoundError:
    print("Creating template files as they don't exist...")
    os.makedirs(TEMPLATES_DIR, exist_ok=True)
    
    # Define base template
    base_template = """<!DOCTYPE html>
<html lang="fa" dir="rtl">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{{ title }}</title>
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/tailwindcss/2.2.19/tailwind.min.css">
    <link rel="stylesheet" href="https://cdn.jsdelivr.net/gh/rastikerdar/vazir-font@v30.1.0/dist/font-face.css">
    <style>
        body {
            font-family: 'Vazir', sans-serif;
        }
        .blog-content h1 {
            @apply text-3xl font-bold mt-8 mb-4;
        }
        .blog-content h2 {
            @apply text-2xl font-bold mt-6 mb-3;
        }
        .blog-content h3 {
            @apply text-xl font-bold mt-5 mb-2;
        }
        .blog-content p {
            @apply my-4 leading-relaxed;
        }
        .blog-content ul {
            @apply list-disc list-inside my-4 ml-4;
        }
        .blog-content ol {
            @apply list-decimal list-inside my-4 ml-4;
        }
        .blog-content blockquote {
            @apply border-r-4 border-gray-500 pl-4 italic my-4;
        }
        .blog-content code {
            @apply bg-gray-100 px-1 py-0.5 rounded text-sm;
        }
        .blog-content pre {
            @apply bg-gray-800 text-white p-4 rounded-lg overflow-x-auto my-4;
        }
        .blog-content a {
            @apply text-blue-600 hover:text-blue-800 underline;
        }
        .blog-content img {
            @apply max-w-full h-auto my-4 rounded-lg shadow-md;
        }
        .toc {
            @apply bg-gray-50 p-4 rounded-lg mb-6 sticky top-4;
        }
        .toc ul {
            @apply list-none;
        }
        .toc li {
            @apply my-1;
        }
        .toc a {
            @apply text-gray-700 hover:text-blue-600 no-underline transition-colors;
        }
        @media print {
            .toc {
                display: none;
            }
        }
    </style>
    {{ extra_head }}
</head>
<body class="bg-gray-100 min-h-screen">
    <header class="bg-gradient-to-r from-purple-700 to-indigo-800 text-white shadow-lg">
        <div class="container mx-auto px-4 py-6">
            <div class="flex flex-col md:flex-row justify-between items-center">
                <a href="/index.html" class="text-2xl font-bold hover:text-purple-200 transition-colors">وبلاگ من</a>
                <nav class="mt-4 md:mt-0">
                    <ul class="flex space-x-6 space-x-reverse">
                        <li><a href="/index.html" class="hover:text-purple-200 transition-colors">صفحه اصلی</a></li>
                        <li><a href="/archives.html" class="hover:text-purple-200 transition-colors">آرشیو</a></li>
                        <li><a href="/about.html" class="hover:text-purple-200 transition-colors">درباره من</a></li>
                    </ul>
                </nav>
            </div>
        </div>
    </header>

    <main class="container mx-auto px-4 py-8">
        {{ content }}
    </main>

    <footer class="bg-gray-800 text-white py-8">
        <div class="container mx-auto px-4">
            <div class="flex flex-col md:flex-row justify-between items-center">
                <div class="mb-4 md:mb-0">
                    <p>&copy; {{ current_year }} وبلاگ من. تمامی حقوق محفوظ است.</p>
                </div>
                <div class="flex space-x-4 space-x-reverse">
                    <a href="#" class="text-gray-300 hover:text-white transition-colors">
                        <span class="sr-only">GitHub</span>
                        <svg class="h-6 w-6" fill="currentColor" viewBox="0 0 24 24" aria-hidden="true">
                            <path fill-rule="evenodd" d="M12 2C6.477 2 2 6.484 2 12.017c0 4.425 2.865 8.18 6.839 9.504.5.092.682-.217.682-.483 0-.237-.008-.868-.013-1.703-2.782.605-3.369-1.343-3.369-1.343-.454-1.158-1.11-1.466-1.11-1.466-.908-.62.069-.608.069-.608 1.003.07 1.531 1.032 1.531 1.032.892 1.53 2.341 1.088 2.91.832.092-.647.35-1.088.636-1.338-2.22-.253-4.555-1.113-4.555-4.951 0-1.093.39-1.988 1.029-2.688-.103-.253-.446-1.272.098-2.65 0 0 .84-.27 2.75 1.026A9.564 9.564 0 0112 6.844c.85.004 1.705.115 2.504.337 1.909-1.296 2.747-1.027 2.747-1.027.546 1.379.202 2.398.1 2.651.64.7 1.028 1.595 1.028 2.688 0 3.848-2.339 4.695-4.566 4.943.359.309.678.92.678 1.855 0 1.338-.012 2.419-.012 2.747 0 .268.18.58.688.482A10.019 10.019 0 0022 12.017C22 6.484 17.522 2 12 2z" clip-rule="evenodd"></path>
                        </svg>
                    </a>
                    <a href="#" class="text-gray-300 hover:text-white transition-colors">
                        <span class="sr-only">Twitter</span>
                        <svg class="h-6 w-6" fill="currentColor" viewBox="0 0 24 24" aria-hidden="true">
                            <path d="M8.29 20.251c7.547 0 11.675-6.253 11.675-11.675 0-.178 0-.355-.012-.53A8.348 8.348 0 0022 5.92a8.19 8.19 0 01-2.357.646 4.118 4.118 0 001.804-2.27 8.224 8.224 0 01-2.605.996 4.107 4.107 0 00-6.993 3.743 11.65 11.65 0 01-8.457-4.287 4.106 4.106 0 001.27 5.477A4.072 4.072 0 012.8 9.713v.052a4.105 4.105 0 003.292 4.022 4.095 4.095 0 01-1.853.07 4.108 4.108 0 003.834 2.85A8.233 8.233 0 012 18.407a11.616 11.616 0 006.29 1.84"></path>
                        </svg>
                    </a>
                </div>
            </div>
        </div>
    </footer>
</body>
</html>
"""
    
    # Define post template
    post_template = """<div class="flex flex-col lg:flex-row">
    <!-- TableOfContents -->
    <div class="w-full lg:w-1/4 lg:pr-8">
        <div class="toc">
            <h3 class="text-lg font-bold mb-3">فهرست مطالب</h3>
            {{ toc }}
        </div>
    </div>
    
    <!-- Post Content -->
    <div class="w-full lg:w-3/4">
        <article class="bg-white rounded-lg shadow-lg overflow-hidden">
            <!-- Hero Image if available -->
            {% if hero_image %}
            <div class="relative h-64 md:h-80 overflow-hidden">
                <img src="{{ hero_image }}" alt="{{ title }}" class="w-full h-full object-cover">
            </div>
            {% endif %}
            
            <div class="p-6 md:p-8">
                <h1 class="text-3xl lg:text-4xl font-bold mb-2">{{ title }}</h1>
                
                <div class="flex items-center text-sm text-gray-600 mt-2 mb-6">
                    <span class="mr-4">{{ date }}</span>
                    {% if author %}
                    <span class="mr-4">نویسنده: {{ author }}</span>
                    {% endif %}
                    {% if tags %}
                    <div class="flex flex-wrap">
                        {% for tag in tags %}
                        <span class="inline-block bg-gray-200 rounded-full px-3 py-1 text-xs font-semibold text-gray-700 mr-2 mb-2">#{{ tag }}</span>
                        {% endfor %}
                    </div>
                    {% endif %}
                </div>
                
                <div class="blog-content">
                    {{ content }}
                </div>
            </div>
        </article>
        
        <!-- Author Bio if available -->
        {% if author_bio %}
        <div class="bg-white rounded-lg shadow-lg overflow-hidden mt-8 p-6">
            <h3 class="text-xl font-bold mb-4">درباره نویسنده</h3>
            <div class="flex items-center">
                {% if author_image %}
                <img src="{{ author_image }}" alt="{{ author }}" class="w-16 h-16 rounded-full object-cover mr-4">
                {% endif %}
                <div>
                    <h4 class="font-bold">{{ author }}</h4>
                    <p class="text-gray-700">{{ author_bio }}</p>
                </div>
            </div>
        </div>
        {% endif %}
    </div>
</div>
"""
    
    # Define index template
    index_template = """<div class="mb-12">
    <h1 class="text-4xl font-bold mb-6 text-center">به وبلاگ من خوش آمدید</h1>
    <p class="text-lg text-center text-gray-700 max-w-3xl mx-auto">اینجا مطالب جذاب و آموزنده‌ای در مورد تکنولوژی، برنامه‌نویسی و مطالب مورد علاقه‌ام می‌نویسم.</p>
</div>

<div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
    {{ post_cards }}
</div>
"""
    
    # Save template files
    with open(os.path.join(TEMPLATES_DIR, "base.html"), 'w', encoding='utf-8') as file:
        file.write(base_template)
    
    with open(os.path.join(TEMPLATES_DIR, "post.html"), 'w', encoding='utf-8') as file:
        file.write(post_template)
        
    with open(os.path.join(TEMPLATES_DIR, "index.html"), 'w', encoding='utf-8') as file:
        file.write(index_template)

# Create extensions for markdown
md = markdown.Markdown(extensions=['meta', 'toc', 'codehilite', 'fenced_code', 'tables'])

# Collect all posts
posts = []
for filename in os.listdir(POSTS_DIR):
    if filename.endswith('.md'):
        post_id = filename[:-3]  # Remove .md extension
        with open(os.path.join(POSTS_DIR, filename), 'r', encoding='utf-8') as file:
            post = frontmatter.load(file)
            
            # Set defaults for missing frontmatter
            if 'title' not in post:
                post['title'] = post_id.replace('-', ' ').title()
            if 'date' not in post:
                post['date'] = datetime.now().strftime('%Y-%m-%d')
            if 'tags' not in post:
                post['tags'] = []
                
            post['id'] = post_id
            post['filename'] = filename
            posts.append(post)

# Sort posts by date (newest first)
posts.sort(key=lambda x: x.get('date', ''), reverse=True)

# Generate HTML for each post
for post in posts:
    # Convert markdown to HTML
    md.reset()
    html_content = md.convert(post.content)
    
    # Generate table of contents
    toc = md.toc
    
    # Replace placeholders in the post template
    post_html = post_template
    post_html = post_html.replace('{{ title }}', post['title'])
    post_html = post_html.replace('{{ date }}', post['date'])
    post_html = post_html.replace('{{ content }}', html_content)
    post_html = post_html.replace('{{ toc }}', toc)
    
    # Handle optional fields
    post_html = post_html.replace('{{ author }}', post.get('author', ''))
    post_html = post_html.replace('{{ author_bio }}', post.get('author_bio', ''))
    post_html = post_html.replace('{{ author_image }}', post.get('author_image', ''))
    
    # Handle hero image
    if 'hero_image' in post:
        post_html = post_html.replace('{% if hero_image %}', '')
        post_html = post_html.replace('{% endif %}', '')
        post_html = post_html.replace('{{ hero_image }}', post['hero_image'])
    else:
        hero_pattern = re.compile(r'{% if hero_image %}.*?{% endif %}', re.DOTALL)
        post_html = hero_pattern.sub('', post_html)
    
    # Handle tags
    if post.get('tags'):
        post_html = post_html.replace('{% if tags %}', '')
        post_html = post_html.replace('{% endif %}', '')
        tags_html = ''
        for tag in post['tags']:
            tag_html = '<span class="inline-block bg-gray-200 rounded-full px-3 py-1 text-xs font-semibold text-gray-700 mr-2 mb-2">#' + tag + '</span>'
            tags_html += tag_html
        post_html = post_html.replace('{% for tag in tags %}' + 
                                     '<span class="inline-block bg-gray-200 rounded-full px-3 py-1 text-xs font-semibold text-gray-700 mr-2 mb-2">#{{ tag }}</span>' + 
                                     '{% endfor %}', tags_html)
    else:
        tags_pattern = re.compile(r'{% if tags %}.*?{% endif %}', re.DOTALL)
        post_html = tags_pattern.sub('', post_html)
    
    # Handle author bio
    if post.get('author_bio'):
        post_html = post_html.replace('{% if author_bio %}', '')
        post_html = post_html.replace('{% endif %}', '')
        if post.get('author_image'):
            post_html = post_html.replace('{% if author_image %}', '')
            post_html = post_html.replace('{% endif %}', '')
        else:
            author_image_pattern = re.compile(r'{% if author_image %}.*?{% endif %}', re.DOTALL)
            post_html = author_image_pattern.sub('', post_html)
    else:
        author_bio_pattern = re.compile(r'{% if author_bio %}.*?{% endif %}', re.DOTALL)
        post_html = author_bio_pattern.sub('', post_html)
    
    # Insert into base template
    page_html = base_template
    page_html = page_html.replace('{{ title }}', post['title'])
    page_html = page_html.replace('{{ content }}', post_html)
    page_html = page_html.replace('{{ current_year }}', str(datetime.now().year))
    page_html = page_html.replace('{{ extra_head }}', post.get('extra_head', ''))
    
    # Write HTML file
    output_file = os.path.join(SITE_DIR, f"{post['id']}.html")
    with open(output_file, 'w', encoding='utf-8') as file:
        file.write(page_html)
    
    print(f"Generated {output_file}")

# Generate index page with post cards
post_cards_html = ""
for post in posts:
    card = f"""
    <a href="{post['id']}.html" class="block hover:shadow-xl transition-shadow duration-300">
        <div class="bg-white rounded-lg shadow-md overflow-hidden h-full">
            {'<img src="' + post.get('hero_image', '') + '" alt="' + post['title'] + '" class="w-full h-48 object-cover">' if post.get('hero_image') else ''}
            <div class="p-6">
                <h2 class="text-xl font-bold mb-2">{post['title']}</h2>
                <div class="text-sm text-gray-600 mb-3">{post['date']}</div>
                <p class="text-gray-700 mb-4">{post.get('summary', '')[:150] + ('...' if len(post.get('summary', '')) > 150 else '')}</p>
                <div class="flex flex-wrap">
                    {"".join(['<span class="inline-block bg-gray-200 rounded-full px-3 py-1 text-xs font-semibold text-gray-700 mr-2 mb-2">#' + tag + '</span>' for tag in post.get('tags', [])])}
                </div>
                <div class="mt-4 text-blue-600 hover:text-blue-800">ادامه مطلب &larr;</div>
            </div>
        </div>
    </a>
    """
    post_cards_html += card

# Create index.html
index_html = index_template.replace('{{ post_cards }}', post_cards_html)
page_html = base_template
page_html = page_html.replace('{{ title }}', 'وبلاگ من')
page_html = page_html.replace('{{ content }}', index_html)
page_html = page_html.replace('{{ current_year }}', str(datetime.now().year))
page_html = page_html.replace('{{ extra_head }}', '')

with open(os.path.join(SITE_DIR, "index.html"), 'w', encoding='utf-8') as file:
    file.write(page_html)

print(f"Generated index.html")

# Create about.html if it doesn't exist
about_file = os.path.join(SITE_DIR, "about.html")
if not os.path.exists(about_file):
    about_content = """
    <div class="bg-white rounded-lg shadow-lg p-8 max-w-3xl mx-auto">
        <h1 class="text-3xl font-bold mb-6">درباره من</h1>
        <p class="mb-4">سلام! به صفحه درباره من خوش آمدید. من یک برنامه‌نویس و علاقه‌مند به تکنولوژی هستم.</p>
        <p class="mb-4">این وبلاگ محلی برای به اشتراک‌گذاری دانش، تجربیات و افکار من است.</p>
        <p>برای تماس با من می‌توانید از طریق شبکه‌های اجتماعی در پایین صفحه اقدام کنید.</p>
    </div>
    """
    
    page_html = base_template
    page_html = page_html.replace('{{ title }}', 'درباره من')
    page_html = page_html.replace('{{ content }}', about_content)
    page_html = page_html.replace('{{ current_year }}', str(datetime.now().year))
    page_html = page_html.replace('{{ extra_head }}', '')
    
    with open(about_file, 'w', encoding='utf-8') as file:
        file.write(page_html)
    
    print(f"Generated {about_file}")

# Create archives.html
archive_content = """
<div class="bg-white rounded-lg shadow-lg p-8">
    <h1 class="text-3xl font-bold mb-6">آرشیو مطالب</h1>
    
    <div class="space-y-12">
"""

# Group posts by year and month
posts_by_year_month = {}
for post in posts:
    date_str = post.get('date', '')
    try:
        post_date = datetime.strptime(date_str, '%Y-%m-%d')
        year = post_date.year
        month = post_date.month
        
        if year not in posts_by_year_month:
            posts_by_year_month[year] = {}
        
        if month not in posts_by_year_month[year]:
            posts_by_year_month[year][month] = []
            
        posts_by_year_month[year][month].append(post)
    except ValueError:
        print(f"Warning: Invalid date format in post {post['id']}")

# Generate HTML for archive
for year in sorted(posts_by_year_month.keys(), reverse=True):
    archive_content += f'<div class="mb-8"><h2 class="text-2xl font-bold mb-4">{year}</h2>'
    
    for month in sorted(posts_by_year_month[year].keys(), reverse=True):
        month_names = [
            "فروردین", "اردیبهشت", "خرداد", "تیر", "مرداد", "شهریور", 
            "مهر", "آبان", "آذر", "دی", "بهمن", "اسفند"
        ]
        month_name = month_names[month-1]
        
        archive_content += f'<div class="mb-6"><h3 class="text-xl font-bold mb-3">{month_name}</h3><ul class="space-y-2">'
        
        for post in posts_by_year_month[year][month]:
            archive_content += f'<li class="flex justify-between items-center"><a href="{post["id"]}.html" class="text-blue-600 hover:text-blue-800">{post["title"]}</a><span class="text-gray-500 text-sm">{post["date"]}</span></li>'
        
        archive_content += '</ul></div>'
    
    archive_content += '</div>'

archive_content += """
    </div>
</div>
"""

page_html = base_template
page_html = page_html.replace('{{ title }}', 'آرشیو مطالب')
page_html = page_html.replace('{{ content }}', archive_content)
page_html = page_html.replace('{{ current_year }}', str(datetime.now().year))
page_html = page_html.replace('{{ extra_head }}', '')

with open(os.path.join(SITE_DIR, "archives.html"), 'w', encoding='utf-8') as file:
    file.write(page_html)

print(f"Generated archives.html")
print("Build completed successfully!")