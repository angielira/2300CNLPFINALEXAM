# Netlify: secret scanning, env vars and Forms spam protection

## Secret scanning on Netlify
- Netlify "scans your repository code and build output files for the existence of secret values", which covers every file in the build, including generated files.
- If it finds one, "it fails the build and adds the location of the secret values to the deploy log". Scanning runs before publish.
- It only searches for secret values longer than four characters that are not booleans.
- Settings: `SECRETS_SCAN_ENABLED` (default `true`; `false` turns off all protection), `SECRETS_SCAN_OMIT_KEYS`, `SECRETS_SCAN_OMIT_PATHS`.
- **Smart detection** scans for likely secrets without any setup (Personal, Pro and Enterprise plans). Use `SECRETS_SCAN_SMART_DETECTION_OMIT_VALUES` to safelist false positives and `SECRETS_SCAN_SMART_DETECTION_ENABLED=false` to turn it off.
- Review rule: any use of an OMIT setting or `SECRETS_SCAN_ENABLED=false` needs a written reason.

## Environment variables
- Store sensitive values in the Netlify UI, CLI or API, not in `netlify.toml`, "to avoid storing sensitive values in your repository".
- Mark sensitive values as "Contains secret values". Limit scopes so values are used only where they are needed.
- Values injected into the site at build time must be non-sensitive. The build does not read `.env` files.

## Forms spam protection
- Netlify filters every submission with Akismet. Flagged submissions go to "Spam submissions".
- Honeypot: add `netlify-honeypot="bot-field"` to the `<form>` and hide the field. Netlify "will quietly reject" a submission that fills it in. With AJAX, include the field in the POST body (`FormData()` does this automatically).
- reCAPTCHA 2: add `data-netlify-recaptcha="true"` to the form and to an empty `<div>`. Netlify validates it server-side. One Netlify-provided challenge per page. A custom reCAPTCHA uses `SITE_RECAPTCHA_KEY` (Builds + Runtime) and `SITE_RECAPTCHA_SECRET` (Runtime).

## Forms privacy (HelpMate review points, not from the docs)
- Submissions are stored in Netlify and read back with a token at build time. Check that the rating form asks for no names or emails, and that the build never writes raw comments or questions that could identify someone into `site/data/`.

## Sources
- https://docs.netlify.com/build/environment-variables/secrets-controller/
- https://docs.netlify.com/build/environment-variables/overview/
- https://docs.netlify.com/build/configure-builds/environment-variables/
- https://docs.netlify.com/manage/forms/spam-filters/
