# Sansevieria Web Application 🌿


Welcome to the Sansevieria frontend project! This is a static HTML/CSS web application dedicated to the cataloging, care, and commerce of Sansevieria (Snake Plants).

## Project Overview

The project consists of multiple statically defined HTML pages, styled with modern utility classes (Tailwind CSS format). It also includes custom Python utility scripts designed to perform bulk structural updates across the codebase, ensuring consistency across all pages.

### Key Pages
- `index.html` — The main landing/home page.
- `catalog.html` — The product catalog.
- `cart.html` & `checkout.html` — E-commerce shopping flow.
- `care.html`, `blog.html`, `problems.html`, `varieties.html` — Informational and guide pages.
- `dashboard.html`, `auth.html` — User profile and authentication views.

### Python Utility Scripts

To keep the static HTML files maintainable, several python scripts are provided in the `frontend/` directory:

- **`update_headers.py`**: Rewrites the `<header>` block in all `.html` files, ensuring that the top navigation bar is identical and updated everywhere.
- **`update_links.py`**: Uses Regular Expressions to traverse the HTML files and update placeholder hrefs (`href="#"`) and `<button>` elements to properly mapped internal semantic links.
- **`update_fonts.py`** & **`fix_links.py`**: Additional batch-processing utilities for styling and link structures.

## Usage

### Viewing the Site
You can open any `.html` file directly in your browser, or spin up a local development server for a better experience:

```bash
cd frontend
python3 -m http.server 8000
```
Then visit `http://localhost:8000/index.html` or just `http://localhost:8000/`.

### Running Updates
If you decide to change the global header structure, edit the raw HTML block located inside `frontend/update_headers.py` and execute the script:

```bash
python3 frontend/update_headers.py
```

To automatically link up new placeholder buttons or correct routing changes across the site:

```bash
python3 frontend/update_links.py
```
