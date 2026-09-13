# Work log (append only)

## 2026-09-13: Security integration and executable test baseline

- Started from remote `fix/transfer-feedback-state` (032314b); cherry-picked the
  earlier static-file/auth fix (6d72212). Claude's seven commits and patch were
  unavailable, so credential and legacy-cleanup changes were reconstructed from
  the handoff. No claim that the absent commits themselves were tested.
- Preserved the existing transfer-state guard and its real ORM regression tests.
- Reject example credentials and trivially repetitive values. Keep credential and
  SPA helpers free of third-party imports.
- Removed global legacy cleanup from startup AND both Excel import entrypoints.
  The extra import paths were a remaining route to deleting unrelated records.
- Added explicit migration selections, temporary-snapshot previews, pre-apply
  backups of both databases, transactional cleanup and operator documentation.
- Added backend regression and frontend build CI; Docker publishing depends on it.
- Verified: Python 3.13.15, exact backend uv.lock dependencies; 77 unittest tests
  passed, including SQLite preview byte preservation, apply/backups, repeated
  startup/import preservation, and HTTP encoded traversal/symlink checks.
- Verified: frozen frontend lockfile installation and production build with local
  Node 24.19.0 / pnpm 11.19.0. CI uses the Docker-compatible Node 22 / pnpm 10.32.1.
- Smoke helper is newly reconstructed and narrower than Claude's reported 41-check
  helper. Full tests above supersede stub-based ORM verification.
- Not yet verified: real NAS deployment, production-data migration, phone browser
  interaction. No production database touched; no image deployed.
- Next: selector pagination (including TodoReminders and TransferRequests), phone
  layout and common workflows, PWA over NAS HTTPS. Coordinate genotype_3 work with
  Claude; ear-tag/transfer identity changes need a dedicated tested migration.

## 2026-09-13: Mobile workflow adaptation

- Reflow cage, transfer and todo forms on phones, enlarge touch controls, use a
  single cage-card column, and wrap room selectors and long todo links.
- Fetch all pages for transfer candidates and todo relations. Reject partial
  failures; protect candidate lists from stale responses after changing rooms.
- Added three pagination tests, including the 501st mouse and later-page failure.
- Added disposable 501-mouse browser fixtures and phone (360/390px) / desktop
  workflow checks to CI. Local agent-browser daemon cannot bind its socket and
  Chromium download times out; browser verification is delegated to CI execution.
- Local production build and three pagination tests pass. CI results pending.
- No NAS deployment or real-device Safari verification yet.
