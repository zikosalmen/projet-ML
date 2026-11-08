# Agrandir et diversifier le dataset

## État du jeu actuel

| Indicateur | État observé |
| --- | --- |
| Images | 143 : 102 train, 27 validation, 14 test |
| Instances annotées | clean 201 (36,3 %), dirty 194 (35,1 %), occupied 158 (28,6 %) |
| Format | Détection YOLO : une boîte par table et une classe par boîte |
| Déduplication initiale | 0 copie binaire exacte; 332 paires candidates pHash au seuil ≤ 4, dont 122 entre splits |

### Analyse visuelle

Échantillon regardé : 18 images, six par split.

| Aspect | Observations |
| --- | --- |
| Tables et cadrage | Surtout tables rectangulaires ou carrées, souvent en bois foncé; plans larges de salle et quelques cadrages rapprochés en plongée. |
| Angle | Vue de caméra haute/oblique, parfois presque zénithale; scènes de surveillance fixes qui couvrent plusieurs tables. |
| Éclairage | Intérieurs majoritairement chauds et assez sombres; quelques scènes plus claires à lumière froide. Ombres et reflets présents. |
| Objets | Assiettes avec restes, couverts, verres, tasses, serviettes, plateaux; quelques personnes et chaises visibles. |
| Qualité | 108 images en 1920×1080, 20 en 1024×1024, 9 dans d’autres tailles; certains exemples ont incrustation d’horodatage/logo et compression CCTV. |
| Variations à ajouter | Terrasses/jour, tables rondes et matériaux clairs, vue client à hauteur des yeux, faible luminosité extrême, occlusions, objets seuls et tables presque propres. |

Le dataset sert donc déjà à classer **chaque table dans une scène** via une boîte YOLO. Si l’objectif devient une seule image par table, il faudra recadrer les boîtes, puis entraîner un classifieur sur les crops.

La répartition des instances est assez proche entre les trois classes; `occupied` est la plus basse. La priorité est d’augmenter la diversité des conditions, sans suréchantillonner artificiellement. Ajouter des photos de stock très propres peut créer un biais de domaine; privilégier des scènes réalistes et garder les nouveaux angles dans les trois classes.

| Classe | Train | Validation | Test | Total | Part |
| --- | ---: | ---: | ---: | ---: | ---: |
| clean | 151 | 34 | 16 | 201 | 36,3 % |
| dirty | 123 | 39 | 32 | 194 | 35,1 % |
| occupied | 117 | 29 | 12 | 158 | 28,6 % |

## Sources à privilégier

| Rang | Source et meilleure requête | Licence à vérifier | Téléchargement et limites |
| --- | --- | --- | --- |
| 1 | [Roboflow Universe](https://universe.roboflow.com/) — `restaurant table clean dirty occupied`, `cafe table CCTV` | Licence affichée pour **chaque projet**. Le `data.yaml` de cet export déclare MIT au niveau du projet; cela ne remplace pas la vérification de la provenance des fichiers image. | Télécharger le projet/version en format YOLOv8 depuis Universe ou utiliser le SDK Roboflow. Vérifier les conditions du projet avant d’importer ses images. |
| 2 | [Open Images V7](https://storage.googleapis.com/openimages/web/download_v7.html) — `Table`, puis filtrer manuellement les scènes café/restaurant | Les images sont répertoriées en CC BY 2.0 et les annotations Open Images en CC BY 4.0. Vérifier la page source et conserver l’auteur, la licence et le lien de chaque image. | [FiftyOne](https://docs.voxel51.com/dataset_zoo/datasets/open_images_v7.html) permet de limiter par classe et par nombre d’images; le téléchargeur officiel permet de récupérer une liste d’IDs. Les labels d’objets ne donnent pas directement `clean/dirty/occupied`, donc annoter ces classes à nouveau. |
| 3 | [Kaggle Datasets](https://www.kaggle.com/datasets) — `restaurant table detection YOLO`, `cafe CCTV table dataset` | Variable selon le dataset et ses sources. N’utiliser que si la licence et les droits des images sources sont indiqués et compatibles; « public » ne veut pas dire libre. | Le [CLI officiel](https://github.com/Kaggle/kaggle-cli/blob/main/docs/datasets.md) liste et télécharge les datasets : `kaggle datasets list -s "restaurant table"`, puis `kaggle datasets download -d propriétaire/slug`. Lire la licence affichée sur la fiche. |
| 4 | [Wikimedia Commons](https://commons.wikimedia.org/) — `restaurant dining table`, `cafe terrace table` | Licence au niveau du fichier : CC BY, CC BY-SA ou domaine public notamment. Vérifier l’auteur, la version de licence et les obligations de partage à l’identique. | Recherche manuelle ou [API MediaWiki](https://commons.wikimedia.org/wiki/Commons%3AREUSE); enregistrer la page du fichier et les informations de licence. Bon pour diversifier les scènes, moins pour les images CCTV. |
| 5 | [Flickr](https://www.flickr.com/) — `restaurant table overhead`, filtre de licence CC | Licence au niveau de chaque photo; les permissions de l’API ne remplacent pas celles du photographe. | L’API [`flickr.photos.search`](https://www.flickr.com/services/api/flickr.photos.search.htm) filtre par licence et retourne des métadonnées. Ses [conditions API](https://www.flickr.com/help/terms/api) limitent le stockage/cache des photos; ne pas constituer un corpus d’entraînement avec des téléchargements API sans vérifier les conditions ou obtenir l’autorisation requise. |

### Pinterest, Unsplash et autres plateformes à conditions particulières

| Source | Motif |
| --- | --- |
| [Pinterest](https://policy.pinterest.com/en/terms-of-service) | Une épingle n’est pas une licence d’image. Les conditions interdisent l’accès automatisé non autorisé; les conditions développeur interdisent l’usage des données Pinterest pour ML sans consentement écrit préalable de Pinterest. Utiliser seulement les URLs/fichiers couverts par l’autorisation et par les droits du photographe; pas de scraping global. |
| [Unsplash classique](https://unsplash.com/terms) | La licence générale des images ne couvre pas les datasets ML. Unsplash a un [programme de dataset séparé](https://unsplash.com/data) : Lite (25 000 images) et Full (accès sur demande, non-commercial); les conditions régissent l’usage d’entraînement et interdisent la redistribution des images. Utiliser ce programme ou une autorisation écrite qui couvre explicitement les images visées. |
| [Pexels](https://help.pexels.com/hc/en-us/articles/900005880463-What-are-the-Terms-and-Conditions) | La collecte à grande échelle via API pour entraîner, évaluer ou développer des datasets ML/IA nécessite une autorisation explicite. |
| [Pixabay](https://pixabay.com/service/terms/) | Les collectes automatisées pour ML et les copies systématiques/grande échelle sont interdites sans permission explicite. |

Tu as indiqué disposer d’une autorisation écrite pour Pinterest/Unsplash. Pour chaque image correspondante, conserve dans le manifeste le lien direct, l’auteur, la licence et une référence à l’autorisation, avec son périmètre (copie locale, entraînement, partage éventuel). Une autorisation sur une photo ne vaut pas autorisation générale sur toute la plateforme.

## Première extension importée — 7 novembre 2026

Six photos ont été ajoutées à train/images avec une annotation YOLO manuelle dans train/labels : deux par classe (clean, dirty, occupied). Trois viennent d’Unsplash et trois de Wikimedia Commons. Les splits validation et test restent inchangés. Les pages sources, les auteurs, les licences et les rendus utilisés sont consignés dans [EXTERNAL_IMAGE_ATTRIBUTION.md](EXTERNAL_IMAGE_ATTRIBUTION.md) et dans dataset_manifest.csv.

Les images Unsplash sont marquées comme reposant sur l’autorisation écrite que tu as confirmée dans cette conversation. Le document de cette autorisation n’est pas joint au projet; son périmètre exact doit correspondre aux photos concernées. Les fichiers Commons sont crédités selon la licence indiquée sur leur page.

Éviter les images CCTV mises en ligne sans preuve de droits, même si elles ressemblent fortement au dataset. Pour les visages visibles, flouter les personnes avant de partager des données de recherche lorsque cela est nécessaire.

## Requêtes de recherche

À utiliser comme requêtes de découverte, puis contrôler la licence de chaque image ou dataset avant téléchargement.

| Groupe | Français | English | العربية | Cible |
| --- | --- | --- | --- | --- |
| Similaire | caméra surveillance restaurant table | restaurant CCTV table view | كاميرا مراقبة مطعم طاولة | Vue haute intérieure |
| Similaire | vidéosurveillance salle de café | indoor cafe security camera footage | كاميرات مراقبة مقهى داخلي | Scène de salle |
| Similaire | tables restaurant vue plongeante | high angle restaurant dining tables | طاولات مطعم زاوية علوية | Angle proche du dataset |
| Similaire | clients assis à table café | cafe customers seated at table | زبائن جالسون على طاولة مقهى | Occupée |
| Similaire | table propre débarrassée restaurant | clean empty restaurant table | طاولة مطعم نظيفة وفارغة | Propre |
| Similaire | vaisselle sale sur table restaurant | dirty dishes on restaurant table | أطباق متسخة على طاولة مطعم | Sale |
| Similaire | tables de fast-food vue haute | fast food tables overhead view | طاولات مطعم وجبات سريعة من الأعلى | Plateaux et fast-food |
| Similaire | salle de restaurant vide tables propres | empty dining room clean tables | قاعة طعام فارغة وطاولات نظيفة | Plusieurs tables |
| Similaire | table de brasserie après le repas | bistro table after a meal | طاولة مطعم بعد تناول الطعام | Restes réalistes |
| Similaire | salle à manger restaurant vue de dessus | restaurant dining room elevated view | قاعة مطعم من زاوية مرتفعة | Vue globale |
| Diversification | table terrasse café soleil | outdoor cafe terrace table sunlight | طاولة مقهى خارجية تحت الشمس | Lumière naturelle |
| Diversification | table ronde en bois café vue haute | round wooden cafe table high angle | طاولة مقهى خشبية مستديرة من الأعلى | Forme ronde |
| Diversification | table bistrot en marbre | marble bistro table | طاولة مقهى رخامية | Matériau et reflets |
| Diversification | table haute de bar mange-debout | high bar table with stools | طاولة بار مرتفعة مع مقاعد | Mange-debout |
| Diversification | table restaurant vue zénithale | restaurant table top-down view | طاولة مطعم من الأعلى مباشرة | Vue 90° |
| Diversification | clients à une table de terrasse café | people sitting at an outdoor cafe table | أشخاص يجلسون على طاولة مقهى خارجية | Occupée dehors |
| Diversification | table en verre restaurant moderne | glass table in a modern restaurant | طاولة زجاجية في مطعم حديث | Transparence |
| Diversification | table restaurant partiellement cachée chaise | restaurant table partially occluded by chair | طاولة مطعم محجوبة جزئياً بكرسي | Occlusion |
| Diversification | terrasse café couverte temps couvert | covered cafe patio overcast weather | شرفة مقهى مغطاة في طقس غائم | Lumière diffuse |
| Diversification | table cafétéria universitaire plateaux | university cafeteria table food trays | طاولة كافتيريا جامعية وصواني طعام | Food court |
| Cas difficile | table café avec un téléphone seul | cafe table with only one smartphone | طاولة مقهى عليها هاتف فقط | Téléphone seul |
| Cas difficile | sac posé sur chaise près d'une table | bag on chair next to restaurant table | حقيبة على كرسي بجانب طاولة مطعم | Réservée ou libre |
| Cas difficile | table avec miettes et serviette froissée | table with crumbs and crumpled napkin | طاولة عليها فتات ومنديل مجعد | Limite propre/sale |
| Cas difficile | un seul verre vide sur table café | single empty glass on cafe table | كأس فارغ واحد على طاولة مقهى | Vaisselle minimale |
| Cas difficile | reflets néon sur table restaurant | neon glare on restaurant table | انعكاس ضوء النيون على طاولة مطعم | Reflets |
| Cas difficile | table café dans bar sombre | cafe table in a dimly lit bar | طاولة مقهى في حانة خافتة الإضاءة | Faible luminosité |
| Cas difficile | table propre avec auréole de café | clean table with a coffee ring | طاولة نظيفة عليها أثر فنجان قهوة | Trace ambiguë |
| Cas difficile | client debout près de sa table | customer standing next to their table | زبون واقف بجانب طاولته | Occupation limite |
| Cas difficile | ordinateur portable ouvert sur table café | open laptop on a cafe table | حاسوب محمول مفتوح على طاولة مقهى | Coworking |
| Cas difficile | table dressée avec couverts sans repas | set table with cutlery but no food | طاولة مجهزة بأدوات المائدة دون طعام | Propre mais non vide |

## Règles d’acquisition et d’annotation

1. Définir la classe par **état du plateau**, pas par le décor : `occupied` si une personne utilise la table; un téléphone ou un sac seuls ne suffisent pas. `dirty` si des traces ou restes de repas indiquent qu’elle doit être débarrassée; `clean` si elle est prête à être réutilisée, même avec un dressage propre. Mettre les cas ambigus en revue humaine.
2. Avant d’annoter, inscrire la source, URL originale, auteur, licence exacte, URL de licence, date de collecte et empreinte dans `dataset_manifest.csv`.
3. Dessiner une boîte autour du plateau de chaque table et appliquer les mêmes règles aux tables partiellement masquées ou coupées. Ne pas déduire l’état d’une table à partir de la classe majoritaire de l’image.
4. Dédupliquer par SHA-256 pour les copies exactes et par pHash pour les quasi-doublons. Les distances pHash de 0 à 4 sont des candidates à revoir, pas une preuve qu’il faut supprimer une image. Le script ne supprime rien.
5. Faire les splits par vidéo, caméra, lieu ou session avant d’extraire des frames, pour éviter que des images presque identiques se retrouvent dans train et test. Le test doit rester intact jusqu’à l’évaluation finale.
6. Viser un nombre comparable d’instances par classe et par type de scène. Les transformations (contraste, légère rotation, recadrage) ne s’appliquent qu’au train; elles ne remplacent pas de nouvelles conditions de prise de vue.
7. Ne pas utiliser un seuil global de netteté comme `Var(Laplacian) < 100` pour supprimer automatiquement : le résultat dépend de la résolution, de la texture et de la compression. Utiliser cette mesure comme alerte à vérifier visuellement.

## Outils dans ce dossier

- `tools/dataset_quality.py` génère ou met à jour `dataset_manifest.csv` et compare les images entre tous les splits avec un pHash 64 bits (seuil par défaut : distance de Hamming ≤ 4).
- `phash_duplicates.csv` liste les paires candidates à contrôler. Le script ne supprime ni ne déplace les images.
- Le premier passage n’a trouvé aucune copie binaire exacte, mais a signalé 122 paires pHash entre train/validation/test. Certaines appartiennent aux fichiers `extra_*.jpg`; cela peut signaler des frames de la même vidéo réparties entre splits. Confirmer les groupes par vidéo/session, puis refaire les splits avant de mesurer le modèle. Une proximité pHash seule ne suffit pas à déclarer deux images doublons.
- Le manifeste conserve les champs de provenance déjà remplis lors d’une nouvelle exécution, dont `authorization_reference` et `authorization_scope`. Les images actuelles sont marquées `UNVERIFIED`, car l’export déclare une licence de projet mais ne donne pas ici la provenance individuelle de chaque image.
- Les chemins de `data.yaml` sont relatifs au dossier du dataset et pointent maintenant vers `train/images`, `valid/images` et `test/images`.

Depuis ce dossier :

```powershell
python tools/dataset_quality.py
```

Le script utilise OpenCV et NumPy, généralement installés avec l’environnement Ultralytics. Pour un autre jeu de données, passer son dossier avec `--root`.
