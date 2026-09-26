# Security Policy

## Reporting a vulnerability

This is a demo/educational project with no dedicated security team or SLA. If you find a
security issue, please **do not open a public GitHub issue**. Instead, contact the repository
owner directly (see the repository's contact/owner information) with:

- A description of the issue and its potential impact
- Steps to reproduce
- Any suggested fix, if you have one

You should expect an acknowledgment within a few business days. There is no bug-bounty program
attached to this project.

## Known, accepted limitations (not vulnerabilities to report)

These are documented design decisions, tracked in [`spec.md`](spec.md) and
[`performance/PERFORMANCE_REVIEW.md`](performance/PERFORMANCE_REVIEW.md):

- **No authentication/authorization.** Every API call acts as an implicit single "physician"
  actor. This app is not intended to be exposed on an untrusted network as-is — see
  "Deployment security expectations" below.
- **`CORS_ALLOW_ORIGINS` defaults to `*`.** Fine for local/demo use; set it explicitly (see
  `.env.example`) before deploying anywhere reachable by other origins.
- **No rate limiting.** A single SQLite writer already caps write throughput (see the
  performance review) — this is a demo constraint, not a defense against abuse.
- **`GET /api/audit` has no pagination.** An unbounded-history data exposure isn't the concern
  here (it's audit data, not secrets) but it is a resource-exhaustion vector at scale — tracked
  as a performance gap, not a security one.

## Deployment security expectations

If you deploy this beyond your own machine:

1. Put it behind authentication (a reverse proxy with auth, or add real auth to the API — not
   included here).
2. Set `CORS_ALLOW_ORIGINS` to the exact origin(s) that should be allowed.
3. Don't expose `/docs` (FastAPI's auto-generated OpenAPI UI) publicly unless you intend to.
4. Use a real database (Postgres, etc.) rather than the bundled SQLite file for anything beyond
   a demo — see the performance review for why.
