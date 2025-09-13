#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import csv, json, os, sys, re, uuid, datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA_CSV = ROOT / "data" / "tmls_cards.csv"
SCHEMA_FILE = ROOT / "schemas" / "card.schema.json"
OUT = ROOT / "datasets"

def slugify(s):
    s = (s or "").strip().lower()
    s = re.sub(r"[^a-z0-9]+", "-", s)
    return s.strip("-")

def stable_uuid5(namespace, name):
    return str(uuid.uuid5(namespace, name))

def read_csv_rows(path):
    with open(path, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        rows = [{k.strip(): (v.strip() if isinstance(v, str) else v) for k,v in row.items()} for row in reader]
    return rows

def ensure_schema():
    with open(SCHEMA_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

def validate_card(card, schema):
    # Light validation (geen externe libs)
    req = schema.get("required", [])
    for r in req:
        if r not in card or card[r] in (None, ""):
            raise ValueError(f"Missing required field: {r}")
    if not isinstance(card.get("hints", []), list):
        raise ValueError("Field 'hints' must be an array")

def build():
    if not DATA_CSV.exists():
        print(f"[!] CSV not found: {DATA_CSV}", file=sys.stderr)
        sys.exit(1)

    rows = read_csv_rows(DATA_CSV)
    cards = []
    index_map = {}
    ns = uuid.NAMESPACE_URL

    for i, row in enumerate(rows, start=2):
        category = (row.get("category") or "").strip()
        card_name = (row.get("card") or "").strip()
        if not category or not card_name:
            raise ValueError(f"CSV line {i}: missing 'category' or 'card'")

        category_slug = slugify(category)
        card_slug = slugify(card_name)
        slug = f"{category_slug}-{card_slug}"

        hints = []
        for k, v in row.items():
            if k and k.lower().startswith("hint") and v:
                hints.append(v.strip())

        tags_raw = row.get("tags", "")
        tags = [t.strip() for t in tags_raw.split(",") if t.strip()] if tags_raw else []

        cid = (row.get("id") or "").strip() or stable_uuid5(ns, slug)

        known = {"id","category","card","subtitle","symbol","rarity","color","flavor","tags","notes"}
        extra = {k:v for k,v in row.items() if k not in known and v not in (None, "") and not k.lower().startswith("hint")}

        card = {
            "id": cid,
            "slug": slug,
            "category": category,
            "category_slug": category_slug,
            "card": card_name,
            "subtitle": row.get("subtitle",""),
            "symbol": row.get("symbol",""),
            "rarity": row.get("rarity",""),
            "color": row.get("color",""),
            "hints": hints,
            "flavor": row.get("flavor",""),
            "tags": tags,
            "extra": extra,
            "notes": row.get("notes","")
        }
        cards.append(card)
        index_map.setdefault(category_slug, {"category": category, "category_slug": category_slug, "count": 0})
        index_map[category_slug]["count"] += 1

    # Validatie
    schema = ensure_schema()
    for c in cards: validate_card(c, schema)

    OUT.mkdir(parents=True, exist_ok=True)
    # all cards
    (OUT / "cards.json").write_text(json.dumps(cards, ensure_ascii=False, indent=2), encoding="utf-8")
    # index
    (OUT / "index.json").write_text(json.dumps(list(index_map.values()), ensure_ascii=False, indent=2), encoding="utf-8")
    # per category
    cats = OUT / "categories"; cats.mkdir(exist_ok=True)
    for slug, meta in index_map.items():
        items = [c for c in cards if c["category_slug"] == slug]
        (cats / f"{slug}.json").write_text(json.dumps(items, ensure_ascii=False, indent=2), encoding="utf-8")
    # per card
    per = OUT / "cards"; per.mkdir(exist_ok=True)
    for c in cards:
        (per / f"{c['id']}.json").write_text(json.dumps(c, ensure_ascii=False, indent=2), encoding="utf-8")
    # version
    meta = {
        "schema": "card.schema.json#2025-09",
        "generated_at": datetime.datetime.utcnow().isoformat() + "Z",
        "totals": {"cards": len(cards), "categories": len(index_map)}
    }
    (OUT / "version.json").write_text(json.dumps(meta, ensure_ascii=False, indent=2), encoding="utf-8")

    print(f"Built {len(cards)} cards across {len(index_map)} categories.")

if __name__ == "__main__":
    build()
