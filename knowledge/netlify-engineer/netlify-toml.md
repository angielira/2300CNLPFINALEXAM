# netlify.toml

- Usually at the repo root; settings override the Netlify UI.
- `[build]`: `base`, `publish`, `command`, `environment`; `[build.environment]` for variables.
- Context overrides: `[context.production]`, `[context.deploy-preview]`, branch contexts.
- `[[redirects]]` and `[[headers]]` (not context-aware).
- Don't store secrets in the file; use the UI/CLI/API.

## Sources
- https://docs.netlify.com/build/configure-builds/file-based-configuration/
