# Secrets in the repo and git history

## GitHub secret scanning
- Secret scanning "automatically detects credential leaks". It looks for hardcoded API keys, passwords and tokens.
- It "scans your entire Git history on all branches of your repository".
- It "runs automatically for free" on public repositories.
- When it finds a secret, it raises an alert on the repository's Security tab. For partner secrets, GitHub notifies the provider, who may revoke the credential. Those secrets do not appear in your own alerts.
- Remediation: **rotate the credential immediately.** Removing a secret from git history takes a lot of time and is often unnecessary once the credential is revoked.

## OWASP Secrets Management Cheat Sheet
- Hardcoding is a common failure: "Many organizations have them hardcoded within the source code in plaintext." Keep secrets out of code, config files and Dockerfiles.
- Least privilege: "Secrets must have the minimum privileges assigned to them to enable their required use/role."
- Rotate regularly, and automate rotation where you can.
- CI/CD: avoid "high-value, long-term, or widely scoped credentials" in pipeline variables. Prefer short-lived credentials scoped to each job.
- Detect early with a pre-commit hook, in the IDE or in test workflows. Use more than one tool (for example Yelp's detect-secrets).
- After a leak: revoke at once, rotate to a new secret, and remove the old one from code and logs.
- Secrets should "Never be logged". If they must appear in logs, mask or encrypt them.

## HelpMate secrets to look for
- `NETLIFY_API_TOKEN` (personal access token), the build-hook URL (anyone who has it can trigger builds), and any reCAPTCHA secret.

## Sources
- https://docs.github.com/en/code-security/secret-scanning/introduction/about-secret-scanning
- https://cheatsheetseries.owasp.org/cheatsheets/Secrets_Management_Cheat_Sheet.html
