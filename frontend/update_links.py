import os
import re

frontend_dir = "/Users/ipaktulane/Downloads/PROJECT/frontend"

for filename in os.listdir(frontend_dir):
    if not filename.endswith('.html'): continue
    filepath = os.path.join(frontend_dir, filename)
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    def replace_specific_links(match, new_href):
        a_tag = match.group(0)
        return a_tag.replace('href="#"', f'href="{new_href}"')

    content = re.sub(r'<a[^>]+href="#"[^>]*>\s*Keep shopping\s*</a>', lambda m: replace_specific_links(m, 'catalog.html'), content)
    content = re.sub(r'<a[^>]+href="#"[^>]*>\s*Detailed Guide\s*</a>', lambda m: replace_specific_links(m, 'care.html'), content)
    content = re.sub(r'<a[^>]+href="#"[^>]*>\s*Report New Issue\s*</a>', lambda m: replace_specific_links(m, 'contact.html'), content)
    content = re.sub(r'<a[^>]+href="#"[^>]*>\s*Plants\s*</a>', lambda m: replace_specific_links(m, 'catalog.html'), content)
    content = re.sub(r'<a[^>]+href="#"[^>]*>\s*Indoor Plants\s*</a>', lambda m: replace_specific_links(m, 'catalog.html'), content)
    content = re.sub(r'<a[^>]+href="#"[^>]*>\s*Privacy Policy\s*</a>', lambda m: replace_specific_links(m, 'contact.html'), content)
    content = re.sub(r'<a[^>]+href="#"[^>]*>\s*Terms of Service\s*</a>', lambda m: replace_specific_links(m, 'contact.html'), content)
    content = re.sub(r'<a[^>]+href="#"[^>]*>\s*Home\s*</a>', lambda m: replace_specific_links(m, 'index.html'), content)

    # Convert specific buttons to <a> links keeping the button class
    def button_to_a(match, href):
        button_content = match.group(1)
        # replace opening <button ... > with <a href="..." ... >
        button_tag = re.sub(r'^<button\b', f'<a href="{href}"', button_content)
        # remove closing </button> and replace with </a>
        button_tag = re.sub(r'</button>$', '</a>', button_tag)
        return button_tag

    # Replace <button ... ><span>Explore</span></button> or <button ...>Explore</button>
    content = re.sub(r'(<button[^>]*>.*?Explore.*?</button>)', lambda m: button_to_a(m, 'catalog.html'), content, flags=re.DOTALL | re.IGNORECASE)
    content = re.sub(r'(<button[^>]*>.*?Shop Now.*?</button>)', lambda m: button_to_a(m, 'catalog.html'), content, flags=re.DOTALL | re.IGNORECASE)
    content = re.sub(r'(<button[^>]*>.*?View Varieties.*?</button>)', lambda m: button_to_a(m, 'varieties.html'), content, flags=re.DOTALL | re.IGNORECASE)
    content = re.sub(r'(<button[^>]*>.*?Checkout.*?</button>)', lambda m: button_to_a(m, 'checkout.html'), content, flags=re.DOTALL | re.IGNORECASE)
    content = re.sub(r'(<button[^>]*>.*?Care Guide.*?</button>)', lambda m: button_to_a(m, 'care.html'), content, flags=re.DOTALL | re.IGNORECASE)

    # Make Dashboard sidebar links actually link to something (dashboard.html, problems.html...)
    if filename == 'dashboard.html':
        content = content.replace('<span>Profile</span>', '<span>Profile</span>') # Just to orient
        content = re.sub(r'<a.*?href="#".*?>\s*<span[^>]*>person</span>.*?</a>', lambda m: m.group(0).replace('href="#"', 'href="dashboard.html"'), content, flags=re.DOTALL)
        content = re.sub(r'<a.*?href="#".*?>\s*<span[^>]*>package_2</span>.*?</a>', lambda m: m.group(0).replace('href="#"', 'href="dashboard.html"'), content, flags=re.DOTALL)
        content = re.sub(r'<a.*?href="#".*?>\s*<span[^>]*>potted_plant</span>.*?</a>', lambda m: m.group(0).replace('href="#"', 'href="varieties.html"'), content, flags=re.DOTALL)
        content = re.sub(r'<a.*?href="#".*?>\s*<span[^>]*>settings</span>.*?</a>', lambda m: m.group(0).replace('href="#"', 'href="dashboard.html"'), content, flags=re.DOTALL)

    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)
        
print("Updated internal links and buttons.")
