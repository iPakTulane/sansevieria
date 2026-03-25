import requests

plants = [
    ("Zeylanica / Trifasciata", "Dracaena_trifasciata"),
    ("Cylindrica", "Dracaena_angolensis"),
    ("Masoniana", "Dracaena_masoniana"),
    ("Ehrenbergii", "Dracaena_ehrenbergii"),
    ("Fernwood", "Dracaena_hyacinthoides"), # closest match or generic
    ("Bird's nest", "Dracaena_trifasciata")
]

for name, title in plants:
    url = f"https://en.wikipedia.org/w/api.php?action=query&titles={title}&prop=pageimages&format=json&pithumbsize=800"
    r = requests.get(url).json()
    pages = r['query']['pages']
    for page_id in pages:
        if 'thumbnail' in pages[page_id]:
            print(f"{name}: {pages[page_id]['thumbnail']['source']}")

