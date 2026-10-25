# UK SFR Market Monitor

Static site served by GitHub Pages from `main` at the repo root (https://radhxy.github.io/uk-sfr-dashboard/). Every push to `main` republishes it.

## Layout
- `dashboard.html` is the source page: one `<style>`, the markup, and one `<script>`. Edit this, not `index.html`.
- `build.py` wraps it into `index.html` (theme tokens, fonts, Sources footer, script tags). Run `python3 -I build.py` after any change to `dashboard.html` or the dataset list in `build.py`, and commit both.
- `js/dash-shim.js` stands in for the claude.ai dashboard runtime: `dash.data(id)` loads `data/<file>.json` (mapped in `build.py`), `dash.calc` runs calculations, `dash.setParams` holds the region/developer filters.
- `data/` holds the datasets as JSON arrays of row objects. Keep column names stable; the page reads them by name.

## Data
- `region_quarterly.json`, `area_quarterly.json`: ONS Price Index of Private Rents, HM Land Registry UK HPI and Price Paid, MHCLG Live Table 217.
- `bulk_deals.json`: Price Paid category B, 5+ new-build houses on one street on one day; deals at 80%+ of the local open-market new-build median are "Likely SFR/PRS".
- `developer_metrics.json`: housebuilder results, one row per metric with `source_url` and `source_type`.
- `schemes_sample.json`: illustrative only. The Development economics tab says so; keep that label until real data replaces it.

## Checks before pushing
- `node --check` on the extracted page script, then load the site with Playwright (`python3 -m http.server` in the repo, open it, click every tab) and confirm no console errors and no horizontal scroll at 400px.
- The site is public. Do not commit private deal data.
