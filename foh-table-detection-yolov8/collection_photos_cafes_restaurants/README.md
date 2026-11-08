# Collection de photos — cafés, restaurants et espaces familiaux

Le dossier `images/` contient **400 photos**. Le fichier [`sources.csv`](sources.csv) contient une ligne de provenance pour chaque photo.

| Source | Photos |
|---|---:|
| Open Images V7 — split validation | 326 |
| Wikimedia Commons | 68 |
| Unsplash | 6 |
| **Total** | **400** |

Les 326 images Open Images retenues ont toutes une boîte d’objet `Table` dans les annotations du split validation. La sélection privilégie les scènes annotées comme restaurant, salle à manger, repas, buffet ou café; elle inclut aussi des tables en espaces intérieurs et familiaux pour varier les exemples. Les pages Flickr d’origine, auteurs, titres, licences indiquées, identifiants Open Images et URL de téléchargement figurent dans `sources.csv`.

## Utilisation dans le projet

Cette collection reste séparée des dossiers YOLO `train`, `valid` et `test`. Les photos ne sont pas encore intégrées à l’entraînement. La colonne `table_box_labels` indique la classe de table présente dans les annotations Open Images; les fichiers d’annotation YOLO du projet ne sont pas modifiés.

## Provenance et droits

- Open Images V7 indique une licence CC BY 2.0 pour les images. Sa documentation recommande de vérifier les droits sur la page source de chaque photo; ces pages sont conservées dans `sources.csv`.
- Pour les six images Unsplash, l’utilisateur a confirmé disposer d’une autorisation écrite couvrant l’utilisation en machine learning. Cette autorisation distincte accompagne l’utilisation de ces fichiers.
- Les licences des images Wikimedia Commons sont renseignées individuellement dans `sources.csv`; respecter les conditions d’attribution indiquées.
- Huit téléchargements Commons sans métadonnées de provenance récupérables restent dans `unverified_downloads/`. Ils sont exclus du total de 400 et du dossier `images/`.

## Références

- [Open Images V7 — téléchargement et format](https://storage.googleapis.com/openimages/web/download_v7.html)
- [Open Images V7 — licence et précisions sur les droits](https://storage.googleapis.com/openimages/web/factsfigures_v7.html)
- [Wikimedia Commons](https://commons.wikimedia.org/)
- [Unsplash](https://unsplash.com/)
