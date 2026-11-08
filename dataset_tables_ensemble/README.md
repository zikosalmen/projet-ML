# Dataset d'Ensembles de Tables (Cafés, Restaurants, Espaces Familiaux)

Ce dossier regroupe un jeu complet de plus de **400 photographies** (exactement **415 images**) soigneusement sélectionnées et téléchargées :
**Des photos de cafés (tables de café), de restaurants et d'espaces familiaux présentant un « ensemble de tables » (plusieurs tables visibles dans chaque scène)** pour la vision par ordinateur et la détection d'objets (YOLOv8).

---

## 1. Résumé du Dataset

- **Nombre total d'images :** 415 images (dépasse le minimum de 400 demandé)
- **Poids total :** ~160.27 Mo
- **Format :** JPEG standardisé (qualité 85, dimensions max 1600 px)
- **Objectif visuel :** Présence de **plusieurs tables simultanées** (rangées de tables, terrasses, tables intérieures, espaces repas familiaux, food courts, cafétérias).

### Répartition par catégorie

| Catégorie | Description | Nombre d'images |
| :--- | :--- | :---: |
| `cafe_terrasse` | Terrasses extérieures, tables de trottoir, salons de café et coffee shops | 168 |
| `restaurant_interieur` | Salles à manger, bistrots contemporains, alignements de tables intérieures | 150 |
| `espace_familial` | Food courts, cafétérias, espaces buffet et grandes salles familiales | 97 |
| **Total** | | **415** |

### Répartition par plateforme source

| Plateforme | Nombre d'images | Statut d'accès & Licence |
| :--- | :---: | :--- |
| **Wikimedia Commons (Wikipedia)** | 400 | Accès libre API, licences CC-BY, CC-BY-SA, CC0 et Domaine Public avec attribution. |
| **Unsplash** | 15 | Téléchargement direct HD, photographies professionnelles sous Unsplash License / CC0. |

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
│   └── table_ensemble_415_espace_familial.jpg
├── dataset_metadata.csv   # Tableau complet des métadonnées (ID, auteur, licence, URL, résolution)
└── README.md              # Cette documentation
```

---

## 4. Aperçu des métadonnées (échantillon)

| ID | Fichier | Catégorie | Source | Licence | Résolution |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `IMG_001` | `table_ensemble_001_restaurant_interieur.jpg` | `restaurant_interieur` | Unsplash | Unsplash License | 1600x1117 |
| `IMG_002` | `table_ensemble_002_restaurant_interieur.jpg` | `restaurant_interieur` | Unsplash | Unsplash License | 1600x1067 |
| `IMG_003` | `table_ensemble_003_restaurant_interieur.jpg` | `restaurant_interieur` | Unsplash | Unsplash License | 1600x1200 |
| `IMG_004` | `table_ensemble_004_cafe_terrasse.jpg` | `cafe_terrasse` | Unsplash | Unsplash License | 1600x1097 |
| `IMG_005` | `table_ensemble_005_cafe_terrasse.jpg` | `cafe_terrasse` | Unsplash | Unsplash License | 1600x1200 |
| `IMG_006` | `table_ensemble_006_cafe_terrasse.jpg` | `cafe_terrasse` | Unsplash | Unsplash License | 1600x1067 |
| `IMG_007` | `table_ensemble_007_restaurant_interieur.jpg` | `restaurant_interieur` | Unsplash | Unsplash License | 1200x1600 |
| `IMG_008` | `table_ensemble_008_restaurant_interieur.jpg` | `restaurant_interieur` | Unsplash | Unsplash License | 1600x1067 |
| `IMG_009` | `table_ensemble_009_espace_familial.jpg` | `espace_familial` | Unsplash | Unsplash License | 1200x1600 |
| `IMG_010` | `table_ensemble_010_espace_familial.jpg` | `espace_familial` | Unsplash | Unsplash License | 1600x1067 |
| `IMG_011` | `table_ensemble_011_espace_familial.jpg` | `espace_familial` | Unsplash | Unsplash License | 1600x1068 |
| `IMG_012` | `table_ensemble_012_cafe_terrasse.jpg` | `cafe_terrasse` | Unsplash | Unsplash License | 1066x1600 |

*(Consultez `dataset_metadata.csv` pour la liste exhaustive des 415 photos avec liens directs et attributions).*

---

## 5. Utilisation pour l'entraînement YOLOv8

1. Les images ont été redimensionnées avec un ratio d'aspect préservé à un maximum de 1600 px (idéal pour l'entraînement à 640×640 ou 1280×1280 sous YOLOv8).
2. Toutes les images présentent **plusieurs tables**, ce qui permet d'annoter plusieurs boîtes englobantes (`table`) par photo, que ce soit pour les classes `clean`, `dirty` ou `occupied`.
