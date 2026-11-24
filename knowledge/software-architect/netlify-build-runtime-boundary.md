# Netlify: build time vs browser (the boundary to guard)

## Environment variables
- You can set variables in the Netlify UI, CLI or API (stored on Netlify) or in `netlify.toml` (stored in the repo). Netlify recommends the UI, CLI or API "to avoid storing sensitive values in your repository".
- Variables set in `netlify.toml` override ones with the same key set in the UI, CLI or API.
- Scopes: **Builds**, **Functions**, **Runtime** (forms and signed proxy redirects) and **Post processing** (snippet injection). By default a variable applies to all scopes. Choosing scopes needs a Pro or Enterprise plan.
- Deploy contexts: Production, Deploy Previews, Branch deploys, Preview server, Local development.
- Build variables are **not** available to the site after the build. You have to "take extra steps" to expose them. "If you inject values into the site using a build script or snippet injection, make sure to only include non-sensitive values."
- The build system "doesn't read `.env` files". Import those variables into Netlify instead.
- Read-only build variables include `NETLIFY`, `CONTEXT`, `BRANCH`, `COMMIT_REF`, `URL`, `DEPLOY_URL`, `SITE_ID`.

## Headers
- Set headers with a `_headers` file in the publish folder or with `[[headers]]` (`for`, `[headers.values]`) in `netlify.toml`.
- Custom headers apply only to files Netlify serves from its own storage. They do not apply to proxied content or functions.
- Headers are global for every build. You cannot scope them by branch or context unless you copy a different `_headers` file in the build command.

## HelpMate boundary (project rule, see docs/06-netlify-architecture.md)
- Python (NLTK, spaCy, training) runs only in the build command and writes `site/data/*.json`.
- The browser gets static files, Pyodide (NLTK, NumPy) and JavaScript only. No server, no database, no secrets in `site/`.

## Sources
- https://docs.netlify.com/build/environment-variables/overview/
- https://docs.netlify.com/build/configure-builds/environment-variables/
- https://docs.netlify.com/manage/routing/headers/
