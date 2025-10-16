# Millephilosoph

Personal site generated with [Hugo](https://gohugo.io/) and the [PaperMod theme](https://github.com/adityatelange/hugo-PaperMod).

## Key Files and Folders
- `hugo.yaml` – site-wide configuration (title, menus, theme params, social icons).
- `content/` – Markdown sources for pages and posts; add new articles under `content/posts/`.
- `layouts/` – overrides for PaperMod templates; use for bespoke layout tweaks.
- `static/` – assets served as-is (images, favicons, robots.txt, etc.).
- `themes/PaperMod/` – theme submodule; avoid editing directly unless you plan to maintain a fork.
- `CNAME` – optional file defining the site’s custom domain (kept at repository root).

## Local Development
1. Install Hugo Extended (`brew install hugo` v0.100+ recommended).
2. Run `hugo server -D` to launch the live preview at `http://localhost:1313`.
3. Edit files in `content/`, `layouts/`, or `static/`; the server reloads automatically.

## Deploying to GitHub Pages
1. Set `baseURL` in `hugo.yaml` to your published site URL (e.g. `https://<user>.github.io/`).
2. Build the site: `hugo --minify` (outputs to `public/`).
3. Push the contents of `public/` to the Pages branch:
   - User/Org sites: push `public/` to the `main` branch of `<user>.github.io`.
   - Project sites: push `public/` to the `gh-pages` branch of the project repo.
   Use either a separate clone of `public/`, `git subtree`, or a GitHub Action (PaperMod docs include a sample workflow).
4. Enable GitHub Pages under **Settings › Pages**, pointing to the branch that serves the built files.

## Custom Domain Setup
1. Update the `CNAME` file with your desired domain (e.g. `www.example.com`).
2. Commit and push `CNAME` alongside your site so GitHub Pages keeps the domain binding.
3. In your DNS provider, create:
   - `A` records pointing to GitHub Pages IPs (if using an apex domain), and/or
   - `CNAME` record pointing to `<user>.github.io` (for subdomains).
4. In GitHub Pages settings, add the same custom domain and enable HTTPS once verified.

Refer to [GitHub Pages documentation](https://docs.github.com/pages) for detailed DNS values and automation options.

## Google Analytics Page View Data
Home page ordering uses Google Analytics 4 page view counts stored at
`data/analytics/pageviews.yaml`. A helper script is provided to pull the latest
metrics via the GA Data API and refresh this file.

1. Create a **service account** in Google Cloud with access to the GA4 property
   and download the JSON credentials file. Add the service account email as a
   *Viewer* on the GA4 property.
2. Install the script dependencies (once):
   ```bash
   pip install google-analytics-data PyYAML
   ```
3. Run the update script (adjust paths and property ID):
   ```bash
   python scripts/update_pageviews.py \
     --property-id=<GA4_PROPERTY_ID> \
     --credentials=/path/to/service-account.json \
     --start-date=2023-01-01 \
     --end-date=today \
     --verbose
   ```
   The script fetches `screenPageViews` grouped by `pagePath`, merges them into
   `data/analytics/pageviews.yaml`, and logs a summary. Use `--dry-run` to test
   without writing.
4. Commit the updated YAML and rebuild (`hugo --environment production`) so the
   home page reflects the latest popularity ranking.

Schedule this command (cron, GitHub Actions with secrets, etc.) to keep the
metrics fresh.

### GitHub Actions automation

A workflow at `.github/workflows/update-pageviews.yml` can run nightly:

1. Add two repository secrets:
   - `GA_SERVICE_ACCOUNT_JSON`: paste the full JSON credential.
   - `GA_PROPERTY_ID`: numeric GA4 property ID (not the `G-` measurement ID).
2. The workflow installs dependencies, writes the credentials into a temporary
   file, runs `scripts/update_pageviews.py`, commits any changed counts, and
   pushes back to `main`.
3. Trigger it manually from the Actions tab (workflow dispatch) or allow the
   scheduled cron (`0 3 * * *`, i.e. 12:00 JST) to keep the ranking current.
