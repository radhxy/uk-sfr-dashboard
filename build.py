# Builds index.html for the standalone site from the dashboard page (dashboard.html).
import json, re, html
page = open('dashboard.html').read()
style = re.search(r'<style>(.*?)</style>', page, re.S).group(1)
script = re.search(r'<script>(.*?)</script>', page, re.S).group(1)
markup = re.sub(r'<style>.*?</style>|<script.*?</script>', '', page, flags=re.S).strip()
DS = {
 'region_quarterly': ('region_quarterly.json', 'Regional prices, rents and yields', 'Quarterly by region, 2019 Q1 to 2026 Q3: average semi-detached price and new-build price (HM Land Registry UK HPI, Aug 2026); semi-detached and 3-bed rent (ONS Price Index of Private Rents, Oct 2026); gross and net yield on a fixed basis (semi-detached, 25% operating costs, 30% London; the page recalculates yields on your Yield basis); standard new-build house sales and houses in bulk deals (Land Registry Price Paid); private-sector completions (MHCLG Live Table 217). Forecasts to 2028 Q4 blend Knight Frank (Apr 2026) and Savills national price forecasts; the rent forecast is a trend assumption.'),
 'region_types_quarterly': ('region_types_quarterly.json', 'Regional rents and prices by property type', 'Quarterly by region, 2019 Q1 to 2026 Q3: ONS rent and UK HPI average price for detached, semi-detached, terraced and flat homes. Drives every yield, on the basis set in the Yield basis panel.'),
 'bulk_deals': ('bulk_deals.json', 'Land Registry bulk deals', '5+ new-build houses on one street registered the same day to a non-private buyer (Price Paid category B), Jan 2019 to Aug 2026, with the local open-market new-build median and outcode coordinates (postcodes.io). Deals at 80%+ of local open market are classed as likely SFR/PRS.'),
 'developer_metrics': ('developer_metrics.json', 'Housebuilder reported metrics', 'Average selling prices, sales rates with and without bulk/PRS sales and completions from Barratt Redrow, Persimmon, Taylor Wimpey, Bellway and Vistry results (2025–2026), each with its source.'),
 'area_quarterly': ('area_quarterly.json', 'Council rents and prices by size', 'Quarterly, 2019 Q1 to 2026 Q3, for every council in eight English regions, the regions and England: rent by bedrooms and property type (ONS PIPR), average price by property type (UK HPI), standard new-build house sales and median price (Price Paid), houses in likely SFR bulk deals.'),
 'developer_economics': ('developer_economics.json', 'Housebuilder economics', 'Gross and operating margins, private and bulk/partner average selling prices, land cost as a share of ASP, land bank, build cost inflation and bulk or partner volumes from Barratt Redrow (FY26), Bellway (FY26), Persimmon, Taylor Wimpey and Vistry (H1 2026) results. Land shares marked derived are calculated from reported land values and plot counts.'),
}
cfg = {k: {'file': v[0]} for k, v in DS.items()}

# Original publications behind the data. Keys are used by CARD_SOURCES and the Sources section anchors (#src-<key>).
SOURCES = {
 'pipr': ('Price Index of Private Rents (PIPR)', 'Office for National Statistics', 'Monthly rents by region and council, by bedrooms and property type. October 2026 release, data to September 2026.', 'https://www.ons.gov.uk/economy/inflationandpriceindices/datasets/priceindexofprivaterentsukmonthlypricestatistics', 'Open Government Licence v3.0'),
 'hpi': ('UK House Price Index', 'HM Land Registry, ONS and devolved agencies', 'Monthly average prices by region and council, by property type and new-build vs existing. August 2026 data release.', 'https://www.gov.uk/government/statistical-data-sets/uk-house-price-index-data-downloads-august-2026--2', 'Open Government Licence v3.0'),
 'ppd': ('Price Paid Data', 'HM Land Registry', 'Every residential sale in England and Wales, January 2019 to August 2026: price, date, postcode, property type, new-build flag and buyer category. Used for new-build sales and the bulk-deal analysis.', 'https://www.gov.uk/government/statistical-data-sets/price-paid-data-downloads', 'Open Government Licence v3.0; contains HM Land Registry data © Crown copyright and database right 2026'),
 'lt217': ('Live Table 217: house building by tenure and region', 'Ministry of Housing, Communities and Local Government', 'Quarterly permanent dwellings started and completed by private enterprise, housing associations and local authorities, to 2026 Q2.', 'https://www.gov.uk/government/statistical-data-sets/live-tables-on-house-building', 'Open Government Licence v3.0'),
 'postcodes': ('postcodes.io', 'Ideal Postcodes (open data from ONS and Ordnance Survey)', 'Latitude and longitude of postcode districts, used to place bulk deals on the map.', 'https://postcodes.io', 'Open Government Licence v3.0; contains OS data © Crown copyright and database right'),
 'kf': ('Knight Frank house price forecast, April 2026', 'Knight Frank (via Property Industry Eye)', 'UK price growth of 1.5% in 2026, 3% in 2027 and 4% in 2028; half of the blended price forecast.', 'https://propertyindustryeye.com/?p=162936', 'Press coverage of a published forecast'),
 'savills': ('Savills five-year house price forecast', 'Savills (via Property Industry Eye)', 'UK prices −2% in 2026 and +18.5% over five years to 2030; the other half of the blended price forecast.', 'https://propertyindustryeye.com/savills-revises-its-five-year-house-price-forecast/', 'Press coverage of a published forecast'),
 'kfsfh': ('Single Family Housing report 2026', 'Knight Frank', 'UK single-family rental investment volumes.', 'https://www.knightfrank.co.uk/site-assets/research/report-pdfs/single-family-housing-report/sfh-report-2026_final.pdf', 'Published research'),
 'results': ('Housebuilder results', 'Barratt Redrow, Persimmon, Taylor Wimpey, Bellway, Vistry', 'Selling prices, sales rates, margins, land costs, land banks, build cost inflation and bulk/PRS volumes. Each document is listed below.', '#src-results-list', 'Company announcements and press coverage'),
}
CARD_SOURCES = {
 'kpis': ['pipr', 'hpi', 'ppd', 'lt217'], 'card-map': ['hpi', 'pipr', 'ppd', 'postcodes'], 'card-region-bars': ['pipr', 'hpi'],
 'card-rates': ['results'], 'card-asp': ['results'], 'card-dev-table': ['results', 'kfsfh'], 'card-units': ['ppd'], 'card-bulk-om': ['ppd'],
 'card-price': ['hpi', 'kf', 'savills'], 'card-rent': ['pipr'], 'card-yield': ['pipr', 'hpi', 'kf', 'savills'], 'card-outlook': ['pipr', 'hpi', 'kf', 'savills'],
 'card-dd-sizes': ['pipr', 'hpi', 'ppd'], 'card-dd-trend': ['pipr', 'hpi', 'ppd'], 'card-dd-rank': ['pipr', 'hpi', 'ppd'], 'card-dd-councils': ['pipr', 'hpi', 'ppd'],
 'card-deals': ['ppd', 'postcodes'], 'card-econ-table': ['results'], 'card-margins': ['results'], 'card-bulkprice': ['results'], 'card-unitecon': ['results'],
}
esc = html.escape

# CSV copies of every dataset for Excel.
import csv, io, os
os.makedirs('data/csv', exist_ok=True)
downloads = []
for key, (fname, title, desc) in DS.items():
    rows = json.load(open('data/' + fname))
    cols = list(dict.fromkeys(k for r in rows for k in r))
    with open('data/csv/' + fname.replace('.json', '.csv'), 'w', newline='', encoding='utf-8-sig') as f:
        w = csv.DictWriter(f, fieldnames=cols); w.writeheader(); w.writerows(rows)
    size = os.path.getsize('data/csv/' + fname.replace('.json', '.csv'))
    downloads.append((title, desc, fname, len(rows), size))

# Company documents behind developer figures, deduplicated by URL.
docs = {}
for f in ('developer_metrics.json', 'developer_economics.json'):
    for r in json.load(open('data/' + f)):
        u = r.get('source_url')
        if u and u.startswith('https://'):
            d = docs.setdefault(u, {'devs': set(), 'periods': set(), 'type': r.get('source_type', '')})
            d['devs'].add(r['developer']); d['periods'].add(r['period'])
host = lambda u: re.sub(r'^https://(www\.)?', '', u).split('/')[0]
ext = 'target="_blank" rel="noopener"'
sources = ''.join(
    f'<li id="src-{k}"><a href="{esc(u)}" {"" if u.startswith("#") else ext}>{esc(t)}</a>'
    f'<span class="src-pub">{esc(p)}</span><span class="src-desc">{esc(d)}</span><span class="src-lic">{esc(l)}</span></li>'
    for k, (t, p, d, u, l) in SOURCES.items())
# What kind of document each host serves, so the label describes the document rather than one figure in it.
DOC_KIND = {'investegate.co.uk': 'Company announcement (RNS)', 'stockopedia.com': 'Company announcement (RNS)', 'barrattredrow.co.uk': 'Company document',
            'knightfrank.co.uk': 'Published research', 'directorstalkinterviews.com': 'Company results document, third-party copy',
            'hl.co.uk': 'Analyst coverage', 'marketbeat.com': 'Earnings coverage', 'scottishhousingnews.com': 'Press coverage'}
doc_name = lambda devs: ', '.join('UK SFR market' if d == 'Market' else d for d in sorted(devs))
doc_items = ''.join(
    f'<li><a href="{esc(u)}" {ext}>{esc(doc_name(v["devs"]))} · {esc(", ".join(sorted(v["periods"])))}</a>'
    f'<span class="src-pub">{esc(DOC_KIND.get(host(u), "Other"))} · {esc(host(u))}</span></li>'
    for u, v in sorted(docs.items(), key=lambda kv: (doc_name(kv[1]['devs']), sorted(kv[1]['periods']))))
kb = lambda n: f'{n / 1e6:.1f} MB' if n >= 1e6 else f'{max(1, round(n / 1e3))} KB'
dl_items = ''.join(
    f'<li><span class="dl-title">{esc(t)}</span><span class="src-desc">{esc(d)}</span>'
    f'<span class="dl-links"><a href="data/csv/{fn.replace(".json", ".csv")}" download>CSV · {kb(s)}</a> '
    f'<a href="data/{fn}" download>JSON</a> <span class="src-pub">{n:,} rows</span></span></li>'
    for t, d, fn, n, s in downloads)
tokens = """
:root {
  --font-anthropic-sans: "IBM Plex Sans", system-ui, -apple-system, "Segoe UI", sans-serif;
  --font-anthropic-serif: "Source Serif 4", Georgia, "Times New Roman", serif;
  --color-bg: #f6f7f5; --color-panel: #ffffff; --color-fg: #1d2421; --color-fg-muted: #5e6863; --color-border-line: #dde2de;
  --color-ok: #23794f; --color-warn: #a35f00; --color-bad: #b4372f;
  --series-1: #2f7d5b; --series-2: #c0632b; --series-3: #3b6fb6; --series-4: #8a4fb0; --series-5: #b8912a; --series-6: #2a8f93; --series-7: #b84a74; --series-8: #6b7470;
  --cds-chart-muted: #c3cbc6; --cds-chart-grid: #eceeec; --cds-chart-axis: #b7beba; --cds-chart-reference: #8f9893;
  --cds-surface-popover: #ffffff; --cds-border: #d4dad6; --cds-shadow-popover: 0 6px 20px rgba(20, 30, 25, .12); --cds-text-secondary: #5e6863;
  --cds-font-size-caption: .78rem; --cds-font-size-body: .9rem; --cds-font-size-heading: 1rem; --cds-font-size-title: 1.75rem; --cds-font-weight-medium: 600;
  --cds-gap-xs: 4px; --cds-gap-sm: 8px; --cds-gap-md: 14px; --cds-gap-lg: 22px; --cds-pad-xs: 4px; --cds-pad-sm: 8px; --cds-pad-md: 12px; --cds-pad-lg: 18px; --cds-pad-xl: 28px;
  --cds-radius: 8px; --cds-dur-slow: .35s; --cds-ease-out: cubic-bezier(.2, .7, .2, 1);
  color-scheme: light;
}
@media (prefers-color-scheme: dark) {
  :root {
    --color-bg: #121614; --color-panel: #1a201d; --color-fg: #e6ebe8; --color-fg-muted: #9aa5a0; --color-border-line: #2c3531;
    --color-ok: #5cc28f; --color-warn: #e0a24a; --color-bad: #ef7a70;
    --series-1: #5cc28f; --series-2: #e58a52; --series-3: #6f9de0; --series-4: #b98ad8; --series-5: #d9b85a; --series-6: #5bbdc0; --series-7: #e07ba1; --series-8: #9aa5a0;
    --cds-chart-muted: #3f4a45; --cds-chart-grid: #232b27; --cds-chart-axis: #3d4742; --cds-chart-reference: #7d8883;
    --cds-surface-popover: #222a26; --cds-border: #36413c; --cds-shadow-popover: 0 6px 20px rgba(0, 0, 0, .45); --cds-text-secondary: #9aa5a0;
    color-scheme: dark;
  }
}
* { box-sizing: border-box; }
html, body { margin: 0; }
body { background: var(--color-bg); color: var(--color-fg); font-family: var(--font-anthropic-sans); font-size: 14px; line-height: 1.4; }
#dash-root { max-width: 1440px; margin-inline: auto; padding-block: 24px 48px; padding-left: max(16px, env(safe-area-inset-left, 0px)); padding-right: max(16px, env(safe-area-inset-right, 0px)); }
[hidden] { display: none !important; }
a { color: inherit; }
.dash-skeleton { color: transparent !important; background: var(--cds-chart-grid); border-radius: 4px; min-width: 3ch; display: inline-block; }
.sfr-chart.dash-skeleton { display: block; }
.site-foot { margin-top: 24px; }
.site-foot h3 { margin: var(--cds-gap-md) 0 0; font-size: var(--cds-font-size-body); font-weight: 600; }
.src-list { list-style: none; margin: 0; padding: 0; display: grid; grid-template-columns: repeat(auto-fit, minmax(min(100%, 22rem), 1fr)); gap: var(--cds-gap-sm) var(--cds-gap-lg); }
.src-list li { display: grid; align-content: start; gap: 2px; min-width: 0; font-size: var(--cds-font-size-caption); line-height: 1.45; padding: var(--cds-pad-xs) 0; border-top: 1px solid var(--color-border-line); }
.src-list li:target { background: color-mix(in srgb, var(--color-fg) 6%, transparent); }
.src-list a, .sfr-src a { color: var(--series-3); text-decoration: underline; text-underline-offset: 2px; overflow-wrap: anywhere; }
.src-list a { font-size: var(--cds-font-size-body); font-weight: 500; }
.src-list a:focus-visible, .sfr-src a:focus-visible { outline: 2px solid var(--color-fg); outline-offset: 2px; border-radius: 2px; }
.src-pub { color: var(--color-fg-muted); }
.src-desc { color: var(--color-fg); }
.src-lic { color: var(--color-fg-muted); font-style: italic; }
.dl-title { font-size: var(--cds-font-size-body); font-weight: 500; }
.dl-links { display: flex; flex-wrap: wrap; gap: var(--cds-gap-md); align-items: baseline; }
.sfr-src { margin: 0; font-size: var(--cds-font-size-caption); color: var(--color-fg-muted); line-height: 1.5; }
.sfr-kpis + .sfr-src { margin-top: calc(-1 * var(--cds-gap-sm)); }
.vh { position: absolute; width: 1px; height: 1px; overflow: hidden; clip: rect(0 0 0 0); white-space: nowrap; }
"""
out = f"""<!doctype html>
<html lang="en-GB">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<title>UK SFR Market Monitor</title>
<meta name="description" content="UK single-family rental market: prices, rents, yields, bulk deals and developer metrics by region and council.">
<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=IBM+Plex+Sans:wght@400;500;600&family=Source+Serif+4:opsz,wght@8..60,400&display=swap">
<style>{tokens}
{style}</style>
</head>
<body>
<div id="dash-root">
{markup}
<section class="sfr-card wide site-foot" id="sources" aria-labelledby="sources-h">
  <h2 id="sources-h">Sources</h2>
  <p class="sfr-note">Links open in a new tab. Every chart and table names its sources underneath it.</p>
  <ul class="src-list">{sources}</ul>
  <h3 id="src-results-list">Company results documents</h3>
  <ul class="src-list">{doc_items}</ul>
  <h3 id="downloads">Download the data</h3>
  <p class="sfr-note">The datasets this site uses, after cleaning and joining. CSV opens in Excel.</p>
  <ul class="src-list dl-list">{dl_items}</ul>
  <p class="sfr-note">Contains HM Land Registry data © Crown copyright and database right 2026. ONS and MHCLG data under the Open Government Licence v3.0. Developer figures from company announcements and press coverage. Built {__import__('datetime').date.today().isoformat()}.</p>
</section>
</div>
<script>window.SFR_DATASETS = {json.dumps(cfg)};</script>
<script src="js/d3.v7.9.0.min.js"></script>
<script src="js/dash-shim.js"></script>
<script src="js/uk_regions.js"></script>
<script>
{script}
</script>
<script>
(() => {{
  const S = {json.dumps({k: [v[0], v[3]] for k, v in SOURCES.items()})}, C = {json.dumps(CARD_SOURCES)};
  for (const [id, keys] of Object.entries(C)) {{
    const card = document.getElementById(id); if (!card) continue;
    const p = document.createElement('p'); p.className = 'sfr-src'; p.append('Source: ');
    keys.forEach((k, i) => {{
      const [name, url] = S[k], a = document.createElement('a'); a.href = url; a.textContent = name;
      if (!url.startsWith('#')) {{ a.target = '_blank'; a.rel = 'noopener'; const v = document.createElement('span'); v.className = 'vh'; v.textContent = ' (opens in a new tab)'; a.append(v); }}
      if (i) p.append(' · '); p.append(a);
    }});
    p.append(' · '); const all = document.createElement('a'); all.href = '#sources'; all.textContent = 'All sources'; p.append(all);
    if (id === 'kpis') card.after(p); else card.append(p);
  }}
}})();
</script>
<script>window.addEventListener('hashchange', () => {{ const t = document.getElementById('tab-' + location.hash.slice(1)); if (t) t.click(); }});</script>
</body>
</html>
"""
out = out.replace('<script src="uk_regions.js"></script>', '')
open('index.html', 'w').write(out)
print(len(out))
