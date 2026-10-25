# UK SFR Market Monitor (standalone site)

A static copy of the claude.ai dashboard. Vercel serves `index.html`, `js/` and `data/` as they are; there is no server or build step.

## Deploy
- **GitHub Pages:** in the repository's Settings → Pages, set Source to "Deploy from a branch", branch `main`, folder `/ (root)`. Every push to `main` republishes the site.
- **From Claude:** add a Vercel token to the cloud environment as `VERCEL_TOKEN`, start a new session, and ask Claude to run `./deploy.sh`.
- **From your computer:** install Node, then in this folder run `npx vercel deploy --prod` and log in when asked.
- **From GitHub:** push this folder to a repository and import it at vercel.com/new (framework preset: Other).

## Update
Replace the files in `data/` (same names and columns), run `python3 build.py` if `dashboard.html` changed, and deploy again.

## Notes
- The Development economics tab uses sample schemes (`data/schemes_sample.json`) unless a visitor drops in their own spreadsheet, which stays in their browser.
- The site is public to anyone with the address. Turn on Vercel Authentication or password protection if it should be private.
