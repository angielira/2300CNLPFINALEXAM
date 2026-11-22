# Build hooks

- A build hook is a unique URL that triggers a build and deploy on POST: `https://api.netlify.com/build_hooks/<id>`.
- Create: Project configuration > Build & deploy > Continuous deployment > Build hooks > Add build hook.
- Optional query params: `trigger_branch`, `trigger_title`, `clear_cache`; a POST body is exposed as `INCOMING_HOOK_BODY`.
- Builds must be active. Treat the URL as a secret.
- Scheduling: a Netlify scheduled function or a GitHub Actions cron can POST the hook.

## Sources
- https://docs.netlify.com/build/configure-builds/build-hooks/
- https://www.netlify.com/blog/how-to-schedule-deploys-with-netlify
