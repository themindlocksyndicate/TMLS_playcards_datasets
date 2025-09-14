# TMLS Datasets Starter (CSV → JSON)

Deze repo zet jouw kaartentabel (CSV) om naar nette JSON datasets die je viewer kan inladen.

## Wat dit genereert
- `datasets/cards.json` – alle kaarten (flat lijst)
- `datasets/index.json` – categorie-index met aantallen
- `datasets/categories/<category>.json` – per categorie
- `datasets/cards/<id>.json` – 1 file per kaart
- `datasets/version.json` – meta (schema, timestamp, totals)

## CSV-format
Zet je deck in `data/tmls_cards.csv` met header:
```
id,category,card,subtitle,symbol,rarity,color,hint1,hint2,hint3,flavor,tags,notes
```
- `id` mag leeg (wordt stabiel uuid5 op basis van slug).
- `tags`: komma-gescheiden.
- Extra kolommen worden automatisch in `extra` gezet.

## Lokaal bouwen
```bash
python3 scripts/build_datasets.py
```

## CI (GitHub Actions)
- **build-datasets.yml** bouwt `datasets/**` en commit dat terug.
- **pages.yml** publiceert de repo naar GitHub Pages.

### Repo-instellingen
1. Settings → Actions → General
   - Allow all actions
   - Workflow permissions: **Read and write**
2. Settings → Pages
   - Build and deployment: **GitHub Actions**

--TMLS
