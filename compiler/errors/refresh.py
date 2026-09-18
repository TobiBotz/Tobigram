import csv
import html
import json
import re
import sys
from pathlib import Path
import urllib.request

HOME = Path(__file__).parent
SOURCE = HOME / "source"
CACHE = HOME / "errors.json"
URL = "https://core.telegram.org/api/errors.json"


def fetch_errors_json() -> dict:
    # Use cached file if it exists and is recent/valid, else fetch online
    if CACHE.exists() and CACHE.stat().st_size > 0:
        with open(CACHE, encoding="utf-8") as f:
            return json.load(f)

    try:
        req = urllib.request.Request(
            URL, headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
        )
        with urllib.request.urlopen(req, timeout=15) as resp:
            data_bytes = resp.read()
            with open(CACHE, "wb") as f:
                f.write(data_bytes)
            return json.loads(data_bytes.decode("utf-8"))
    except Exception as e:
        print(f"Warning: Failed to download from {URL}: {e}")
        if CACHE.exists():
            print(f"Using cached {CACHE}")
            with open(CACHE, encoding="utf-8") as f:
                return json.load(f)
        raise


def clean_description(desc: str) -> str:
    if not desc:
        return ""
    # Decode html entities
    desc = html.unescape(desc)
    # Replace %d with {value}
    desc = desc.replace("%d", "{value}")
    # Remove HTML tags if any
    desc = re.sub(r"<[^>]+>", "", desc)
    # Remove triple quotes if any
    desc = desc.replace('"""', '"')
    # Normalize spaces
    desc = re.sub(r"\s+", " ", desc).strip()
    return desc


def normalize_id(err_id: str) -> str:
    err_id = re.sub(r"_%d", "_X", err_id)
    err_id = re.sub(r"%d", "X", err_id)
    return err_id


def refresh(force_download: bool = False):
    if force_download and CACHE.exists():
        CACHE.unlink()

    data = fetch_errors_json()
    layer = data.get("layer", "unknown")
    print(f"Loaded official Telegram errors (Layer {layer})")

    descriptions = data.get("descriptions", {})
    official_errors = data.get("errors", {})

    # Build lookup map from normalized ID to cleaned official description
    norm_desc_map = {}
    for err_id, raw_desc in descriptions.items():
        cd = clean_description(raw_desc)
        if cd:
            norm_desc_map[err_id] = cd
            norm_desc_map[normalize_id(err_id)] = cd

    tsv_files = {p.stem.split("_")[0]: p for p in SOURCE.glob("*.tsv")}

    total_added = 0
    total_updated = 0

    for code, err_dict in sorted(official_errors.items()):
        tsv_code = "503" if code == "-503" else code
        tsv_path = tsv_files.get(tsv_code)
        if not tsv_path:
            continue

        existing = {}
        with open(tsv_path, encoding="utf-8") as f:
            reader = csv.reader(f, delimiter="\t")
            next(reader, None)  # header
            for row in reader:
                if row:
                    existing[row[0]] = row[1]

        added_count = 0
        updated_count = 0

        # 1. Add / Update all errors from official error list
        for err_id in err_dict:
            norm_id = normalize_id(err_id)
            target_id = (
                norm_id if norm_id in existing else (err_id if err_id in existing else norm_id)
            )

            desc = norm_desc_map.get(target_id) or norm_desc_map.get(err_id)
            if not desc:
                raw_desc = descriptions.get(err_id, "")
                desc = clean_description(raw_desc)
            if not desc:
                desc = target_id.replace("_", " ").capitalize()

            if target_id in existing:
                if desc and existing[target_id] != desc:
                    existing[target_id] = desc
                    updated_count += 1
            else:
                existing[target_id] = desc
                added_count += 1

        # 2. Update any other existing errors that have an official description
        for k in list(existing.keys()):
            if k in norm_desc_map and existing[k] != norm_desc_map[k]:
                existing[k] = norm_desc_map[k]
                updated_count += 1

        # Sort and write back
        sorted_keys = sorted(existing.keys())
        with open(tsv_path, "w", encoding="utf-8", newline="") as f:
            f.write("id\tmessage\n")
            for k in sorted_keys:
                f.write(f"{k}\t{existing[k]}\n")

        print(
            f"  {tsv_path.name}: added {added_count}, updated {updated_count} (total {len(sorted_keys)})"
        )
        total_added += added_count
        total_updated += updated_count

    print(f"\nTotal new errors added: {total_added}, existing updated: {total_updated}")

    print("Recompiling exception classes...")
    sys.path.insert(0, str(HOME))
    import compiler

    compiler.start()
    print("Exceptions recompiled successfully.")


if __name__ == "__main__":
    refresh()
