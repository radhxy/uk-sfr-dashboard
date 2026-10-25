# Builds index.html for the standalone site from the dashboard page (dashboard.html).
import json, re, html
page = open('dashboard.html').read()
style = re.search(r'<style>(.*?)</style>', page, re.S).group(1)
script = re.search(r'<script>(.*?)</script>', page, re.S).group(1)
markup = re.sub(r'<style>.*?</style>|<script.*?</script>', '', page, flags=re.S).strip()
DS = {
 'region_quarterly': ('region_quarterly.json', 'Regional prices, rents and yields', 'Quarterly by region, 2019 Q1 to 2026 Q3: average semi-detached price and new-build price (HM Land Registry UK HPI, Aug 2026); semi-detached and 3-bed rent (ONS Price Index of Private Rents, Oct 2026); net yield after 25% operating costs (30% London); standard new-build house sales and houses in bulk deals (Land Registry Price Paid); private-sector completions (MHCLG Live Table 217). Forecasts to 2028 Q4 blend Knight Frank (Apr 2026) and Savills national price forecasts; the rent forecast is a trend assumption.'),
 'bulk_deals': ('bulk_deals.json', 'Land Registry bulk deals', '5+ new-build houses on one street registered the same day to a non-private buyer (Price Paid category B), Jan 2019 to Aug 2026, with the local open-market new-build median and outcode coordinates (postcodes.io). Deals at 80%+ of local open market are classed as likely SFR/PRS.'),
 'developer_metrics': ('developer_metrics.json', 'Housebuilder reported metrics', 'Average selling prices, sales rates with and without bulk/PRS sales and completions from Barratt Redrow, Persimmon, Taylor Wimpey, Bellway and Vistry results (2025–2026), each with its source.'),
 'area_quarterly': ('area_quarterly.json', 'Council rents and prices by size', 'Quarterly, 2019 Q1 to 2026 Q3, for every council in eight English regions, the regions and England: rent by bedrooms and property type (ONS PIPR), average price by property type (UK HPI), standard new-build house sales and median price (Price Paid), houses in likely SFR bulk deals.'),
 'schemes': ('schemes_sample.json', 'Sample SFR schemes', 'Illustrative schemes generated for the Development economics tab. Not real developments or company figures.'),
}
cfg = {k: {'file': v[0]} for k, v in DS.items()}
sources = ''.join(f'<div><dt>{html.escape(t)}</dt><dd>{html.escape(d)}</dd></div>' for _, t, d in DS.values())
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
<section class="sfr-card wide site-foot" id="sources">
  <h2>Sources</h2>
  <dl class="sfr-defs">{sources}</dl>
  <p class="sfr-note">Contains HM Land Registry data © Crown copyright and database right 2026, ONS and MHCLG data under the Open Government Licence v3.0. Developer figures from company announcements and press coverage. Built {__import__('datetime').date.today().isoformat()}.</p>
</section>
</div>
<script>window.SFR_DATASETS = {json.dumps(cfg)};</script>
<script src="js/d3.v7.9.0.min.js"></script>
<script src="js/dash-shim.js"></script>
<script src="js/uk_regions.js"></script>
<script>
{script}
</script>
<script>window.addEventListener('hashchange', () => {{ const t = document.getElementById('tab-' + location.hash.slice(1)); if (t) t.click(); }});</script>
</body>
</html>
"""
out = out.replace('<script src="uk_regions.js"></script>', '')
open('index.html', 'w').write(out)
print(len(out))
