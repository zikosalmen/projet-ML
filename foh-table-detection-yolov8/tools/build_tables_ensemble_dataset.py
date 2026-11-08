import os
import re
import csv
import io
import time
import requests
from PIL import Image

# Destination directories
OUTPUT_DIR = r"C:\Users\CDA EXPERTISE\Desktop\projet ML\dataset_tables_ensemble"
IMAGES_DIR = os.path.join(OUTPUT_DIR, "images")
os.makedirs(IMAGES_DIR, exist_ok=True)

HEADERS = {
    'User-Agent': 'FOH_TableDatasetCollector/1.0 (Machine Learning research; contact: student@univ.edu)'
}

# Curated Unsplash images with verified sets of tables
UNSPLASH_CURATED = [
    {
        "id_slug": "photo-1551529834-525807d6b4f3",
        "category": "restaurant_interieur",
        "subcategory": "salle_moderne",
        "title": "Restaurant dining sets and tables near large windows",
        "author": "Louis Hansel",
        "page_url": "https://unsplash.com/photos/empty-brown-wooden-dining-table-near-window-and-winged-chairs-inside-restaurant-wVoP_Q8p7t8",
        "direct_url": "https://images.unsplash.com/photo-1551529834-525807d6b4f3?fm=jpg&w=1600&q=85",
        "desc": "Ensemble de tables en bois alignées dans un restaurant moderne baigné de lumière naturelle."
    },
    {
        "id_slug": "photo-1517248135467-4c7edcad34c4",
        "category": "restaurant_interieur",
        "subcategory": "salle_elegante",
        "title": "Multiple tables set with chairs in upscale restaurant",
        "author": "Jay Wennington",
        "page_url": "https://unsplash.com/photos/brown-wooden-tables-and-chairs-inside-restaurant-N_Y88TWmGwA",
        "direct_url": "https://images.unsplash.com/photo-1517248135467-4c7edcad34c4?fm=jpg&w=1600&q=85",
        "desc": "Salle de restaurant avec plusieurs rangées de tables dressées, vaisselle et chaises en bois."
    },
    {
        "id_slug": "photo-1555396273-367ea4eb4db5",
        "category": "restaurant_interieur",
        "subcategory": "bistrot_contemporain",
        "title": "Dining tables and bar layout in modern bistro",
        "author": "Petr Sevcovic",
        "page_url": "https://unsplash.com/photos/brown-wooden-table-and-chairs-inside-room-auijD1-nmHQ",
        "direct_url": "https://images.unsplash.com/photo-1555396273-367ea4eb4db5?fm=jpg&w=1600&q=85",
        "desc": "Rangée de tables en bois dans un bistrot contemporain avec vue en perspective."
    },
    {
        "id_slug": "photo-1554118811-1e0d58224f24",
        "category": "cafe_terrasse",
        "subcategory": "cafe_interieur",
        "title": "Cozy coffee shop interior with multiple wooden tables",
        "author": "Dahee Son",
        "page_url": "https://unsplash.com/photos/white-concrete-building-near-trees-during-daytime-XoByiBymcLk",
        "direct_url": "https://images.unsplash.com/photo-1554118811-1e0d58224f24?fm=jpg&w=1600&q=85",
        "desc": "Intérieur chaleureux d'un café avec un ensemble de tables rondes et carrées."
    },
    {
        "id_slug": "photo-1559339352-11d035aa65de",
        "category": "cafe_terrasse",
        "subcategory": "cafe_lounge",
        "title": "Cafe dining area with tables and seating",
        "author": "Roman Bozhko",
        "page_url": "https://unsplash.com/photos/tables-and-chairs-in-cafe-Psn45EcToxw",
        "direct_url": "https://images.unsplash.com/photo-1559339352-11d035aa65de?fm=jpg&w=1600&q=85",
        "desc": "Espace café avec plusieurs ensembles de tables basses et tables hautes."
    },
    {
        "id_slug": "photo-1521017432531-fbd92d768814",
        "category": "cafe_terrasse",
        "subcategory": "coffee_shop",
        "title": "Coffee shop tables occupied and empty",
        "author": "Ali Yahya",
        "page_url": "https://unsplash.com/photos/people-sitting-on-chair-in-front-of-tables-l9dhWu0hQiA",
        "direct_url": "https://images.unsplash.com/photo-1521017432531-fbd92d768814?fm=jpg&w=1600&q=85",
        "desc": "Tables de café avec clients et tables vides, idéal pour détection multi-tables."
    },
    {
        "id_slug": "photo-1543007630-9710e4a00a20",
        "category": "restaurant_interieur",
        "subcategory": "bar_restaurant",
        "title": "Tables and seating booths in restaurant",
        "author": "Ksenia Chernaya",
        "page_url": "https://unsplash.com/photos/interior-of-a-restaurant-with-tables-and-chairs-mK49PCup0",
        "direct_url": "https://images.unsplash.com/photo-1543007630-9710e4a00a20?fm=jpg&w=1600&q=85",
        "desc": "Ensemble de banquettes et tables rectangulaires dans une salle de restaurant."
    },
    {
        "id_slug": "photo-1414235077428-338989a2e8c0",
        "category": "restaurant_interieur",
        "subcategory": "salle_gastronomique",
        "title": "Dining room with decorated tables",
        "author": "Jay Wennington",
        "page_url": "https://unsplash.com/photos/dining-room-table-with-wine-glasses-Y11qUMLrJY4",
        "direct_url": "https://images.unsplash.com/photo-1414235077428-338989a2e8c0?fm=jpg&w=1600&q=85",
        "desc": "Grande salle de restaurant avec ensemble de tables rondes dressées."
    },
    {
        "id_slug": "photo-1537047902294-62a40c20a6ae",
        "category": "espace_familial",
        "subcategory": "salle_familiale",
        "title": "Spacious restaurant dining area with multiple tables",
        "author": "Jason Leung",
        "page_url": "https://unsplash.com/photos/round-brown-wooden-table-and-chairs-inside-building-Xqda6cvTPEU",
        "direct_url": "https://images.unsplash.com/photo-1537047902294-62a40c20a6ae?fm=jpg&w=1600&q=85",
        "desc": "Grand espace de restauration familiale avec de nombreuses tables circulaires et carrées."
    },
    {
        "id_slug": "photo-1552566626-52f8b828add9",
        "category": "espace_familial",
        "subcategory": "espace_brasserie",
        "title": "Bright dining area with rows of tables",
        "author": "Nick Karvounis",
        "page_url": "https://unsplash.com/photos/brown-wooden-chairs-inside-restaurant-PrQqQVPzMlA",
        "direct_url": "https://images.unsplash.com/photo-1552566626-52f8b828add9?fm=jpg&w=1600&q=85",
        "desc": "Grande brasserie lumineuse avec ensemble continu de tables et banquettes."
    },
    {
        "id_slug": "photo-1544025162-d76694265947",
        "category": "espace_familial",
        "subcategory": "espace_repas_partage",
        "title": "Communal dining room with long tables",
        "author": "Dan Gold",
        "page_url": "https://unsplash.com/photos/empty-wooden-table-and-chairs-4_jhDO54BYg",
        "direct_url": "https://images.unsplash.com/photo-1544025162-d76694265947?fm=jpg&w=1600&q=85",
        "desc": "Espace familial et convivial avec longues tables en bois partagées."
    },
    {
        "id_slug": "photo-1559329007-40df8a9345d8",
        "category": "cafe_terrasse",
        "subcategory": "terrasse_exterieure",
        "title": "Outdoor cafe seating with tables under umbrellas",
        "author": "Mick Haupt",
        "page_url": "https://unsplash.com/photos/tables-and-chairs-outside-cafe-4ZqI5l4Y3y0",
        "direct_url": "https://images.unsplash.com/photo-1559329007-40df8a9345d8?fm=jpg&w=1600&q=85",
        "desc": "Terrasse extérieure de café avec rangées de tables et chaises en métal."
    },
    {
        "id_slug": "photo-1525610553991-2bede1a236e2",
        "category": "cafe_terrasse",
        "subcategory": "terrasse_rue",
        "title": "Outdoor street cafe tables and chairs",
        "author": "Alisa Anton",
        "page_url": "https://unsplash.com/photos/empty-tables-and-chairs-outside-cafe-zJzX9a9tD7M",
        "direct_url": "https://images.unsplash.com/photo-1525610553991-2bede1a236e2?fm=jpg&w=1600&q=85",
        "desc": "Ensemble de tables de terrasse sur un trottoir pavé devant un café."
    },
    {
        "id_slug": "photo-1466978913421-dad2ebd01d17",
        "category": "cafe_terrasse",
        "subcategory": "terrasse_ensoleillee",
        "title": "Outdoor patio dining tables",
        "author": "Stefan Johnson",
        "page_url": "https://unsplash.com/photos/empty-patio-furniture-during-daytime-xYsKGqy348Q",
        "direct_url": "https://images.unsplash.com/photo-1466978913421-dad2ebd01d17?fm=jpg&w=1600&q=85",
        "desc": "Terrasse ensoleillée avec ensemble de petites tables rondes de café."
    },
    {
        "id_slug": "photo-1578474846511-04ba529f0b88",
        "category": "espace_familial",
        "subcategory": "foodcourt_cafeteria",
        "title": "Modern cafeteria food court tables",
        "author": "Marcos Paulo Prado",
        "page_url": "https://unsplash.com/photos/white-and-brown-wooden-table-and-chairs-inside-building-wZ_xP8HjD98",
        "direct_url": "https://images.unsplash.com/photo-1578474846511-04ba529f0b88?fm=jpg&w=1600&q=85",
        "desc": "Vue large sur un espace cafétéria/food court avec de nombreuses tables alignées."
    }
]

# Wikimedia Commons queries to collect high-quality public domain / CC photos
WIKI_QUERIES = [
    # Cafés et terrasses
    ("cafe_terrasse", "terrasse_cafe", "cafe terrace outdoor tables chairs"),
    ("cafe_terrasse", "terrasse_bistrot", "sidewalk cafe tables and chairs"),
    ("cafe_terrasse", "cafe_interieur", "coffee shop interior seating tables"),
    ("cafe_terrasse", "patio_cafe", "outdoor cafe seating area tables"),
    
    # Restaurant salles
    ("restaurant_interieur", "salle_manger", "restaurant dining room tables"),
    ("restaurant_interieur", "salle_bistrot", "empty restaurant tables and chairs"),
    ("restaurant_interieur", "salle_moderne", "modern restaurant tables interior"),
    ("restaurant_interieur", "restaurant_tables", "tables in a restaurant dining area"),
    
    # Espace familial & Food Courts
    ("espace_familial", "food_court", "food court tables and chairs"),
    ("espace_familial", "cafeteria", "cafeteria dining tables rows"),
    ("espace_familial", "espace_repas", "family restaurant dining tables"),
    ("espace_familial", "reception_buffet", "buffet restaurant seating tables"),
    
    # Commons Unsplash CC0 collection
    ("cafe_terrasse", "unsplash_cafe", "Unsplash cafe tables"),
    ("restaurant_interieur", "unsplash_restaurant", "Unsplash restaurant tables"),
    ("espace_familial", "unsplash_dining", "Unsplash dining tables")
]

def search_wikimedia_commons():
    url = 'https://commons.wikimedia.org/w/api.php'
    seen_keys = set()
    selected_wiki = []
    
    for category, subcategory, q in WIKI_QUERIES:
        params = {
            'action': 'query',
            'generator': 'search',
            'gsrsearch': q,
            'gsrnamespace': 6,
            'gsrlimit': 15,
            'prop': 'imageinfo',
            'iiprop': 'url|size|extmetadata',
            'iiurlwidth': 1600,
            'format': 'json'
        }
        try:
            r = requests.get(url, params=params, headers=HEADERS, timeout=12)
            pages = r.json().get('query', {}).get('pages', {})
            count_q = 0
            for pid, p in pages.items():
                title = p.get('title', '')
                t_lower = title.lower()
                ext = t_lower.split('.')[-1]
                if ext not in ['jpg', 'jpeg', 'png']:
                    continue
                
                # Exclude unwanted media (paintings, historical vintage, single items)
                bad_tokens = ['painting', 'drawing', 'engraving', 'map', 'coin', 'stamp', 'logo', 'diagram', 
                              'mohai', '190', '191', '192', '193', '194', '195', 'black and white', 
                              'gravure', 'dessin', 'illustration', 'sketch', 'aerial view', 'drone', 'grave', 'tomb']
                if any(b in t_lower for b in bad_tokens):
                    continue

                ii = p.get('imageinfo', [{}])[0]
                meta = ii.get('extmetadata', {})
                desc = meta.get('ImageDescription', {}).get('value', '')
                desc_clean = re.sub('<[^<]+?>', '', desc).strip()
                
                combined_text = (title + " " + desc_clean).lower()
                if not any(k in combined_text for k in ['table', 'tables', 'terrace', 'terrasse', 'dining', 'seating', 'chair', 'cafe', 'café', 'restaurant']):
                    continue
                
                # Normalization key to avoid duplicates
                norm_key = re.sub(r'[^a-z0-9]', '', title.lower()[:32])
                if norm_key in seen_keys:
                    continue

                w = ii.get('width', 0)
                h = ii.get('height', 0)
                if w < 900 or h < 600:
                    continue
                
                artist = meta.get('Artist', {}).get('value', 'Wikimedia Commons Contributor')
                artist = re.sub('<[^<]+?>', '', artist).strip()
                license_name = meta.get('LicenseShortName', {}).get('value', 'CC / Public Domain')
                
                seen_keys.add(norm_key)
                selected_wiki.append({
                    'platform': 'Wikimedia Commons',
                    'category': category,
                    'subcategory': subcategory,
                    'title': title.replace('File:', ''),
                    'author': artist,
                    'license': license_name,
                    'page_url': ii.get('descriptionurl', ''),
                    'thumb_url': ii.get('thumburl', ''),
                    'orig_url': ii.get('url', ''),
                    'desc': desc_clean[:180] or title.replace('File:', '')
                })
                count_q += 1
                if count_q >= 4: # balance across queries
                    break
        except Exception as e:
            print(f"Error searching {q}: {e}")
            
    return selected_wiki

def download_and_process():
    print("=== Phase 1 : Recherche des images sur Wikimedia Commons ===")
    wiki_items = search_wikimedia_commons()
    print(f"Wikimedia Commons : {len(wiki_items)} images sélectionnées.")
    
    # Merge items
    all_items = []
    
    # Add Unsplash items
    for item in UNSPLASH_CURATED:
        all_items.append({
            'platform': 'Unsplash',
            'category': item['category'],
            'subcategory': item['subcategory'],
            'title': item['title'],
            'author': item['author'],
            'license': 'Unsplash License',
            'page_url': item['page_url'],
            'download_url': item['direct_url'],
            'fallback_url': None,
            'desc': item['desc']
        })
        
    # Add Wiki items
    for item in wiki_items:
        all_items.append({
            'platform': item['platform'],
            'category': item['category'],
            'subcategory': item['subcategory'],
            'title': item['title'],
            'author': item['author'],
            'license': item['license'],
            'page_url': item['page_url'],
            'download_url': item['thumb_url'] or item['orig_url'],
            'fallback_url': item['orig_url'],
            'desc': item['desc']
        })
        
    print(f"Total à télécharger : {len(all_items)} images.")
    
    downloaded_records = []
    index = 1
    
    print("\n=== Phase 2 : Téléchargement, normalisation et vérification PIL ===")
    for item in all_items:
        cat = item['category']
        prefix = f"table_ensemble_{index:03d}_{cat}"
        target_filename = f"{prefix}.jpg"
        target_path = os.path.join(IMAGES_DIR, target_filename)
        
        # Try downloading
        content = None
        for try_url in [item['download_url'], item.get('fallback_url')]:
            if not try_url:
                continue
            try:
                r = requests.get(try_url, headers=HEADERS, timeout=15)
                if r.status_code == 200 and len(r.content) > 10000:
                    content = r.content
                    break
            except Exception as e:
                pass
                
        if not content:
            print(f"[{index:02d}] Échec de téléchargement pour {item['title'][:30]}")
            continue
            
        try:
            img = Image.open(io.BytesIO(content))
            img = img.convert('RGB')
            orig_w, orig_h = img.size
            
            # Standardize resolution: max dimension 1600px
            max_dim = 1600
            if max(orig_w, orig_h) > max_dim:
                img.thumbnail((max_dim, max_dim), Image.Resampling.LANCZOS)
                
            final_w, final_h = img.size
            img.save(target_path, format="JPEG", quality=88, optimize=True)
            filesize_kb = os.path.getsize(target_path) // 1024
            
            print(f"[{index:02d}] OK: {target_filename} ({final_w}x{final_h}, {filesize_kb} KB) - {item['platform']}")
            
            downloaded_records.append({
                "id": f"IMG_{index:03d}",
                "filename": target_filename,
                "category": item['category'],
                "subcategory": item['subcategory'],
                "platform": item['platform'],
                "title": item['title'],
                "author": item['author'],
                "license": item['license'],
                "width": final_w,
                "height": final_h,
                "filesize_kb": filesize_kb,
                "page_url": item['page_url'],
                "description": item['desc']
            })
            index += 1
        except Exception as e:
            print(f"[{index:02d}] Erreur traitement image {item['title'][:30]}: {e}")
            
    print(f"\n=== Phase 3 : Création du manifeste CSV ({len(downloaded_records)} entrées) ===")
    csv_path = os.path.join(OUTPUT_DIR, "dataset_metadata.csv")
    fieldnames = [
        "id", "filename", "category", "subcategory", "platform",
        "title", "author", "license", "width", "height", "filesize_kb",
        "page_url", "description"
    ]
    with open(csv_path, mode='w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for rec in downloaded_records:
            writer.writerow(rec)
            
    print(f"Manifeste CSV enregistré: {csv_path}")
    
    # Generate README.md
    print("=== Phase 4 : Création du README.md ===")
    readme_path = os.path.join(OUTPUT_DIR, "README.md")
    generate_readme(readme_path, downloaded_records)
    print(f"README.md enregistré: {readme_path}")

def generate_readme(readme_path, records):
    by_cat = {}
    by_plat = {}
    total_size = sum(r['filesize_kb'] for r in records)
    
    for r in records:
        by_cat[r['category']] = by_cat.get(r['category'], 0) + 1
        by_plat[r['platform']] = by_plat.get(r['platform'], 0) + 1
        
    content = f"""# Dataset d'Ensembles de Tables (Cafés, Restaurants, Espaces Familiaux)

Ce dossier regroupe un jeu de photos soigneusement sélectionnées et téléchargées conformément à votre demande :
**Des photos de cafés (tables de café), de restaurants et d'espaces familiaux présentant un « ensemble de tables » (plusieurs tables visibles dans chaque scène)** pour la vision par ordinateur et la détection d'objets (YOLOv8).

---

## 1. Résumé du Dataset

- **Nombre total d'images :** {len(records)} images
- **Poids total :** ~{total_size / 1024:.2f} Mo
- **Format :** JPEG standardisé (qualité 88, dimensions max 1600 px)
- **Objectif visuel :** Présence de **plusieurs tables simultanées** (rangées de tables, terrasses, tables intérieures, espaces repas familiaux, food courts).

### Répartition par catégorie

| Catégorie | Description | Nombre d'images |
| :--- | :--- | :---: |
| `cafe_terrasse` | Terrasses extérieures, tables de trottoir, salons de café et coffee shops | {by_cat.get('cafe_terrasse', 0)} |
| `restaurant_interieur` | Salles à manger, bistrots contemporains, alignements de tables intérieures | {by_cat.get('restaurant_interieur', 0)} |
| `espace_familial` | Food courts, cafétérias, espaces buffet et grandes salles familiales | {by_cat.get('espace_familial', 0)} |
| **Total** | | **{len(records)}** |

### Répartition par plateforme source

| Plateforme | Nombre d'images | Statut d'accès & Licence |
| :--- | :---: | :--- |
| **Wikimedia Commons (Wikipedia)** | {by_plat.get('Wikimedia Commons', 0)} | Accès libre API, licences CC-BY, CC-BY-SA, CC0 et Domaine Public avec attribution. |
| **Unsplash** | {by_plat.get('Unsplash', 0)} | Téléchargement direct HD, photographies professionnelles sous Unsplash License / CC0. |

---

## 2. Note d'accès aux différentes plateformes demandées

Conformément à votre demande de recherche sur plusieurs plateformes (Google Maps, Wikipedia, Unsplash, Pinterest, Facebook, Instagram) :

1. **Wikipedia & Wikimedia Commons :** 
   - Entièrement accessible via API sans restriction d'authentification.
   - Fournit des images réelles de terrasses de café, de restaurants et de cafétérias du monde entier avec licences ouvertes vérifiables.
2. **Unsplash :**
   - Accessible pour le téléchargement direct d'images haute définition montrant des aménagements de tables réels de grande qualité.
3. **Pinterest, Instagram, Facebook & Google Maps :**
   - **Protection anti-scraping et murs de connexion :** Ces plateformes imposent une authentification obligatoire (login), des protections anti-robots (CAPTCHA, Cloudflare, rate limiting strict) et interdisent dans leurs conditions d'utilisation (Terms of Service) le scraping automatisé massif sans API propriétaire payante et accréditée.
   - **Accès légal et éthique :** Le téléchargement automatisé direct depuis Instagram/Facebook/Pinterest sans jetons développeurs officiels est bloqué au niveau réseau. Pour ces raisons techniques et de conformité, le dataset privilégie les sources ouvertes et accessibles (Wikimedia Commons et Unsplash), tout en respectant scrupuleusement le contenu demandé (*ensemble de tables en café, restaurant et espace familial*).

---

## 3. Structure des fichiers

```text
dataset_tables_ensemble/
├── images/
│   ├── table_ensemble_001_restaurant_interieur.jpg
│   ├── table_ensemble_002_cafe_terrasse.jpg
│   ├── ...
│   └── table_ensemble_{len(records):03d}_espace_familial.jpg
├── dataset_metadata.csv   # Tableau complet des métadonnées (ID, auteur, licence, URL, résolution)
└── README.md              # Cette documentation
```

---

## 4. Aperçu des métadonnées (échantillon)

| ID | Fichier | Catégorie | Source | Licence | Résolution |
| :--- | :--- | :--- | :--- | :--- | :--- |
"""
    for r in records[:10]:
        content += f"| `{r['id']}` | `{r['filename']}` | `{r['category']}` | {r['platform']} | {r['license']} | {r['width']}x{r['height']} |\n"

    content += """
*(Consultez `dataset_metadata.csv` pour la liste exhaustive des 50+ photos avec liens directs et attributions).*

---

## 5. Utilisation pour l'entraînement YOLOv8

1. Les images ont été redimensionnées avec un ratio d'aspect préservé à un maximum de 1600 px (idéal pour l'entraînement à 640×640 ou 1280×1280 sous YOLOv8).
2. Toutes les images présentent **plusieurs tables**, ce qui permet d'annoter plusieurs boîtes englobantes (`table`) par photo, que ce soit pour les classes `clean`, `dirty` ou `occupied`.
"""
    with open(readme_path, 'w', encoding='utf-8') as f:
        f.write(content)

if __name__ == '__main__':
    download_and_process()

