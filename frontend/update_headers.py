import os
import re
import sys

# Directory containing the html files
frontend_dir = "/Users/ipaktulane/Downloads/PROJECT/frontend"

header_html = """<header class="w-full shrink-0 border-b border-solid border-primary/10 px-6 lg:px-10 py-3 md:h-16 flex items-center justify-between bg-background-light/80 dark:bg-background-dark/80 backdrop-blur-md z-50">
    <!-- Logo / Brand -->
    <div class="flex items-center gap-3">
        <div class="size-6 text-primary flex items-center justify-center">
            <span class="material-symbols-outlined">eco</span>
        </div>
        <a href="index.html" class="text-slate-900 dark:text-slate-100 text-lg font-bold leading-tight tracking-[-0.015em] hover:text-primary transition-colors">Sansevieria</a>
    </div>
    
    <!-- Navigation Area -->
    <div class="flex flex-1 justify-end gap-6 items-center">
        <!-- Main Links -->
        <nav class="hidden lg:flex items-center gap-6">
            <a class="text-slate-700 dark:text-slate-300 text-sm font-medium hover:text-primary transition-colors" href="index.html">Home</a>
            <a class="text-slate-700 dark:text-slate-300 text-sm font-medium hover:text-primary transition-colors" href="catalog.html">Catalog</a>
            <a class="text-slate-700 dark:text-slate-300 text-sm font-medium hover:text-primary transition-colors" href="about.html">About</a>
            <a class="text-slate-700 dark:text-slate-300 text-sm font-medium hover:text-primary transition-colors" href="team.html">Team</a>
            <a class="text-slate-700 dark:text-slate-300 text-sm font-medium hover:text-primary transition-colors" href="contact.html">Contact</a>
            
            <div class="relative group cursor-pointer inline-block z-[100]">
                <span class="text-slate-700 dark:text-slate-300 text-sm font-medium hover:text-primary transition-colors flex items-center gap-1 py-4">More <span class="material-symbols-outlined text-[1rem]">expand_more</span></span>
                <div class="absolute right-0 top-full -mt-2 w-48 bg-white dark:bg-slate-800 rounded-lg shadow-xl border border-primary/10 opacity-0 invisible group-hover:opacity-100 group-hover:visible transition-all flex flex-col p-2 z-[100]">
                    <a href="varieties.html" class="px-3 py-2 text-sm text-slate-700 dark:text-slate-300 hover:bg-primary/5 hover:text-primary rounded-md transition-colors">Varieties</a>
                    <a href="care.html" class="px-3 py-2 text-sm text-slate-700 dark:text-slate-300 hover:bg-primary/5 hover:text-primary rounded-md transition-colors">Care</a>
                    <a href="problems.html" class="px-3 py-2 text-sm text-slate-700 dark:text-slate-300 hover:bg-primary/5 hover:text-primary rounded-md transition-colors">Problems</a>
                    <a href="blog.html" class="px-3 py-2 text-sm text-slate-700 dark:text-slate-300 hover:bg-primary/5 hover:text-primary rounded-md transition-colors">Blog</a>
                    <div class="h-px w-full bg-primary/10 my-1"></div>
                </div>
            </div>
        </nav>
        
        <!-- Action Buttons -->
        <div class="flex items-center gap-3">
             <a href="cart.html" class="flex items-center justify-center p-2 rounded-full hover:bg-primary/10 transition-colors" title="Cart">
                <span class="material-symbols-outlined text-slate-600 dark:text-slate-300">shopping_cart</span>
            </a>
            <a href="auth.html" class="flex items-center justify-center p-2 rounded-full hover:bg-primary/10 transition-colors" title="Auth/Login">
                <span class="material-symbols-outlined text-slate-600 dark:text-slate-300">login</span>
            </a>
            <a href="dashboard.html" class="flex flex-shrink-0 items-center justify-center p-2 rounded-full hover:bg-primary/10 transition-colors" title="Dashboard">
                <span class="material-symbols-outlined text-slate-600 dark:text-slate-300">account_circle</span>
            </a>
        </div>
    </div>
</header>"""

for filename in os.listdir(frontend_dir):
    if not filename.endswith('.html'):
        continue
    file_path = os.path.join(frontend_dir, filename)
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # Regex to find <header ...> ... </header>
    # Note: re.DOTALL is necessary to match across newlines
    new_content, count = re.subn(r'<header\b[^>]*>.*?</header>', header_html, content, flags=re.DOTALL)
    
    if count == 0:
        print(f"No <header> found in {filename}. Skipping.")
    else:
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(new_content)
        print(f"Updated header in {filename}.")
