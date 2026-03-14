import os
import re

frontend_dir = "/Users/ipaktulane/Downloads/PROJECT/frontend"

for filename in os.listdir(frontend_dir):
    if not filename.endswith('.html'): continue
    filepath = os.path.join(frontend_dir, filename)
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    # Fix cart.html Malformed tag
    if filename == 'cart.html':
        content = content.replace('<button class="w-full bg-primary hover:bg-primary/90 text-slate-900 font-bold py-4 rounded-xl shadow-lg shadow-primary/20 transition-all active:scale-[0.98] flex items-center justify-center gap-2">\n<span>Proceed to Checkout</span>\n<span class="material-symbols-outlined">arrow_forward</span>\n</a>',
                                  '<a href="checkout.html" class="w-full bg-primary hover:bg-primary/90 text-slate-900 font-bold py-4 rounded-xl shadow-lg shadow-primary/20 transition-all active:scale-[0.98] flex items-center justify-center gap-2">\n<span>Proceed to Checkout</span>\n<span class="material-symbols-outlined">arrow_forward</span>\n</a>')
        content = content.replace('href="#">\n<span class="material-symbols-outlined text-sm">arrow_back</span>\n                    Continue Shopping', 'href="catalog.html">\n<span class="material-symbols-outlined text-sm">arrow_back</span>\n                    Continue Shopping')
        
    if filename == 'auth.html':
        content = content.replace('href="#">Forgot?</a>', 'href="contact.html">Forgot?</a>')
        content = content.replace('href="#">Create Account</a>', 'href="auth.html">Create Account</a>')
        
    if filename == 'blog.html':
        content = content.replace('href="#">\n                        Read More', 'href="blog.html">\n                        Read More')
        content = content.replace('href="#">#IndoorGardening', 'href="blog.html">#IndoorGardening')
        content = content.replace('href="#">#SlowGrowth', 'href="blog.html">#SlowGrowth')
        content = content.replace('href="#">#AirPurifier', 'href="blog.html">#AirPurifier')

    if filename == 'product.html':
        # Replace empty href="#" for social links to leave them but maybe point to contact or leave as #
        pass
        
    if filename == 'contact.html':
        content = content.replace('href="#">Shipping Info', 'href="about.html">Shipping Info')

    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)

print("Fixed additional links.")
