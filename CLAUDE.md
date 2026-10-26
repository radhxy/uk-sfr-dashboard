# UK SFR Market Monitor

Static site served by GitHub Pages from `main` at the repo root (https://radhxy.github.io/uk-sfr-dashboard/). Every push to `main` republishes it.

## Layout
- `dashboard.html` is the source page: one `<style>`, the markup, and one `<script>`. Edit this, not `index.html`.
- `build.py` wraps it into `index.html` (theme tokens, fonts, script tags) and owns the sources: `SOURCES` lists each original publication with its link and licence, `CARD_SOURCES` says which sources each chart or table cites (rendered as a "Source:" line under it), company documents are listed from the `source_url` fields, and it writes CSV copies of every dataset to `data/csv/` for the download links. Add a source there when you add data. Run `python3 -I build.py` after any change to `dashboard.html` or the dataset list in `build.py`, and commit both.
- `js/dash-shim.js` stands in for the claude.ai dashboard runtime: `dash.data(id)` loads `data/<file>.json` (mapped in `build.py`), `dash.calc` runs calculations, `dash.setParams` holds the region/developer filters.
- `data/` holds the datasets as JSON arrays of row objects. Keep column names stable; the page reads them by name.

## Data
- `region_quarterly.json`, `area_quarterly.json`: ONS Price Index of Private Rents, HM Land Registry UK HPI and Price Paid, MHCLG Live Table 217.
- `region_types_quarterly.json`: region rows from `area_quarterly.json` (rent and price by property type), so the main tabs don't load the 5 MB council file. Every market yield is computed in the page by `yieldOf()` from rent and price on the viewer's Yield basis (market, or investor: new-let uplift, bulk discount, operating costs, purchaser's costs); don't store yields in the data files. The panel's property mix drives the whole page: `regionMixSeries()` gives mix rent, price and yield (with forecast), and `dealMixHouses()` / `dealInMix()` restrict bulk-deal counts, prices and lists to the mix. Only MHCLG completions have no house-type split.
- `bulk_deals.json`: Price Paid category B, 5+ new-build houses on one street on one day; deals at 80%+ of the local open-market new-build median are "Likely SFR/PRS".
- `developer_metrics.json`: housebuilder results, one row per metric with `source_url` and `source_type`.
- `developer_economics.json`: one row per housebuilder from its latest results (margins, ASPs, land cost share, land bank, build cost inflation, bulk/partner volumes), with `source_url`. `land_cost_derived` marks shares calculated from reported land values rather than stated. Scheme-level charts on that tab only show a visitor's own uploaded spreadsheet.

## Checks before pushing
- `node --check` on the extracted page script, then load the site with Playwright (`python3 -m http.server` in the repo, open it, click every tab) and confirm no console errors and no horizontal scroll at 400px.
- The site is public. Do not commit private deal data.
