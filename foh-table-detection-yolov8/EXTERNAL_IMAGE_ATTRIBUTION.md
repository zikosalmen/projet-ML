# Provenance des images ajoutées

Ajout du 7 novembre 2026. Six images ont été placées dans train/images; leur boîte et leur classe YOLO sont dans le fichier homonyme de train/labels. Les coordonnées désignent la table visible. Les photos restent dans le split train afin de garder validation et test inchangés.

| Image | Classe | Source et auteur | Licence indiquée | Rendu installé |
| --- | --- | --- | --- | --- |
| external_unsplash_clean_001.jpg | clean | [Unsplash — Jonas Jacobsson](https://unsplash.com/photos/empty-brown-wooden-restaurant-table-with-chairs-1iTKoFJvJ6E) | Unsplash License; utilisation ML fondée sur l’autorisation écrite confirmée par l’utilisateur | [1600 px](https://images.unsplash.com/photo-1525193612562-0ec53b0e5d7c?fm=jpg&w=1600&q=85) |
| external_unsplash_dirty_001.jpg | dirty | [Unsplash — tommao wang](https://unsplash.com/photos/dirty-dishes-and-glasses-on-a-wooden-table-vQR2SlPSu1c) | Unsplash License; utilisation ML fondée sur l’autorisation écrite confirmée par l’utilisateur | [1600 px](https://images.unsplash.com/photo-1756395080881-a6e83b582509?fm=jpg&w=1600&q=85) |
| external_unsplash_occupied_001.jpg | occupied | [Unsplash — Johan Mouchet](https://unsplash.com/photos/woman-sitting-at-cafe-table-with-coffee-and-phone-ttdlQ0Wgrp8/) | Unsplash License; utilisation ML fondée sur l’autorisation écrite confirmée par l’utilisateur | [1600 px](https://images.unsplash.com/photo-1759050498232-967c4ee40cdb?fm=jpg&w=1600&q=85) |
| external_commons_clean_001.jpg | clean | [Wikimedia Commons — Mattes](https://commons.wikimedia.org/wiki/File:Table_setting_in_a_restaurant.JPG) | Domaine public, dédicace de l’auteur | [Original](https://upload.wikimedia.org/wikipedia/commons/1/17/Table_setting_in_a_restaurant.JPG) |
| external_commons_dirty_001.jpg | dirty | [Wikimedia Commons — Nenad Stojković, publié par Shixart1985](https://commons.wikimedia.org/wiki/File:Dining_experience_concludes_with_a_plate_left_behind_featuring_remnants_of_a_delicious_meal_at_a_table_undefined.jpg) | CC BY 2.0 | [Rendu 1280 px](https://thumb.wikimedia.org/wikipedia/commons/thumb/4/45/Dining_experience_concludes_with_a_plate_left_behind_featuring_remnants_of_a_delicious_meal_at_a_table_undefined.jpg/1280px-Dining_experience_concludes_with_a_plate_left_behind_featuring_remnants_of_a_delicious_meal_at_a_table_undefined.jpg) |
| external_commons_occupied_001.jpg | occupied | [Wikimedia Commons — rawpixel.com](https://commons.wikimedia.org/wiki/File:Meeting_at_the_Cafe_%28Unsplash%29.jpg) | CC0 1.0; Commons indique une publication Unsplash antérieure au 5 juin 2017 | [Rendu 1280 px](https://thumb.wikimedia.org/wikipedia/commons/thumb/8/85/Meeting_at_the_Cafe_%28Unsplash%29.jpg/1280px-Meeting_at_the_Cafe_%28Unsplash%29.jpg) |

## Notes d’utilisation

- Les pages Unsplash affichent leur licence de plateforme, mais l’ajout à l’entraînement ML repose sur l’autorisation écrite que l’utilisateur dit détenir. L’autorisation n’a pas été copiée dans le dépôt; le manifeste indique cette attestation et précise que son document n’a pas été fourni.
- Pour la photo CC BY 2.0, conserver le crédit « Nenad Stojković » et un lien vers la licence; l’image a été réduite à 1280 px et annotée.
- Les rendus Commons CC0 et domaine public n’imposent pas d’attribution, mais les crédits sont conservés pour retracer la source.
- Les six boîtes ont été annotées manuellement au format YOLO, une boîte par photo. Les photos sont des scènes de stock et de photographie de restauration, avec des angles plus rapprochés que la majorité des images de surveillance du dataset.
