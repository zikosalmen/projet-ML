# projet-ML

Projet de Machine Learning et Computer Vision dédié à la détection, au suivi et à la classification opérationnelle de tables de restauration (cafés, restaurants, cantines et food courts).

## 📁 Architecture du Dépôt

- **`dataset_tables_classes/`** : Corpus complet consolidé et dédoublonné de **904 images uniques** classées sans redondance selon 4 états opérationnels (+ 1 dossier de filtrage d'images non concernées) :
  - `1_table_vide_et_clean/` (204 photos) : tables dressées, propres et libres.
  - `2_table_avec_personnes/` (409 photos) : tables occupées avec convives/clients.
  - `3_table_vide_et_non_clean/` (51 photos) : tables sans convives avec vaisselle usagée ou restes à débarrasser.
  - `4_tables_melanges/` (213 photos) : grands espaces multi-tables (cafétérias, food courts) avec configurations et états mixtes.
  - `images_eliminees_non_concernees/` (27 photos) : éléments hors périmètre (structures de plafonds, musées, étals sans tables).
  - `classification_complete.csv` : Manifeste exhaustif des 966 photos brutes d'origine et traçabilité des 62 doublons éliminés.
  - `README.md` : Documentation détaillée du dataset de classification.

- **`dataset_tables_ensemble/`** : Collection initiale de tables de restauration avec métadonnées enrichies (`dataset_metadata.csv`).

- **`foh-table-detection-yolov8/`** : Pipeline et jeu de données de détection d'objets (YOLOv8) annoté pour la détection de tables :
  - `train/`, `valid/`, `test/` : Splits d'entraînement au format YOLO avec annotations de boîtes englobantes (`clean`, `dirty`, `occupied`).
  - `collection_photos_cafes_restaurants/` : Images sources issues d'Open Images V7, Wikimedia Commons et Unsplash avec `sources.csv`.
  - `tools/` : Scripts d'automatisation, de collecte et de classification dédoublonnée.

---

## 🛠️ Utilisation et Entraînement

Pour entraîner le modèle de détection YOLOv8 :
```bash
cd foh-table-detection-yolov8
# Entraînement YOLOv8
yolo detect train data=data.yaml model=yolov8n.pt epochs=50 imgsz=640
```
