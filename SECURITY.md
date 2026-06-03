# Security Policy

## Reporting a Vulnerability

If you find a security vulnerability in this project, please report it **privately**:

- Open a GitHub Security Advisory: **Security → Report a vulnerability**
- Or email: nlai741533@gmail.com with the subject `[security] EFC-Plugin`

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

## Network safety (SSRF guard)

`efc verify` fetches the source URLs found in evidence records, and those URLs
may come from untrusted reports or pull requests. To prevent server-side request
forgery (SSRF), `efc verify`:

- accepts only `http`/`https` schemes (no `file://`, `gopher://`, etc.);
- resolves each host and **refuses any URL that resolves to a non-public
  address** — loopback, private, link-local (including the cloud metadata
  endpoint `169.254.169.254`), reserved, multicast, or unspecified IPs;
- re-validates the target of every HTTP redirect, so a public URL cannot bounce
  to an internal one.

This still relies on standard-library `urllib`; it is defense against accidental
and opportunistic SSRF, not a substitute for running untrusted checks in a
network-isolated sandbox when the threat model warrants it.

## Scope

This policy covers the EFC-Plugin repository. It does not cover:
- Third-party tools or dependencies (report to their maintainers)
- The user's own environment or credentials
