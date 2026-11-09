"""Collect 400 licensed indoor restaurant, cafe, and bar table photos from Commons.

Only Wikimedia Commons files with CC BY, CC BY-SA, CC0, or public-domain
licensing are considered. The script records attribution and rejects exact and
near-duplicate files against all images already present in this project.
"""

from __future__ import annotations

import csv
import hashlib
import html
import re
import sys
import time
from collections import deque
from datetime import datetime, timezone
from pathlib import Path

import cv2
import numpy as np
import requests
from PIL import Image


PROJECT_ROOT = Path(__file__).resolve().parents[2]
OUTPUT_ROOT = PROJECT_ROOT / "dataset_tables_interieurs_400"
STAGING_DIR = OUTPUT_ROOT / ".staging"
IMAGE_DIR = OUTPUT_ROOT / "images"
MANIFEST_PATH = OUTPUT_ROOT / "dataset_metadata.csv"
README_PATH = OUTPUT_ROOT / "README.md"
TARGET_TOTAL = 400
PHASH_THRESHOLD = 4
MAX_SIDE = 1600
USER_AGENT = "FOHTableDetectionIndoorCollection/1.0 (Wikimedia Commons reuse with source attribution)"


QUERIES: dict[str, dict[str, object]] = {
    "restaurant_interieur": {
        "target": 155,
        "roots": [
            ("Category:Interiors of restaurants", True, False),
            ("Category:Restaurant tables", False, True),
            ("Category:Dining rooms in restaurants", True, False),
            ("Category:Interiors of eating establishments", True, False),
        ],
    },
    "cafe_interieur": {
        "target": 142,
        "roots": [
            ("Category:Interiors of cafés", True, False),
            ("Category:Round tables in cafés", False, True),
            ("Category:Cafés", False, False),
        ],
    },
    "bar_interieur": {
        "target": 103,
        "roots": [
            ("Category:Interiors of bars", True, False),
            ("Category:Pub tables", False, True),
        ],
    },
}


OUTDOOR_RE = re.compile(
    r"\b(outdoors?|outside|terrace|terrasse|patio|street|sidewalk|garden|beach|"
    r"open[ -]air|market|plaza|park|courtyard|veranda|deck|waterfront|promenade|"
    r"rooftop|roof[ -]top|seaside|outdoor dining|pavement|pier)\b",
    re.IGNORECASE,
)
SKIP_CATEGORY_RE = re.compile(
    r"\b(kitchens?|bathrooms?|lighting|chandeliers?|furniture|people|portraits?|"
    r"art|paintings?|drawings?|logos?|refrigerators?|serving carts?|menus?|food|"
    r"counters?|cash registers?|architecture|construction|demolition|plans?|"
    r"television|tv sets?|fish tanks?|aquariums?|bookcases?|bookshelves?|bookstores?|"
    r"libraries|computer labs?|arcades?|gaming|classrooms?)\b",
    re.IGNORECASE,
)
BAD_CONTENT_RE = re.compile(
    r"\b(aquariums?|fish tanks?|television sets?|arcades?|video games?|bookstores?|"
    r"bookshops?|bookshelves?|bookcases?|libraries|computer labs?|restaurant kitchens?|"
    r"conference rooms?|classrooms?|museum galleries|paintings?|engravings?|mannequins?)\b",
    re.IGNORECASE,
)
INDOOR_RE = re.compile(
    r"\b(interiors?|inside|indoors?|room|dining room|dining hall|cafeteria|canteen|"
    r"interior view|banquet hall)\b",
    re.IGNORECASE,
)
TABLE_RE = re.compile(r"\b(tables?|tabletop|chairs?|seating|booths?|dining)\b", re.IGNORECASE)
VENUE_PATTERNS = {
    "restaurant_interieur": re.compile(
        r"\b(restaurant|bistro|diner|eatery|cafeteria|canteen|food hall|pizzeria|trattoria)\b",
        re.IGNORECASE,
    ),
    "cafe_interieur": re.compile(
        r"\b(cafe|café|coffee ?shop|coffee ?house|bakery|tea room)\b", re.IGNORECASE
    ),
    "bar_interieur": re.compile(
        r"\b(bar|pub|tavern|brewpub|wine bar|beer hall|nightclub)\b", re.IGNORECASE
    ),
}


def clean_markup(value: str) -> str:
    value = re.sub(r"<[^>]+>", " ", value or "")
    return re.sub(r"\s+", " ", html.unescape(value)).strip()


def allowed_license(name: str) -> bool:
    value = name.lower().strip()
    if not value or any(term in value for term in ("noncommercial", "non-commercial", "cc by-nc", "nd", "no derivatives")):
        return False
    if "cc0" in value or "public domain" in value or value.startswith("pd"):
        return True
    return bool(re.search(r"\bcc by(?:-sa)?(?:\s|$)", value))


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def perceptual_hash(image_path: Path) -> int:
    image = cv2.imread(str(image_path), cv2.IMREAD_GRAYSCALE)
    if image is None:
        raise ValueError(f"Image illisible : {image_path}")
    resized = cv2.resize(image, (32, 32), interpolation=cv2.INTER_AREA)
    coefficients = cv2.dct(np.float32(resized) / 255.0)[:8, :8].flatten()
    median = float(np.median(coefficients[1:]))
    result = 0
    for coefficient in coefficients:
        result = (result << 1) | int(coefficient > median)
    return result


def existing_hashes() -> tuple[set[str], list[int]]:
    exact: set[str] = set()
    perceptual: list[int] = []
    suffixes = {".jpg", ".jpeg", ".png", ".webp", ".bmp", ".tif", ".tiff"}
    output_resolved = OUTPUT_ROOT.resolve()
    paths = sorted(
        p for p in PROJECT_ROOT.rglob("*")
        if p.is_file() and p.suffix.lower() in suffixes
        and not p.resolve().is_relative_to(output_resolved)
    )
    if IMAGE_DIR.exists():
        paths.extend(sorted(p for p in IMAGE_DIR.iterdir() if p.is_file() and p.suffix.lower() in suffixes))
    print(f"Comparaison avec {len(paths)} images déjà présentes dans le projet…", flush=True)
    for index, path in enumerate(paths, 1):
        try:
            exact.add(sha256(path))
            perceptual.append(perceptual_hash(path))
        except Exception as error:
            print(f"Image existante ignorée ({path.name}) : {error}", flush=True)
        if index % 300 == 0:
            print(f"  {index}/{len(paths)} images comparées", flush=True)
    return exact, perceptual


def commons_search(session: requests.Session, term: str) -> list[dict[str, object]]:
    endpoint = "https://commons.wikimedia.org/w/api.php"
    params = {
        "action": "query",
        "maxlag": 5,
        "generator": "search",
        "gsrsearch": term,
        "gsrnamespace": 6,
        "gsrlimit": 50,
        "prop": "imageinfo",
        "iiprop": "url|size|extmetadata",
        "iiurlwidth": MAX_SIDE,
        "format": "json",
    }
    payload = None
    for attempt in range(5):
        response = session.get(endpoint, params=params, timeout=30)
        if response.status_code in (429, 503):
            retry_after = response.headers.get("Retry-After", "")
            try:
                delay = max(5.0, float(retry_after))
            except ValueError:
                delay = min(60.0, 5.0 * (2**attempt))
            print(f"Commons ralentit les requêtes; nouvelle tentative dans {delay:g} s…", flush=True)
            time.sleep(delay)
            continue
        response.raise_for_status()
        payload = response.json()
        break
    if payload is None:
        raise RuntimeError("Limite de requêtes Commons persistante après plusieurs reprises.")
    pages = payload.get("query", {}).get("pages", {}).values()
    return list(pages)


def commons_category_members(
    session: requests.Session, category_title: str
) -> tuple[list[dict[str, object]], list[str]]:
    endpoint = "https://commons.wikimedia.org/w/api.php"
    params: dict[str, str | int] = {
        "action": "query",
        "maxlag": 5,
        "generator": "categorymembers",
        "gcmtitle": category_title,
        "gcmtype": "file|subcat",
        "gcmlimit": 500,
        "prop": "imageinfo",
        "iiprop": "url|size|extmetadata",
        "iiurlwidth": MAX_SIDE,
        "format": "json",
    }
    files: list[dict[str, object]] = []
    subcategories: list[str] = []
    continuation: dict[str, str] = {}
    while True:
        payload = None
        for attempt in range(5):
            response = session.get(endpoint, params={**params, **continuation}, timeout=30)
            if response.status_code in (429, 503):
                retry_after = response.headers.get("Retry-After", "")
                try:
                    delay = max(5.0, float(retry_after))
                except ValueError:
                    delay = min(60.0, 5.0 * (2**attempt))
                print(f"Commons ralentit les requêtes; reprise dans {delay:g} s…", flush=True)
                time.sleep(delay)
                continue
            response.raise_for_status()
            payload = response.json()
            break
        if payload is None:
            break
        for page in payload.get("query", {}).get("pages", {}).values():
            if int(page.get("ns", -1)) == 14:
                subcategories.append(str(page.get("title", "")))
            elif int(page.get("ns", -1)) == 6:
                files.append(page)
        continuation = payload.get("continue", {})
        if not continuation:
            break
    return files, subcategories


def infer_category(default: str, source_category: str, title: str, description: str) -> str:
    text = f"{source_category} {title} {description}".lower()
    if re.search(r"\b(cafe|café|coffee shop|coffeehouse|tea room|maid cafe)\b", text):
        return "cafe_interieur"
    if re.search(r"\b(bar|pub|tavern|brewpub|wine bar|beer hall|taproom)\b", text):
        return "bar_interieur"
    if re.search(r"\b(restaurant|diner|bistro|eatery|canteen|cafeteria|pizzeria|trattoria)\b", text):
        return "restaurant_interieur"
    return default


def candidate_record(
    category: str,
    page: dict[str, object],
    source_category: str,
    category_is_indoor: bool,
    category_is_tables: bool,
) -> dict[str, str] | None:
    title = str(page.get("title", "")).removeprefix("File:")
    info = (page.get("imageinfo") or [{}])[0]
    metadata = info.get("extmetadata", {})
    description = clean_markup(metadata.get("ImageDescription", {}).get("value", ""))
    artist = clean_markup(metadata.get("Artist", {}).get("value", ""))
    license_name = clean_markup(metadata.get("LicenseShortName", {}).get("value", ""))
    license_url = clean_markup(metadata.get("LicenseUrl", {}).get("value", ""))
    text = f"{title} {description}"
    if not allowed_license(license_name) or BAD_CONTENT_RE.search(text):
        return None
    if OUTDOOR_RE.search(text) or not (category_is_indoor or INDOOR_RE.search(text)):
        return None
    if not (category_is_tables or TABLE_RE.search(text) or category_is_indoor):
        return None
    if category == "restaurant_interieur" and re.search(r"\b(pub|bar|cafe|café|coffee shop)\b", text, re.I):
        return None
    if category == "cafe_interieur" and re.search(r"\b(pub|bar|tavern|brewpub)\b", text, re.I):
        return None
    if category == "bar_interieur" and re.search(r"\b(cafe|café|coffee shop|restaurant)\b", text, re.I):
        return None
    if not VENUE_PATTERNS[category].search(text) and not category_is_indoor:
        return None
    width, height = int(info.get("width", 0)), int(info.get("height", 0))
    if width < 600 or height < 400:
        return None
    thumb_url = str(info.get("thumburl", ""))
    if not thumb_url:
        return None
    return {
        "category": category,
        "title": title,
        "description": description,
        "author": artist or "Unknown (Commons file metadata)",
        "license": license_name,
        "license_url": license_url,
        "source_url": str(info.get("descriptionurl", "")),
        "image_url": thumb_url,
        "width_original": str(width),
        "height_original": str(height),
        "page_id": str(page.get("pageid", "")),
        "source_category": source_category,
        "interior_evidence": source_category if category_is_indoor else "Title or file description",
        "table_evidence": source_category if category_is_tables else "Commons interior category; visual review required",
    }


def download_image(session: requests.Session, record: dict[str, str], target: Path) -> tuple[str, int, int] | None:
    response = None
    for attempt in range(5):
        response = session.get(record["image_url"], timeout=45)
        if response.status_code in (429, 503):
            retry_after = response.headers.get("Retry-After", "")
            try:
                delay = max(5.0, float(retry_after))
            except ValueError:
                delay = min(60.0, 5.0 * (2**attempt))
            print(f"Commons limite les téléchargements; reprise dans {delay:g} s…", flush=True)
            time.sleep(delay)
            continue
        break
    if response is None or response.status_code != 200:
        return None
    if response.status_code != 200 or len(response.content) < 10_000 or len(response.content) > 25_000_000:
        return None
    try:
        from io import BytesIO

        with Image.open(BytesIO(response.content)) as opened:
            image = opened.convert("RGB")
            if image.width < 600 or image.height < 400:
                return None
            if max(image.size) > MAX_SIDE:
                image.thumbnail((MAX_SIDE, MAX_SIDE), Image.Resampling.LANCZOS)
            image.save(target, format="JPEG", quality=88, optimize=True)
        return sha256(target), image.width, image.height
    except Exception:
        target.unlink(missing_ok=True)
        return None


def main() -> int:
    OUTPUT_ROOT.mkdir(parents=True, exist_ok=True)
    STAGING_DIR.mkdir(parents=True, exist_ok=True)
    prior_records: list[dict[str, str]] = []
    if MANIFEST_PATH.exists():
        with MANIFEST_PATH.open("r", encoding="utf-8-sig", newline="") as stream:
            prior_records = list(csv.DictReader(stream))
        if not prior_records and IMAGE_DIR.exists() and any(IMAGE_DIR.iterdir()):
            print("Manifeste vide alors que des images existent; je n'écrase rien.", file=sys.stderr)
            return 2
    prior_counts = {category: 0 for category in QUERIES}
    for row in prior_records:
        if row.get("category") in prior_counts:
            prior_counts[row["category"]] += 1
    if len(prior_records) >= TARGET_TOTAL:
        print(f"La collection contient déjà {len(prior_records)} lignes de manifeste.")
        return 0
    needed_total = TARGET_TOTAL - len(prior_records)
    exact_hashes, perceptual_hashes = existing_hashes()
    session = requests.Session()
    session.headers.update({"User-Agent": USER_AGENT})

    candidates: dict[str, list[dict[str, str]]] = {key: [] for key in QUERIES}
    seen_page_ids: dict[str, set[str]] = {
        key: {row.get("page_id", "") for row in prior_records if row.get("category") == key}
        for key in QUERIES
    }
    excluded_path = OUTPUT_ROOT / "review_excluded.csv"
    excluded_ids: set[str] = set()
    if excluded_path.exists():
        with excluded_path.open("r", encoding="utf-8-sig", newline="") as stream:
            excluded_ids = {row.get("page_id", "") for row in csv.DictReader(stream)}
    seen_categories: dict[str, set[str]] = {key: set() for key in QUERIES}
    category_budget = {"restaurant_interieur": 180, "cafe_interieur": 120, "bar_interieur": 120}
    print("Recherche dans les catégories Wikimedia Commons d’intérieurs et de tables…", flush=True)
    for category, config in QUERIES.items():
        queue = deque((title, indoor, tables, 0) for title, indoor, tables in config["roots"])
        needed_category = max(0, int(config["target"]) - prior_counts[category])
        while queue and len(candidates[category]) < needed_category * 2 and len(seen_categories[category]) < category_budget[category]:
            category_title, category_is_indoor, category_is_tables, depth = queue.popleft()
            if category_title in seen_categories[category]:
                continue
            seen_categories[category].add(category_title)
            short_category_name = category_title.removeprefix("Category:")
            if SKIP_CATEGORY_RE.search(short_category_name):
                continue
            try:
                pages, subcategories = commons_category_members(session, category_title)
            except Exception as error:
                print(f"Catégorie Commons ignorée — {category_title}: {error}", flush=True)
                continue
            added = 0
            for page in pages:
                info = (page.get("imageinfo") or [{}])[0]
                metadata = info.get("extmetadata", {})
                page_title = str(page.get("title", "")).removeprefix("File:")
                page_description = clean_markup(metadata.get("ImageDescription", {}).get("value", ""))
                assigned_category = infer_category(category, category_title, page_title, page_description)
                if str(page.get("pageid", "")) in excluded_ids:
                    continue
                record = candidate_record(
                    assigned_category,
                    page,
                    category_title,
                    category_is_indoor,
                    category_is_tables,
                )
                if not record or record["page_id"] in seen_page_ids[assigned_category]:
                    continue
                seen_page_ids[assigned_category].add(record["page_id"])
                candidates[assigned_category].append(record)
                added += 1
            if added:
                print(f"{category}: +{added} candidats ({category_title})", flush=True)
            if depth < 4:
                for subcategory in subcategories:
                    child_name = subcategory.removeprefix("Category:")
                    if SKIP_CATEGORY_RE.search(child_name):
                        continue
                    child_inside = category_is_indoor or bool(INDOOR_RE.search(child_name))
                    child_tables = category_is_tables or bool(re.search(r"\btables?\b", child_name, re.I))
                    # Only descend category paths that can establish the indoor venue or table context.
                    if child_inside or child_tables:
                        queue.append((subcategory, child_inside, child_tables, depth + 1))
            time.sleep(1.5)
        print(
            f"Recherche {category} terminée: {len(candidates[category])} candidats depuis "
            f"{len(seen_categories[category])} catégories.",
            flush=True,
        )

    for category, records in candidates.items():
        records.sort(key=lambda item: (item["title"].casefold(), item["source_url"]))
    print("\nDébut du téléchargement avec contrôle SHA-256 et pHash…", flush=True)

    accepted: list[dict[str, str]] = []
    category_counts = {category: 0 for category in QUERIES}
    category_targets = {category: max(0, int(config["target"]) - prior_counts[category]) for category, config in QUERIES.items()}
    indices = []
    for path in (IMAGE_DIR.glob("table_interieur_*.jpg") if IMAGE_DIR.exists() else []):
        match = re.search(r"table_interieur_(\d+)_", path.name)
        if match:
            indices.append(int(match.group(1)))
    next_index = max(indices, default=0) + 1
    # Interleave categories so all three venue types are represented throughout.
    queues = {category: iter(records) for category, records in candidates.items()}
    stalled_rounds = 0
    while len(accepted) < needed_total and stalled_rounds < 2:
        made_progress = False
        for category, config in QUERIES.items():
            if category_counts[category] >= category_targets[category]:
                continue
            while True:
                record = next(queues[category], None)
                if record is None:
                    break
                filename = f"table_interieur_{next_index:04d}_{category}.jpg"
                staging_path = STAGING_DIR / filename
                try:
                    result = download_image(session, record, staging_path)
                except Exception:
                    result = None
                if not result:
                    continue
                digest, width, height = result
                if digest in exact_hashes:
                    staging_path.unlink(missing_ok=True)
                    continue
                phash = perceptual_hash(staging_path)
                if any((phash ^ previous).bit_count() <= PHASH_THRESHOLD for previous in perceptual_hashes):
                    staging_path.unlink(missing_ok=True)
                    continue
                exact_hashes.add(digest)
                perceptual_hashes.append(phash)
                record.update({
                    "filename": filename,
                    "sha256": digest,
                    "phash64": f"{phash:016x}",
                    "width": str(width),
                    "height": str(height),
                    "filesize_kb": str(staging_path.stat().st_size // 1024),
                    "collected_utc": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
                })
                accepted.append(record)
                category_counts[category] += 1
                next_index += 1
                made_progress = True
                if len(accepted) % 20 == 0 or len(accepted) == needed_total:
                    print(f"{len(prior_records) + len(accepted)}/{TARGET_TOTAL} — {category_counts}", flush=True)
                break
        if made_progress:
            stalled_rounds = 0
        else:
            stalled_rounds += 1

    total_records = prior_records + accepted
    total_counts = {category: prior_counts[category] + category_counts[category] for category in QUERIES}
    print(f"\nImages uniques acceptées: {len(total_records)}/{TARGET_TOTAL}; répartition: {total_counts}", flush=True)
    fields = [
        "id", "filename", "category", "title", "description", "author", "license", "license_url",
        "source_url", "image_url", "source_category", "width_original", "height_original", "width", "height",
        "filesize_kb", "sha256", "phash64", "page_id", "collected_utc", "interior_evidence", "table_evidence",
    ]
    next_id = max((int(row.get("id", "IMG_0000").split("_")[-1]) for row in prior_records), default=0) + 1
    for index, record in enumerate(accepted, next_id):
        record["id"] = f"IMG_{index:04d}"
    with MANIFEST_PATH.open("w", encoding="utf-8-sig", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=fields)
        writer.writeheader()
        writer.writerows(total_records)
    IMAGE_DIR.mkdir(parents=True, exist_ok=True)
    for record in accepted:
        (STAGING_DIR / record["filename"]).replace(IMAGE_DIR / record["filename"])
    if len(total_records) != TARGET_TOTAL:
        print(
            f"Progression enregistrée : {len(total_records)}/{TARGET_TOTAL}; les sources sont conservées dans le manifeste.",
            file=sys.stderr,
        )
        return 1
    STAGING_DIR.rmdir()

    license_counts: dict[str, int] = {}
    for record in total_records:
        license_counts[record["license"]] = license_counts.get(record["license"], 0) + 1
    readme = f"""# 400 photos d’intérieurs de restaurants, cafés et bars

Cette collection contient 400 images téléchargées depuis Wikimedia Commons. Les critères de collecte exigent une mention d’intérieur / salle, une mention de table ou d’assise et un établissement de restauration dans le titre ou la description. Les fichiers mentionnant terrasse, patio, rue, jardin, plage ou autre lieu extérieur sont écartés.

## Répartition

| Type d’intérieur | Images |
| --- | ---: |
| Restaurants | {total_counts['restaurant_interieur']} |
| Cafés | {total_counts['cafe_interieur']} |
| Bars | {total_counts['bar_interieur']} |
| **Total** | **{len(total_records)}** |

Fichiers JPEG, maximum {MAX_SIDE} px sur le plus grand côté. Les fichiers sont dédoublonnés par SHA-256 et pHash (seuil de distance de Hamming ≤ {PHASH_THRESHOLD}) contre toutes les images déjà présentes dans le projet.

Les licences acceptées sont CC BY, CC BY-SA, CC0 et domaine public. Chaque ligne de `dataset_metadata.csv` conserve l’auteur, la licence, l’URL de la page source, le lien de téléchargement, les dimensions, les empreintes et les indices textuels ayant motivé la sélection. L’attribution de chaque fichier demeure requise lorsque sa licence l’impose; les fichiers n’ont pas reçu d’annotation YOLO.

## Répartition des licences

""" + "\n".join(f"- {name}: {count}" for name, count in sorted(license_counts.items())) + "\n"
    README_PATH.write_text(readme, encoding="utf-8")
    print(f"Terminé : {IMAGE_DIR} et {MANIFEST_PATH}", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
