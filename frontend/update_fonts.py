import os
import re

frontend_dir = "/Users/ipaktulane/Downloads/PROJECT/frontend"

for filename in os.listdir(frontend_dir):
    if not filename.endswith('.html'): continue
    filepath = os.path.join(frontend_dir, filename)
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    # Remove the Google Font link for Inter
    content = re.sub(r'<link[^>]*family=Inter[^>]*>\s*', '', content)

    # Change fontFamily in tailwind config
    content = re.sub(r'"display":\s*\["Inter"[^\]]*\]', '"display": ["Arial", "sans-serif"]', content)
    content = re.sub(r'"display":\s*\[''Inter''[^\]]*\]', '"display": ["Arial", "sans-serif"]', content)

    # Change font-family in CSS blocks
    content = re.sub(r"font-family:\s*['\"]Inter['\"][^;]*;", 'font-family: Arial, sans-serif;', content)
    
    # Just in case there are direct inline styles or other mentions
    content = content.replace("'Inter'", "'Arial'")
    content = content.replace('"Inter"', '"Arial"')

    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)

print("Updated fonts to Arial in all HTML files.")
