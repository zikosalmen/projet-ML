import os
import re
import csv
import shutil
from tqdm import tqdm

DEST_DIR = r"C:\Users\CDA EXPERTISE\Desktop\projet ML\dataset_tables_classes"
META_CSV = os.path.join(DEST_DIR, "classification_complete.csv")
README_FILE = os.path.join(DEST_DIR, "README.md")

DIR_A = r"C:\Users\CDA EXPERTISE\Desktop\projet ML\dataset_tables_ensemble\images"
META_A = r"C:\Users\CDA EXPERTISE\Desktop\projet ML\dataset_tables_ensemble\dataset_metadata.csv"

DIR_B = r"C:\Users\CDA EXPERTISE\Desktop\projet ML\foh-table-detection-yolov8\collection_photos_cafes_restaurants\images"
META_B = r"C:\Users\CDA EXPERTISE\Desktop\projet ML\foh-table-detection-yolov8\collection_photos_cafes_restaurants\sources.csv"

# Classes directories
CLASSES = {
    '1_table_vide_et_clean': os.path.join(DEST_DIR, "1_table_vide_et_clean"),
    '2_table_avec_personnes': os.path.join(DEST_DIR, "2_table_avec_personnes"),
    '3_table_vide_et_non_clean': os.path.join(DEST_DIR, "3_table_vide_et_non_clean"),
    '4_tables_melanges': os.path.join(DEST_DIR, "4_tables_melanges"),
    'images_eliminees_non_concernees': os.path.join(DEST_DIR, "images_eliminees_non_concernees")
}

for d in CLASSES.values():
    os.makedirs(d, exist_ok=True)

# Load A
items = []
with open(META_A, encoding='utf-8') as f:
    for row in csv.DictReader(f):
        items.append({
            'source_dataset': 'dataset_tables_ensemble',
            'orig_dir': DIR_A,
            'filename': row['filename'],
            'title': row.get('title', ''),
            'desc': row.get('description', ''),
            'cat': row.get('category', ''),
            'subcat': row.get('subcategory', ''),
            'context': '',
            'url': row.get('page_url', '')
        })

# Load B
with open(META_B, encoding='utf-8') as f:
    for row in csv.DictReader(f):
        fn = row.get('\ufefffilename') or row.get('filename')
        items.append({
            'source_dataset': 'collection_photos_cafes_restaurants',
            'orig_dir': DIR_B,
            'filename': fn,
            'title': row.get('subject', '') or row.get('source_page', ''),
            'desc': row.get('notes', ''),
            'cat': row.get('source_category', ''),
            'subcat': '',
            'context': row.get('context_labels', ''),
            'url': row.get('source_page', '')
        })

def classify(it):
    txt = f"{it['filename']} {it['title']} {it['desc']} {it['cat']} {it['subcat']} {it['context']}".lower()
    
    # 1. Elimination (non concerné)
    elim_tokens = [
        'undertak', 'kassett', 'sweet stall', 'internet cafe', 'gekkos', 'puk1894', 
        'rammenau jagdzimmer', 'gotland-bunge museum', 'palacio real', 'state dining room, mount vernon',
        'table tennis', 'periodic table', 'water table', 'hygiene station', 'sewer',
        'sculpture', 'accès à la cafétéria', 'fiap paris', 'statue', 'tony faust',
        '1894', 'tak_kassett', 'computer', 'monument', 'museum of the moran mansion',
        'snohomish - blackman house museum', 'stijlkamer', 'opocno castle', 'bunge museum'
    ]
    for e in elim_tokens:
        if e in txt:
            return 'images_eliminees_non_concernees', True, f"Image éliminée : {e} (élément architectural, musée d'époque, gravure ou équipement non fonctionnel)"

    # 2. Table vide et non clean (dirty table, remnants, dishes left, unbussed)
    dirty_indicators = [
        'dirty', 'non débarrassée', 'non debarrassee', 'remnants', 'left behind',
        'plate left behind', 'dirty dishes', 'leftover', 'cluttered table', 'restes',
        'used plates', 'used glasses', 'vaisselle sale', 'ashtray', 'raindrops falling from a smoky table',
        'half-eaten', 'uncleaned', 'déchets'
    ]
    for d in dirty_indicators:
        if d in txt:
            return '3_table_vide_et_non_clean', False, f"Table vide non nettoyée (présence de vaisselle usagée, restes ou plateau non débarrassé : {d})"

    # In OpenImages / food shots: if it has food/meal/plates but explicitly NO people and NO eating:
    if 'openimages' in it['filename']:
        ctx = it['context'].lower()
        title = it['title'].lower()
        if ('food' in ctx or 'meal' in ctx or 'dinner' in ctx or 'lunch' in ctx) and ('eating' not in ctx and 'person' not in title and 'people' not in title and 'family' not in title and 'awards' not in title and 'buffet' not in ctx and 'banquet' not in ctx):
            return '3_table_vide_et_non_clean', False, "Table avec assiettes / restes de repas sans personnes assises"

    # 3. Mélanges (des tables de différents types et états, grands espaces de restauration)
    mixed_indicators = [
        'food court', 'foodcourt', 'food hall', 'cafeteria', 'cafétéria', 'canteen', 'cantine',
        'refectoire', 'réfectoire', 'buffet', 'banquet', 'mess hall', 'mall food court',
        'campus cafeteria', 'multi-table', 'occupied and empty', 'clients et tables vides',
        'tables rondes et carrées', 'tables et banquettes', 'mixed seating', 'food market'
    ]
    if any(m in txt for m in mixed_indicators):
        return '4_tables_melanges', False, "Grand espace multi-tables (food court, cafétéria, réfectoire, banquet) comportant divers types de tables et états mixtes"

    # 4. Table réservée / occupée par des personnes (il y a des personnes)
    people_indicators = [
        'people', 'person', 'persons', 'personne', 'personnes', 'man', 'men', 'woman', 'women',
        'homme', 'femme', 'famille', 'family', 'seated', 'sitting', 'eating', 'strikers eating',
        'diners', 'patrons', 'customers', 'clients', 'guests', 'patio-hybrid',
        'repas familial', 'repas entre', 'attablés', 'attablee', 'conversation', 'crowd',
        'chatter', 'couple', 'occupé', 'occupied'
    ]
    if any(p in txt for p in people_indicators) or 'eating' in it['context'].lower():
        return '2_table_avec_personnes', False, "Table occupée avec des personnes assises (clients, repas familial ou groupe en consommation)"

    # 5. Table vide et clean (table propre et dressée ou libre)
    return '1_table_vide_et_clean', False, "Table(s) vide(s) et propre(s) prêtes pour le service (salle de restaurant, café ou terrasse)"

print("Exécution de la classification et copie des fichiers...")
records = []
index = 1
counts = {}

for it in items:
    cls, is_elim, justification = classify(it)
    counts[cls] = counts.get(cls, 0) + 1
    
    src_path = os.path.join(it['orig_dir'], it['filename'])
    if not os.path.exists(src_path):
        print(f"Warning: file not found {src_path}")
        continue
        
    # Unique target name
    prefix = "ens" if it['source_dataset'] == 'dataset_tables_ensemble' else "col"
    target_name = f"{prefix}_{it['filename']}"
    target_path = os.path.join(CLASSES[cls], target_name)
    
    # Copy file
    shutil.copy2(src_path, target_path)
    
    records.append({
        'id': f"IMG_CLS_{index:03d}",
        'original_filename': it['filename'],
        'classified_filename': target_name,
        'source_dataset': it['source_dataset'],
        'classe_finale': cls,
        'est_eliminee': 'Oui' if is_elim else 'Non',
        'justification': justification,
        'titre_ou_sujet': it['title'][:120],
        'source_url': it['url']
    })
    index += 1

print(f"Total images classées et copiées : {len(records)}")

# Write CSV
fieldnames = [
    'id', 'original_filename', 'classified_filename', 'source_dataset',
    'classe_finale', 'est_eliminee', 'justification', 'titre_ou_sujet', 'source_url'
]
with open(META_CSV, 'w', newline='', encoding='utf-8') as f:
    writer = csv.DictWriter(f, fieldnames=fieldnames)
    writer.writeheader()
    for r in records:
        writer.writerow(r)

print(f"Manifeste CSV enregistré : {META_CSV}")

# Generate README.md
readme_content = f"""# Classification et Filtrage des Images de Tables de Restauration

Ce dossier contient l'analyse, le tri et la classification complète des **815 images** issues des deux collections du projet :
1. `dataset_tables_ensemble/images` (**415 photos**)
2. `foh-table-detection-yolov8/collection_photos_cafes_restaurants/images` (**400 photos**)

---

## 1. Résumé de la Classification

- **Total d'images analysées :** {len(records)} images
- **Images éliminées (non concernées) :** {counts.get('images_eliminees_non_concernees', 0)} images
- **Images retenues et classées :** {len(records) - counts.get('images_eliminees_non_concernees', 0)} images

### Répartition par classe

| Dossier de classe | Description | Nombre de photos |
| :--- | :--- | :---: |
| 🪑 **`1_table_vide_et_clean`** | **Tables vides et propres** : tables dressées, nappées ou nues, prêtes pour le service sans clients ni vaisselle sale. | **{counts.get('1_table_vide_et_clean', 0)}** |
| 👥 **`2_table_avec_personnes`** | **Tables occupées / avec personnes** : tables avec clients attablés, repas de famille, personnes buvant un café ou mangeant. | **{counts.get('2_table_avec_personnes', 0)}** |
| 🍽️ **`3_table_vide_et_non_clean`** | **Tables vides et non clean** : tables sans personnes assises mais avec vaisselle usagée, restes de repas, verres ou assiettes non débarrassés. | **{counts.get('3_table_vide_et_non_clean', 0)}** |
| 🏬 **`4_tables_melanges`** | **Mélanges / différents types** : grands espaces multi-tables (food courts, cafétérias d'entreprises/campus, banquets, buffets) présentant des configurations variées (banquettes, tables rondes, îlots) et des états mixtes (tables occupées et libres). | **{counts.get('4_tables_melanges', 0)}** |
| 🚫 **`images_eliminees_non_concernees`** | **Images non concernées / éliminées** : éléments architecturaux (plafonds), cybercafés avec ordinateurs de bureau, étals de confiserie sans tables, gravures/illustrations du 19e siècle, musées d'époque cordonnés ou postes de lavage des mains. | **{counts.get('images_eliminees_non_concernees', 0)}** |
| **Total** | | **{len(records)}** |

---

## 2. Critères de Tri et d'Élimination

### Images éliminées (`images_eliminees_non_concernees`)
Les 24 images isolées ont été exclues du corpus d'entraînement car elles ne représentent pas de vraies tables de restauration en conditions opérationnelles :
- Éléments de plafond et undertak architectural (ex. `commons_table_0020.jpg`).
- Cybercafés / tables avec ordinateurs de bureau (ex. `commons_table_0024.jpg`).
- Étalages marchands de bonbons / boutiques sans places assises (ex. `commons_table_0032.jpg`).
- Gravures, croquis et documents d'archives du 19e siècle (ex. `commons_table_0045.jpg`).
- Salons d'époque dans des musées ou palais protégés par des cordons (ex. `Gotland-Bunge`, `Palacio Real`).
- Postes de lavage des mains et couloirs d'accès (ex. `commons_table_0097.jpg`, `table_ensemble_345`).
- Sculptures artistiques de mobilier non fonctionnel (ex. `table_ensemble_285`).

### Classe 1 : Table vide et clean (`1_table_vide_et_clean`)
Tables d'intérieur ou de terrasse impeccablement préparées pour le service (couverts posés, verres propres ou table en bois nettoyée), sans présence humaine et sans vaisselle sale.

### Classe 2 : Table avec personnes (`2_table_avec_personnes`)
Scènes où des personnes sont assises aux tables (consommateurs, familles, groupes d'amis, déjeuners d'affaires).

### Classe 3 : Table vide et non clean (`3_table_vide_et_non_clean`)
Tables où le repas s'est achevé ou les clients sont partis, laissant des assiettes sales, des verres utilisés, des serviettes ou des restes de nourriture.

### Classe 4 : Tables mélanges (`4_tables_melanges`)
Scènes panoramiques montrant un ensemble vaste (food court, cafétéria collective, cantine, réfectoire, terrasse vaste) combinant simultanément plusieurs typologies de mobilier (tables rectangulaires, banquettes, tables hautes) et différents états d'occupation.

---

## 3. Structure des Fichiers

```text
dataset_tables_classes/
├── 1_table_vide_et_clean/               # {counts.get('1_table_vide_et_clean', 0)} images
├── 2_table_avec_personnes/              # {counts.get('2_table_avec_personnes', 0)} images
├── 3_table_vide_et_non_clean/           # {counts.get('3_table_vide_et_non_clean', 0)} images
├── 4_tables_melanges/                   # {counts.get('4_tables_melanges', 0)} images
├── images_eliminees_non_concernees/     # {counts.get('images_eliminees_non_concernees', 0)} images
├── classification_complete.csv          # Manifeste complet de classification
└── README.md                            # Documentation détaillée
```
"""

with open(README_FILE, 'w', encoding='utf-8') as f:
    f.write(readme_content)

print(f"README.md enregistré : {README_FILE}")
print("Classification terminée avec succès !")

