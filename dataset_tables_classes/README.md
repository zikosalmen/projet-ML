# Classification Complète et Filtrage Rigoureux des Images de Tables

Ce dossier regroupe et consolide l'ensemble exhaustif des photos de tables issues de **tous les répertoires du projet Machine Learning** :
1. `dataset_tables_ensemble/images` (**415 photos brutes**)
2. `foh-table-detection-yolov8/collection_photos_cafes_restaurants/images` (**400 photos brutes**)
3. `foh-table-detection-yolov8/collection_photos_cafes_restaurants/unverified_downloads` (**8 photos brutes**)
4. `foh-table-detection-yolov8/train/images` (**102 photos brutes**)
5. `foh-table-detection-yolov8/valid/images` (**27 photos brutes**)
6. `foh-table-detection-yolov8/test/images` (**14 photos brutes**)

**Total brut analysé : 966 photos.**

---

## 1. Dédoublonnage Rigoureux ("Sans Redondance")

Afin de garantir un jeu de données propre et exploitable pour l'apprentissage automatique sans biais d'évaluation, un dédoublonnage strict en 3 phases a été appliqué :
- **Phase 1 (Empreinte binaire SHA-256) :** Détection et fusion de tous les doublons strictement identiques au bit près (ex. paires identiques dans `dataset_tables_ensemble` et entre `images` et `unverified_downloads`).
- **Phase 2 (URL & Identifiant source identique) :** Détection et fusion des photos issues d'une même ressource Wikimedia/Unsplash téléchargée à plusieurs reprises sous des noms différents.
- **Phase 3 (Conversions inter-formats) :** Élimination des doublons recompressés (ex. PNG vs JPEG pour les mêmes scènes).

| Métrique de dédoublonnage | Valeur |
| :--- | :---: |
| **Total de photos brutes analysées** | **966** |
| 🔄 **Doublons redondants détectés et éliminés** | **62** |
| ✨ **Photos uniques canoniques classées** | **904** |

Chaque photo unique n'est présente qu'une seule et unique fois dans l'arborescence des classes. Le fichier [`classification_complete.csv`](classification_complete.csv) consigne l'ensemble des 966 fichiers d'origine avec le lien précis vers leur fichier canonique retenu.

---

## 2. Résumé de la Répartition des Classes

Sur les **904 photos uniques retenues** :
- **877 photos exploitables** pour l'entraînement et l'évaluation des modèles ML.
- **27 photos éliminées** (hors périmètre / non concernées).

| Dossier de classe | Description & Critères | Nombre de photos uniques |
| :--- | :--- | :---: |
| 🪑 **`1_table_vide_et_clean`** | **Tables vides et propres** : tables dressées, nappées ou nues, prêtes pour le service sans clients attablés ni vaisselle sale. | **204** |
| 👥 **`2_table_avec_personnes`** | **Tables occupées / avec personnes** : clients attablés, repas de famille, groupes déjeunant ou buvant un café. | **409** |
| 🍽️ **`3_table_vide_et_non_clean`** | **Tables vides et non débarrassées (sales)** : tables sans personnes assises comportant de la vaisselle usagée, assiettes sales, verres vides, serviettes froissées ou restes de repas non débarrassés. | **51** |
| 🏬 **`4_tables_melanges`** | **Espaces multi-tables & états mixtes** : grands espaces de restauration (food courts, cafétérias collectives, réfectoires, banquets, terrasses vastes) présentant simultanément plusieurs typologies de mobilier et des états mixtes (tables occupées et libres, tables propres et tables à débarrasser). | **213** |
| 🚫 **`images_eliminees_non_concernees`** | **Photos hors périmètre / éliminées** : éléments architecturaux isolés (plafonds à caissons), cybercafés avec ordinateurs, étals marchands sans places assises, gravures du 19e siècle, salles historiques de musées (Mount Vernon, Palais Royal) et stations de lavage des mains. | **27** |
| **TOTAL UNIQUE** | | **904** |

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
| **Total Général** | **966** | **62** | **904** |

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

Les 27 photos classées dans `images_eliminees_non_concernees` ont été écartées pour des motifs objectifs de pertinence opérationnelle :
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
├── 1_table_vide_et_clean/               # 204 photos uniques
├── 2_table_avec_personnes/              # 409 photos uniques
├── 3_table_vide_et_non_clean/           # 51 photos uniques
├── 4_tables_melanges/                   # 213 photos uniques
├── images_eliminees_non_concernees/     # 27 photos uniques
├── classification_complete.csv          # Manifeste complet des 966 fichiers bruts
└── README.md                            # Documentation détaillée et statistiques
```
