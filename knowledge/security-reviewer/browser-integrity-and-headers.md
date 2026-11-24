# Browser side: SRI, CSP, headers and OWASP Top 10

## Subresource Integrity (MDN)
- SRI lets the browser check that a fetched file (for example from a CDN) "is delivered without unexpected manipulation".
- `integrity="sha384-<base64>"`. Allowed prefixes are `sha256`, `sha384` and `sha512`. If several are given, only the strongest algorithm is checked.
- Cross-origin SRI requires CORS, so the tag **must** include `crossorigin="anonymous"`. Without it the request "will always fail".
- On a hash mismatch the browser refuses to load the file and returns a network error.
- Generate the hash: `cat FILENAME.js | openssl dgst -sha384 -binary | openssl base64 -A`
- Pin exact versions in CDN URLs (for example `pyodide/v0.x.y/full/`) so the hash stays valid.

## Content-Security-Policy (MDN)
- The header controls which resources the page may load. It helps "guard against cross-site scripting attacks".
- Syntax: `Content-Security-Policy: <directive> <value>; <directive> <value>`.
- Useful directives: `default-src` (fallback), `script-src` (JavaScript **and WebAssembly**), `connect-src` (fetch/XHR), `worker-src`, `object-src`, `frame-ancestors`.
- Avoid `'unsafe-eval'` and `'unsafe-inline'` because they defeat "much of the purpose of having a CSP". `'wasm-unsafe-eval'` allows WebAssembly compilation (blocked by default) and is "a much safer alternative to `'unsafe-eval'`".
- A policy can also be set in `<meta http-equiv>`. MDN's page does not say whether `frame-ancestors` works there, so send CSP as a header.
- HelpMate (inference, verify in the browser): Pyodide compiles WebAssembly, so `script-src` probably needs `'wasm-unsafe-eval'` plus the pinned CDN origin.

## Netlify headers
- Use `[[headers]] for = "/*"` with `[headers.values]` in `netlify.toml`, or a `_headers` file in the publish folder. These headers apply only to static files Netlify serves.

## OWASP Top 10 (2025)
A01 Broken Access Control, A02 Security Misconfiguration, A03 Software Supply Chain Failures, A04 Cryptographic Failures, A05 Injection, A06 Insecure Design, A07 Authentication Failures, A08 Software or Data Integrity Failures, A09 Security Logging and Alerting Failures, A10 Mishandling of Exceptional Conditions.
- For a static site like HelpMate, A02, A03 and A08 (headers, CDN scripts, integrity) and A05 (injecting user text into HTML) matter most.

## Sources
- https://developer.mozilla.org/en-US/docs/Web/Security/Subresource_Integrity
- https://developer.mozilla.org/en-US/docs/Web/HTTP/Reference/Headers/Content-Security-Policy
- https://docs.netlify.com/manage/routing/headers/
- https://owasp.org/www-project-top-ten/
- https://owasp.org/Top10/2025/
