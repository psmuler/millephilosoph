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
