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
