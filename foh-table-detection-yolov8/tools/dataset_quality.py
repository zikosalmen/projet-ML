"""Create a provenance manifest and report perceptual near-duplicates.

Run from any directory:
    python tools/dataset_quality.py

The script never deletes or moves images. Review phash_duplicates.csv manually
before deciding whether two images are redundant.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
from collections import Counter
from pathlib import Path

import cv2
import numpy as np


SPLITS = ("train", "valid", "test")
IMAGE_SUFFIXES = {".jpg", ".jpeg", ".png", ".bmp", ".webp", ".tif", ".tiff"}
FALLBACK_CLASS_NAMES = {0: "clean", 1: "dirty", 2: "occupied"}
MANIFEST_FIELDS = [
    "image_path",
    "split",
    "labels_present",
    "label_instance_counts",
    "sha256",
    "phash64",
    "source_platform",
    "source_dataset",
    "dataset_project_url",
    "dataset_declared_license",
    "source_image_url",
    "author_credit",
    "image_license",
    "license_url",
    "authorization_reference",
    "authorization_scope",
    "provenance_status",
    "notes",
]
DUPLICATE_FIELDS = ["image_a", "image_b", "hamming_distance", "split_a", "split_b"]


def load_config(root: Path) -> dict:
    config_path = root / "data.yaml"
    try:
        import yaml
    except ImportError:
        return {}
    if not config_path.exists():
        return {}
    data = yaml.safe_load(config_path.read_text(encoding="utf-8")) or {}
    return data if isinstance(data, dict) else {}


def class_name_map(config: dict) -> dict[int, str]:
    names = config.get("names", FALLBACK_CLASS_NAMES)
    if isinstance(names, list):
        return {index: str(name) for index, name in enumerate(names)}
    if isinstance(names, dict):
        return {int(index): str(name) for index, name in names.items()}
    return FALLBACK_CLASS_NAMES.copy()


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def perceptual_hash(path: Path) -> str:
    image = cv2.imread(str(path), cv2.IMREAD_GRAYSCALE)
    if image is None:
        raise ValueError(f"Unable to read image: {path}")
    resized = cv2.resize(image, (32, 32), interpolation=cv2.INTER_AREA)
    coefficients = cv2.dct(np.float32(resized) / 255.0)[:8, :8].flatten()
    median = float(np.median(coefficients[1:]))
    bits = 0
    for coefficient in coefficients:
        bits = (bits << 1) | int(coefficient > median)
    return f"{bits:016x}"


def read_label_counts(label_path: Path, names: dict[int, str]) -> Counter:
    counts: Counter = Counter()
    if not label_path.exists():
        return counts
    for line_number, line in enumerate(label_path.read_text(encoding="utf-8").splitlines(), 1):
        fields = line.split()
        if not fields:
            continue
        try:
            class_id = int(fields[0])
        except (ValueError, IndexError):
            raise ValueError(f"Invalid YOLO label at {label_path}:{line_number}")
        counts[names.get(class_id, f"class_{class_id}")] += 1
    return counts


def previous_metadata(path: Path) -> dict[str, dict[str, str]]:
    if not path.exists():
        return {}
    with path.open("r", encoding="utf-8-sig", newline="") as stream:
        return {row.get("image_path", ""): row for row in csv.DictReader(stream)}


def default_provenance(config: dict) -> dict[str, str]:
    roboflow = config.get("roboflow", {})
    if not isinstance(roboflow, dict):
        roboflow = {}
    project = str(roboflow.get("project", ""))
    version = str(roboflow.get("version", ""))
    return {
        "source_platform": "Roboflow export (original source to verify)",
        "source_dataset": f"{project} v{version}".strip(" v"),
        "dataset_project_url": str(roboflow.get("url", "")),
        "dataset_declared_license": str(roboflow.get("license", "")),
        "source_image_url": "",
        "author_credit": "",
        "image_license": "UNVERIFIED",
        "license_url": "",
        "authorization_reference": "",
        "authorization_scope": "",
        "provenance_status": "needs_manual_verification",
        "notes": (
            "The export declares a project-level license; verify the original "
            "image source and rights for this image."
        ),
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    default_root = Path(__file__).resolve().parents[1]
    parser.add_argument("--root", type=Path, default=default_root, help="YOLO dataset root")
    parser.add_argument("--threshold", type=int, default=4, help="Maximum pHash Hamming distance")
    parser.add_argument("--manifest", type=Path, help="Manifest CSV path (default: ROOT/dataset_manifest.csv)")
    parser.add_argument("--duplicates", type=Path, help="Duplicate report path (default: ROOT/phash_duplicates.csv)")
    args = parser.parse_args()

    root = args.root.resolve()
    manifest_path = (args.manifest or root / "dataset_manifest.csv").resolve()
    duplicates_path = (args.duplicates or root / "phash_duplicates.csv").resolve()
    config = load_config(root)
    names = class_name_map(config)
    old_rows = previous_metadata(manifest_path)
    defaults = default_provenance(config)
    rows = []
    image_records = []
    instance_totals: Counter = Counter()
    image_totals: Counter = Counter()

    for split in SPLITS:
        image_dir = root / split / "images"
        label_dir = root / split / "labels"
        if not image_dir.exists():
            continue
        for image_path in sorted(p for p in image_dir.iterdir() if p.suffix.lower() in IMAGE_SUFFIXES):
            relative_path = image_path.relative_to(root).as_posix()
            counts = read_label_counts(label_dir / f"{image_path.stem}.txt", names)
            instance_totals.update(counts)
            image_totals.update(counts.keys())
            row = {
                "image_path": relative_path,
                "split": split,
                "labels_present": ";".join(sorted(counts)),
                "label_instance_counts": json.dumps(dict(sorted(counts.items())), ensure_ascii=False),
                "sha256": sha256_file(image_path),
                "phash64": perceptual_hash(image_path),
            }
            prior = old_rows.get(relative_path, {})
            for field, default in defaults.items():
                row[field] = prior.get(field, default)
            rows.append(row)
            image_records.append((relative_path, split, int(row["phash64"], 16)))

    manifest_path.parent.mkdir(parents=True, exist_ok=True)
    with manifest_path.open("w", encoding="utf-8-sig", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=MANIFEST_FIELDS)
        writer.writeheader()
        writer.writerows(rows)

    matches = []
    for index, (path_a, split_a, hash_a) in enumerate(image_records):
        for path_b, split_b, hash_b in image_records[index + 1 :]:
            distance = (hash_a ^ hash_b).bit_count()
            if distance <= args.threshold:
                matches.append({
                    "image_a": path_a,
                    "image_b": path_b,
                    "hamming_distance": distance,
                    "split_a": split_a,
                    "split_b": split_b,
                })
    duplicates_path.parent.mkdir(parents=True, exist_ok=True)
    with duplicates_path.open("w", encoding="utf-8-sig", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=DUPLICATE_FIELDS)
        writer.writeheader()
        writer.writerows(matches)

    print(f"Images analysees : {len(rows)}")
    print("Instances annotees : " + ", ".join(f"{name}={count}" for name, count in sorted(instance_totals.items())))
    print("Images contenant chaque classe : " + ", ".join(f"{name}={count}" for name, count in sorted(image_totals.items())))
    print(f"Paires pHash a controler (distance <= {args.threshold}) : {len(matches)}")
    print(f"Manifeste : {manifest_path}")
    print(f"Rapport pHash : {duplicates_path}")


if __name__ == "__main__":
    main()
