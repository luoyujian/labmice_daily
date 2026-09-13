# Legacy import cleanup

Application startup and ordinary Excel imports no longer perform whole-database
legacy deletion. Existing rows, including C57-labelled mice and cages in rooms
previously hard-coded by the importer, remain in place.

Only use this tool for records confirmed to be artifacts of the original import.
A room selection can remove its cages and delete or archive its mice. Invalid-code
cleanup can remove mice and genotype records, including codes such as C57.

Stop the application before applying cleanup. Run from the repository root using
the backend Python environment. Supply the directory holding both SQLite files:

```sh
backend/.venv/bin/python tools/migrate_legacy_imports.py --data-dir /path/to/data --rooms 'confirmed legacy room'
```

Preview uses temporary SQLite snapshots and leaves both original databases untouched.
It prints every removed or updated mouse, cage and genotype row. Available selections
are `--placeholders`, `--rooms NAME [NAME ...]`, and `--invalid-codes`; none is selected
automatically. Add `--apply` after reviewing the preview. Apply first snapshots both
databases into `DATA_DIR/backups/legacy-TIMESTAMP/`, then commits cleanup in one business
database transaction. Foreign-key conflicts abort cleanup; investigate them rather
than disabling constraints. Never apply while the server is accepting writes.

Keep both backup files together for recovery. Before restoring, stop the application
and preserve the failed installation. Use SQLite backup restoration to account for
WAL files; do not copy a .db file over an open database.

Startup still normalizes strain/status labels, euthanasia ownership and legacy room
and member category labels. This migration tool does not change those normalizations.
