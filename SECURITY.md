# Security Policy

## Reporting a Vulnerability

If you find a security vulnerability in this project, please report it **privately**:

- Open a GitHub Security Advisory: **Security → Report a vulnerability**
- Or email: nlai741533@gmail.com with the subject `[security] everything-fact-checked`

Please **do not** open a public issue for security-related findings.

We aim to respond within 48 hours and patch critical issues within 7 days.

## Secret Scanning

This repo uses layered secret detection:

| Layer | Tool | When |
|---|---|---|
| Local commits | gitleaks (pre-commit hook) | Before every `git commit` |
| Push/PR | gitleaks (CI job) | On every push and pull request |
| GitHub native | push protection (public repos) | On every push |

If you accidentally commit a secret:
1. **Rotate the credential immediately** — assume it is compromised
2. Do NOT just delete it from the file; it remains in git history
3. Use `git filter-repo` or BFG Repo Cleaner to purge it from history, or contact a maintainer

## Scope

This policy covers the `everything-fact-checked` repository. It does not cover:
- Third-party tools or dependencies (report to their maintainers)
- The user's own environment or credentials
