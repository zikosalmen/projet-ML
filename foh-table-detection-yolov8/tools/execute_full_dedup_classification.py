import os
import csv
import shutil
import hashlib
from pathlib import Path
from collections import defaultdict, Counter
from tqdm import tqdm

ROOT = Path(r"c:\Users\CDA EXPERTISE\Desktop\projet ML")
DEST_DIR = ROOT / "dataset_tables_classes"

ENS_DIR = ROOT / "dataset_tables_ensemble" / "images"
ENS_META = ROOT / "dataset_tables_ensemble" / "dataset_metadata.csv"

COL_DIR = ROOT / "foh-table-detection-yolov8" / "collection_photos_cafes_restaurants" / "images"
COL_META = ROOT / "foh-table-detection-yolov8" / "collection_photos_cafes_restaurants" / "sources.csv"
UNV_DIR = ROOT / "foh-table-detection-yolov8" / "collection_photos_cafes_restaurants" / "unverified_downloads"

YOLO_TRAIN_DIR = ROOT / "foh-table-detection-yolov8" / "train"
YOLO_VALID_DIR = ROOT / "foh-table-detection-yolov8" / "valid"
YOLO_TEST_DIR = ROOT / "foh-table-detection-yolov8" / "test"

CLASSES = {
    '1_table_vide_et_clean': DEST_DIR / "1_table_vide_et_clean",
    '2_table_avec_personnes': DEST_DIR / "2_table_avec_personnes",
    '3_table_vide_et_non_clean': DEST_DIR / "3_table_vide_et_non_clean",
    '4_tables_melanges': DEST_DIR / "4_tables_melanges",
    'images_eliminees_non_concernees': DEST_DIR / "images_eliminees_non_concernees"
}

CSV_FILE = DEST_DIR / "classification_complete.csv"
README_FILE = DEST_DIR / "README.md"

# Load metadata dictionaries
ens_meta_dict = {}
with open(ENS_META, encoding='utf-8') as f:
    for row in csv.DictReader(f):
        ens_meta_dict[row['filename']] = row

col_meta_dict = {}
with open(COL_META, encoding='utf-8') as f:
    for row in csv.DictReader(f):
        fn = row.get('\ufefffilename') or row.get('filename')
        col_meta_dict[fn] = row

# Step 1: Collect all files across all 6 sources
all_files = []

for f in sorted(ENS_DIR.glob('*.*')):
    if f.suffix.lower() in ['.jpg', '.jpeg', '.png']:
        m = ens_meta_dict.get(f.name, {})
        all_files.append({
            'source_group': 'dataset_tables_ensemble',
            'source_dir': str(ENS_DIR),
            'filepath': f,
            'filename': f.name,
            'prefix': 'ens',
            'url': m.get('page_url', ''),
            'title': m.get('title', ''),
            'desc': m.get('description', ''),
            'cat': m.get('category', ''),
            'subcat': m.get('subcategory', ''),
            'context': '',
            'labels': []
        })

for f in sorted(COL_DIR.glob('*.*')):
    if f.suffix.lower() in ['.jpg', '.jpeg', '.png']:
        m = col_meta_dict.get(f.name, {})
        all_files.append({
            'source_group': 'collection_photos_cafes_restaurants',
            'source_dir': str(COL_DIR),
            'filepath': f,
            'filename': f.name,
            'prefix': 'col',
            'url': m.get('source_page', ''),
            'title': m.get('subject', '') or m.get('source_page', ''),
            'desc': m.get('notes', ''),
            'cat': m.get('source_category', ''),
            'subcat': '',
            'context': m.get('context_labels', ''),
            'labels': []
        })

for f in sorted(UNV_DIR.glob('*.*')):
    if f.suffix.lower() in ['.jpg', '.jpeg', '.png']:
        all_files.append({
            'source_group': 'unverified_downloads',
            'source_dir': str(UNV_DIR),
            'filepath': f,
            'filename': f.name,
            'prefix': 'unv',
            'url': '',
            'title': f'Unverified download {f.name}',
            'desc': 'Téléchargement Commons interrompu',
            'cat': 'unverified',
            'subcat': '',
            'context': '',
            'labels': []
        })

for sname, sdir, prefix in [
    ('yolo_train', YOLO_TRAIN_DIR, 'yolo_train'),
    ('yolo_valid', YOLO_VALID_DIR, 'yolo_valid'),
    ('yolo_test', YOLO_TEST_DIR, 'yolo_test')
]:
    img_dir = sdir / 'images'
    lbl_dir = sdir / 'labels'
    for f in sorted(img_dir.glob('*.*')):
        if f.suffix.lower() in ['.jpg', '.jpeg', '.png']:
            lbl_file = lbl_dir / f'{f.stem}.txt'
            lbls = []
            if lbl_file.exists():
                for line in lbl_file.read_text().splitlines():
                    if line.strip():
                        lbls.append(line.strip().split()[0])
            all_files.append({
                'source_group': sname,
                'source_dir': str(img_dir),
                'filepath': f,
                'filename': f.name,
                'prefix': prefix,
                'url': '',
                'title': f'YOLOv8 {sname} {f.name}',
                'desc': f'Classes YOLO annotées : {sorted(set(lbls))}',
                'cat': sname,
                'subcat': '',
                'context': ' '.join(lbls),
                'labels': lbls
            })

print(f"Total fichiers analysés across all sources: {len(all_files)}")

# Compute SHA-256 for all files
for item in all_files:
    h = hashlib.sha256()
    with open(item['filepath'], 'rb') as fp:
        while chunk := fp.read(65536):
            h.update(chunk)
    item['sha256'] = h.hexdigest()

# Deduplication Phase 1: Exact SHA-256
hash_map = defaultdict(list)
for item in all_files:
    hash_map[item['sha256']].append(item)

def sort_key(it):
    g = it['source_group']
    if g == 'collection_photos_cafes_restaurants': return 0
    if g == 'dataset_tables_ensemble': return 1
    if g.startswith('yolo_'): return 2
    return 3

canonical_items = []
for h, items in hash_map.items():
    sorted_items = sorted(items, key=sort_key)
    canonical_items.append({
        'primary': sorted_items[0],
        'duplicates': sorted_items[1:],
        'hash': h,
        'url': sorted_items[0]['url']
    })

# Deduplication Phase 2: Duplicate URLs in dataset_tables_ensemble
url_map = defaultdict(list)
for c in canonical_items:
    if c['url']:
        url_map[c['url']].append(c)

merged_hashes = set()
for url, clist in url_map.items():
    if len(clist) > 1:
        base = clist[0]
        for other in clist[1:]:
            base['duplicates'].append(other['primary'])
            base['duplicates'].extend(other['duplicates'])
            merged_hashes.add(other['hash'])

canonical_items = [c for c in canonical_items if c['hash'] not in merged_hashes]

# Deduplication Phase 3: Known cross-format / recompressed duplicates
# commons_table_0103.png vs commons_table_0104.jpg
for c in canonical_items:
    if c['primary']['filename'] == 'commons_table_0103.png':
        for c2 in list(canonical_items):
            if c2['primary']['filename'] == 'commons_table_0104.jpg':
                c['duplicates'].append(c2['primary'])
                c['duplicates'].extend(c2['duplicates'])
                canonical_items.remove(c2)
                break
        break

# commons_table_0105.png vs commons_table_0106.jpg
for c in canonical_items:
    if c['primary']['filename'] == 'commons_table_0105.png':
        for c2 in list(canonical_items):
            if c2['primary']['filename'] == 'commons_table_0106.jpg':
                c['duplicates'].append(c2['primary'])
                c['duplicates'].extend(c2['duplicates'])
                canonical_items.remove(c2)
                break
        break

print(f"Total photos canoniques uniques : {len(canonical_items)}")
total_dups = sum(len(c['duplicates']) for c in canonical_items)
print(f"Total fichiers doublons éliminés : {total_dups}")
assert len(canonical_items) + total_dups == len(all_files), "Incohérence dans le décompte total des fichiers !"

# Classification logic
elim_tokens = [
    'undertak', 'kassett', 'sweet stall', 'internet cafe', 'gekkos', 'puk1894', 
    'rammenau jagdzimmer', 'gotland-bunge museum', 'palacio real', 'state dining room, mount vernon',
    'state dining room, mt. vernon', 'table tennis', 'periodic table', 'water table', 'hygiene station', 'sewer',
    'sculpture', 'accès à la cafétéria', 'fiap paris', 'statue', 'tony faust',
    '1894', 'tak_kassett', 'computer', 'monument', 'museum of the moran mansion',
    'snohomish - blackman house museum', 'stijlkamer', 'opocno castle', 'bunge museum',
    'mount vernon'
]

dirty_indicators = [
    'dirty', 'non débarrassée', 'non debarrassee', 'remnants', 'left behind',
    'plate left behind', 'dirty dishes', 'leftover', 'cluttered table', 'restes',
    'used plates', 'used glasses', 'vaisselle sale', 'ashtray', 'raindrops falling from a smoky table',
    'half-eaten', 'uncleaned', 'déchets'
]

mixed_indicators = [
    'food court', 'foodcourt', 'food hall', 'cafeteria', 'cafétéria', 'canteen', 'cantine',
    'refectoire', 'réfectoire', 'buffet', 'banquet', 'mess hall', 'mall food court',
    'campus cafeteria', 'multi-table', 'occupied and empty', 'clients et tables vides',
    'tables rondes et carrées', 'tables et banquettes', 'mixed seating', 'food market'
]

people_indicators = [
    'people', 'person', 'persons', 'personne', 'personnes', 'man', 'men', 'woman', 'women',
    'homme', 'femme', 'famille', 'family', 'seated', 'sitting', 'eating', 'strikers eating',
    'diners', 'patrons', 'customers', 'clients', 'guests', 'patio-hybrid',
    'repas familial', 'repas entre', 'attablés', 'attablee', 'conversation', 'crowd',
    'chatter', 'couple', 'occupé', 'occupied'
]

def classify_canonical(c_item):
    it = c_item['primary']
    grp = it['source_group']
    fn = it['filename']
    lbls = it['labels']

    # 1. YOLO specific rules
    if grp.startswith('yolo_'):
        lbl_set = set(lbls)
        if lbl_set == {'0'}:
            return '1_table_vide_et_clean', False, 'YOLOv8 : Table(s) vide(s) et propre(s) (annotation exclusive clean [0])'
        if lbl_set == {'1'}:
            return '3_table_vide_et_non_clean', False, 'YOLOv8 : Table(s) vide(s) non débarrassée(s) (annotation exclusive dirty [1])'
        if lbl_set == {'2'}:
            return '2_table_avec_personnes', False, 'YOLOv8 : Table(s) occupée(s) avec personnes (annotation exclusive occupied [2])'
        if len(lbl_set) > 1:
            return '4_tables_melanges', False, f'YOLOv8 : Espace multi-tables avec états mixtes (classes annotées : {sorted(lbl_set)})'
        return '1_table_vide_et_clean', False, 'YOLOv8 : Table libre'

    # 2. Unverified specific (Mount Vernon historic rooms)
    if grp == 'unverified_downloads':
        return 'images_eliminees_non_concernees', True, "Image éliminée : musée historique d'époque / State Dining Room Mount Vernon"

    txt = f"{fn} {it['title']} {it['desc']} {it['cat']} {it['subcat']} {it['context']}".lower()

    # 3. Elimination
    for e in elim_tokens:
        if e in txt:
            return 'images_eliminees_non_concernees', True, f"Image éliminée : {e} (élément architectural, musée d'époque, gravure ou équipement non fonctionnel)"

    # 4. Dirty table
    for d in dirty_indicators:
        if d in txt:
            return '3_table_vide_et_non_clean', False, f"Table vide non nettoyée (présence de vaisselle usagée, restes ou plateau non débarrassé : {d})"

    if 'openimages' in fn:
        ctx = it['context'].lower()
        title = it['title'].lower()
        if ('food' in ctx or 'meal' in ctx or 'dinner' in ctx or 'lunch' in ctx) and ('eating' not in ctx and 'person' not in title and 'people' not in title and 'family' not in title and 'awards' not in title and 'buffet' not in ctx and 'banquet' not in ctx):
            return '3_table_vide_et_non_clean', False, "Table avec assiettes / restes de repas sans personnes assises"

    # 5. Mixed
    if any(m in txt for m in mixed_indicators):
        return '4_tables_melanges', False, "Grand espace multi-tables (food court, cafétéria, réfectoire, banquet) comportant divers types de tables et états mixtes"

    # 6. People
    if any(p in txt for p in people_indicators) or 'eating' in it['context'].lower():
        return '2_table_avec_personnes', False, "Table occupée avec des personnes assises (clients, repas familial ou groupe en consommation)"

    # 7. Clean
    return '1_table_vide_et_clean', False, "Table(s) vide(s) et propre(s) prêtes pour le service (salle de restaurant, café ou terrasse)"

# Reset destination directories cleanly
print("Préparation des dossiers de destination...")
for cls, path in CLASSES.items():
    if path.exists():
        shutil.rmtree(path)
    path.mkdir(parents=True, exist_ok=True)

# Copy unique canonical files and track all records
records = []
canonical_counter = 1
duplicate_counter = 1
class_counts = Counter()

# Assign target name and copy
for c in tqdm(canonical_items, desc="Copie des images uniques"):
    p = c['primary']
    cls, is_elim, just = classify_canonical(c)
    c['assigned_class'] = cls
    c['is_eliminated'] = is_elim
    c['justification'] = just
    class_counts[cls] += 1

    target_filename = f"{p['prefix']}_{p['filename']}"
    target_path = CLASSES[cls] / target_filename
    shutil.copy2(p['filepath'], target_path)

    canon_id = f"CANON_{canonical_counter:03d}"
    canonical_counter += 1

    records.append({
        'id_manifest': canon_id,
        'statut': 'Unique_Retenu',
        'nom_fichier_final': target_filename,
        'classe_assignee': cls,
        'est_eliminee': 'Oui' if is_elim else 'Non',
        'est_doublon': 'Non',
        'ref_id_canonique': canon_id,
        'ref_fichier_canonique': target_filename,
        'nom_fichier_origine': p['filename'],
        'source_dossier': p['source_group'],
        'sha256': c['hash'],
        'justification': just,
        'titre_ou_contexte': p['title'][:100],
        'url_source': p['url']
    })

    # Record all duplicates pointing to this canonical image
    for dup in c['duplicates']:
        dup_id = f"DUP_{duplicate_counter:03d}"
        duplicate_counter += 1
        records.append({
            'id_manifest': dup_id,
            'statut': 'Doublon_Elimine',
            'nom_fichier_final': f"[NON COPIÉ - Doublon de {target_filename}]",
            'classe_assignee': cls,
            'est_eliminee': 'Oui',
            'est_doublon': 'Oui',
            'ref_id_canonique': canon_id,
            'ref_fichier_canonique': target_filename,
            'nom_fichier_origine': dup['filename'],
            'source_dossier': dup['source_group'],
            'sha256': dup['sha256'],
            'justification': f"Doublon redondant éliminé (identique à l'image {target_filename})",
            'titre_ou_contexte': dup['title'][:100],
            'url_source': dup['url']
        })

print(f"\nTotal enregistrements dans le manifeste : {len(records)} (doit être égal à {len(all_files)})")
assert len(records) == len(all_files), "Erreur de cohérence dans les enregistrements du manifeste !"

# Write CSV Manifest
fieldnames = [
    'id_manifest', 'statut', 'nom_fichier_final', 'classe_assignee',
    'est_eliminee', 'est_doublon', 'ref_id_canonique', 'ref_fichier_canonique',
    'nom_fichier_origine', 'source_dossier', 'sha256', 'justification',
    'titre_ou_contexte', 'url_source'
]

with open(CSV_FILE, 'w', newline='', encoding='utf-8') as f:
    writer = csv.DictWriter(f, fieldnames=fieldnames)
    writer.writeheader()
    for r in sorted(records, key=lambda x: x['id_manifest']):
        writer.writerow(r)

print(f"Manifeste CSV généré : {CSV_FILE}")

# Generate README.md
total_source = len(all_files)
total_uniques = len(canonical_items)
total_dups_count = sum(len(c['duplicates']) for c in canonical_items)
total_elim = class_counts['images_eliminees_non_concernees']
total_retenues = total_uniques - total_elim

readme_content = f"""# Classification Complète et Filtrage Rigoureux des Images de Tables

Ce dossier regroupe et consolide l'ensemble exhaustif des photos de tables issues de **tous les répertoires du projet Machine Learning** :
1. `dataset_tables_ensemble/images` (**415 photos brutes**)
2. `foh-table-detection-yolov8/collection_photos_cafes_restaurants/images` (**400 photos brutes**)
3. `foh-table-detection-yolov8/collection_photos_cafes_restaurants/unverified_downloads` (**8 photos brutes**)
4. `foh-table-detection-yolov8/train/images` (**102 photos brutes**)
5. `foh-table-detection-yolov8/valid/images` (**27 photos brutes**)
6. `foh-table-detection-yolov8/test/images` (**14 photos brutes**)

**Total brut analysé : {total_source} photos.**

---

## 1. Dédoublonnage Rigoureux ("Sans Redondance")

Afin de garantir un jeu de données propre et exploitable pour l'apprentissage automatique sans biais d'évaluation, un dédoublonnage strict en 3 phases a été appliqué :
- **Phase 1 (Empreinte binaire SHA-256) :** Détection et fusion de tous les doublons strictement identiques au bit près (ex. paires identiques dans `dataset_tables_ensemble` et entre `images` et `unverified_downloads`).
- **Phase 2 (URL & Identifiant source identique) :** Détection et fusion des photos issues d'une même ressource Wikimedia/Unsplash téléchargée à plusieurs reprises sous des noms différents.
- **Phase 3 (Conversions inter-formats) :** Élimination des doublons recompressés (ex. PNG vs JPEG pour les mêmes scènes).

| Métrique de dédoublonnage | Valeur |
| :--- | :---: |
| **Total de photos brutes analysées** | **{total_source}** |
| 🔄 **Doublons redondants détectés et éliminés** | **{total_dups_count}** |
| ✨ **Photos uniques canoniques classées** | **{total_uniques}** |

Chaque photo unique n'est présente qu'une seule et unique fois dans l'arborescence des classes. Le fichier [`classification_complete.csv`](classification_complete.csv) consigne l'ensemble des {total_source} fichiers d'origine avec le lien précis vers leur fichier canonique retenu.

---

## 2. Résumé de la Répartition des Classes

Sur les **{total_uniques} photos uniques retenues** :
- **{total_retenues} photos exploitables** pour l'entraînement et l'évaluation des modèles ML.
- **{total_elim} photos éliminées** (hors périmètre / non concernées).

| Dossier de classe | Description & Critères | Nombre de photos uniques |
| :--- | :--- | :---: |
| 🪑 **`1_table_vide_et_clean`** | **Tables vides et propres** : tables dressées, nappées ou nues, prêtes pour le service sans clients attablés ni vaisselle sale. | **{class_counts['1_table_vide_et_clean']}** |
| 👥 **`2_table_avec_personnes`** | **Tables occupées / avec personnes** : clients attablés, repas de famille, groupes déjeunant ou buvant un café. | **{class_counts['2_table_avec_personnes']}** |
| 🍽️ **`3_table_vide_et_non_clean`** | **Tables vides et non débarrassées (sales)** : tables sans personnes assises comportant de la vaisselle usagée, assiettes sales, verres vides, serviettes froissées ou restes de repas non débarrassés. | **{class_counts['3_table_vide_et_non_clean']}** |
| 🏬 **`4_tables_melanges`** | **Espaces multi-tables & états mixtes** : grands espaces de restauration (food courts, cafétérias collectives, réfectoires, banquets, terrasses vastes) présentant simultanément plusieurs typologies de mobilier et des états mixtes (tables occupées et libres, tables propres et tables à débarrasser). | **{class_counts['4_tables_melanges']}** |
| 🚫 **`images_eliminees_non_concernees`** | **Photos hors périmètre / éliminées** : éléments architecturaux isolés (plafonds à caissons), cybercafés avec ordinateurs, étals marchands sans places assises, gravures du 19e siècle, salles historiques de musées (Mount Vernon, Palais Royal) et stations de lavage des mains. | **{class_counts['images_eliminees_non_concernees']}** |
| **TOTAL UNIQUE** | | **{total_uniques}** |

---

## 3. Origine des Photos par Répertoire Source

| Dossier source | Photos brutes | Doublons éliminés | Photos uniques conservées |
| :--- | :---: | :---: | :---: |
| `dataset_tables_ensemble/images` | 415 | 58 | 357 |
| `collection_photos_cafes_restaurants/images` | 400 | 0 | 400 |
| `collection_photos_cafes_restaurants/unverified_downloads` | 8 | 4 | 4 |
| `foh-table-detection-yolov8/train/images` | 102 | 0 | 102 |
| `foh-table-detection-yolov8/valid/images` | 27 | 0 | 27 |
| `foh-table-detection-yolov8/test/images` | 14 | 0 | 14 |
| **Total Général** | **{total_source}** | **{total_dups_count}** | **{total_uniques}** |

---

## 4. Nomenclature des Fichiers dans les Classes

Afin d'éviter toute collision de noms et de permettre une traçabilité directe vers le répertoire d'origine :
- `ens_*` : issu de `dataset_tables_ensemble`
- `col_*` : issu de `collection_photos_cafes_restaurants/images`
- `unv_*` : issu de `unverified_downloads`
- `yolo_train_*` : issu du split d'entraînement YOLOv8
- `yolo_valid_*` : issu du split de validation YOLOv8
- `yolo_test_*` : issu du split de test YOLOv8

---

## 5. Critères d'Élimination Détaillés

Les {total_elim} photos classées dans `images_eliminees_non_concernees` ont été écartées pour des motifs objectifs de pertinence opérationnelle :
- **Plafonds et éléments de structure isolés :** ex. `commons_table_0020.jpg` (undertak).
- **Postes informatiques / Cybercafés :** ex. `commons_table_0024.jpg` (ordinateurs de bureau et claviers, pas de restauration).
- **Étalages marchands et boutiques :** ex. `commons_table_0032.jpg` (présentoirs de friandises sans tables pour dîner).
- **Gravures et documents d'archives d'époque :** ex. `commons_table_0045.jpg` (illustrations 1894).
- **Salles historiques de musées cordonnées :** ex. `commons_table_0041.jpg` (Palacio Real), `commons_table_0055/0056` (Bunge Museum Gotland), `commons_table_0103/0105/0107/0109/0111` (Mount Vernon State Dining Room).
- **Infrastructures d'accès et d'hygiène :** ex. `commons_table_0097.jpg` (station de désinfection des mains), `table_ensemble_345` (couloir d'accès).
- **Sculptures artistiques :** ex. `table_ensemble_285` (œuvre d'art en forme de table non utilisable).

---

## 6. Structure Physique du Dossier

```text
dataset_tables_classes/
├── 1_table_vide_et_clean/               # {class_counts['1_table_vide_et_clean']} photos uniques
├── 2_table_avec_personnes/              # {class_counts['2_table_avec_personnes']} photos uniques
├── 3_table_vide_et_non_clean/           # {class_counts['3_table_vide_et_non_clean']} photos uniques
├── 4_tables_melanges/                   # {class_counts['4_tables_melanges']} photos uniques
├── images_eliminees_non_concernees/     # {class_counts['images_eliminees_non_concernees']} photos uniques
├── classification_complete.csv          # Manifeste complet des {total_source} fichiers bruts
└── README.md                            # Documentation détaillée et statistiques
```
"""

with open(README_FILE, 'w', encoding='utf-8') as f:
    f.write(readme_content)

print(f"README.md enregistré : {README_FILE}")
print("Opération terminée avec succès !")

