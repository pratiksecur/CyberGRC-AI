# CyberGRC-AI Security Runbook

## Release gates

- No secrets in source or Docker image layers.
- Production uses PostgreSQL, not SQLite.
- Production docs are disabled unless explicitly approved.
- CORS contains only approved origins.
- Trusted hosts are configured for the public API hostname.
- HTTPS is enforced at the edge.
- HSTS is enabled after HTTPS verification.
- Metrics are not publicly exposed without authentication/network controls.
- Dependency audit is clean or every exception is documented.
- Full pytest regression passes.
- Tenant-isolation tests pass.

## Incident basics

When a security incident is suspected:

1. Preserve logs and request IDs.
2. Restrict or disable affected credentials/tokens.
3. Isolate affected service(s) if required.
4. Preserve relevant database and evidence snapshots.
5. Determine tenant/data scope before notifying stakeholders.
6. Rotate compromised secrets.
7. Restore from a known-good backup only after evidence preservation.
8. Run tenant-isolation and authorization regression tests before recovery.

Do not put passwords, tokens, evidence contents, or sensitive request bodies into logs.
