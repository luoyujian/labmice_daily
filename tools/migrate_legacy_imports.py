"""Explicit legacy cleanup. Stop the application before --apply.

Preview runs against SQLite snapshots in a temporary directory, so even import-time
schema changes cannot touch the source databases. No cleanup is selected by default.
"""
import argparse
import json
import os
from pathlib import Path
import sys
import tempfile
from datetime import datetime, timezone

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--data-dir', type=Path, required=True)
    parser.add_argument('--placeholders', action='store_true')
    parser.add_argument('--rooms', nargs='+', help='Exact legacy room names to clean')
    parser.add_argument('--invalid-codes', action='store_true')
    parser.add_argument('--apply', action='store_true')
    args = parser.parse_args(argv)
    if not (args.placeholders or args.rooms or args.invalid_codes):
        parser.error('Select --placeholders, --rooms, or --invalid-codes explicitly')
    source = args.data_dir.resolve()
    names = ('mouse-manager.db', 'accounts.db')
    for name in names:
        if not (source / name).is_file():
            parser.error(f'Missing database: {source / name}')
    from backend.app.services.database_backup import snapshot
    with tempfile.TemporaryDirectory(prefix='labmice-migration-') as temporary:
        if args.apply:
            backup = source / 'backups' / datetime.now(timezone.utc).strftime('legacy-%Y%m%dT%H%M%S%fZ')
            backup.mkdir(parents=True)
            destination = backup
        else:
            destination = Path(temporary)
        for name in names:
            snapshot(source / name, destination / name)
        if args.apply:
            print(f'Backup: {destination}', flush=True)
        os.environ['DATA_DIR'] = str(source if args.apply else destination)
        from backend.app.database import SessionLocal, engine
        from backend.app.models.models import Mouse, Cage, GenotypeRecord
        from backend.app.services.importer import (
            remove_inferred_parent_placeholders, cleanup_synthetic_room_imports,
            cleanup_invalid_genotype_mice,
        )

        def state(db):
            return {model.__tablename__: {
                str(row.id): {column.name: getattr(row, column.name) for column in model.__table__.columns}
                for row in db.query(model).all()
            } for model in (Mouse, Cage, GenotypeRecord)}

        try:
            with SessionLocal() as db:
                before = state(db)
                if args.placeholders:
                    remove_inferred_parent_placeholders(db)
                    db.flush()
                if args.rooms:
                    cleanup_synthetic_room_imports(db, rooms=args.rooms)
                    db.flush()
                if args.invalid_codes:
                    cleanup_invalid_genotype_mice(db)
                    db.flush()
                after = state(db)
                changes = {table: {
                    'removed': [row for key, row in rows.items() if key not in after[table]],
                    'updated': [{'before': row, 'after': after[table][key]} for key, row in rows.items()
                                if key in after[table] and row != after[table][key]],
                } for table, rows in before.items()}
                print(json.dumps({'applied': args.apply, 'changes': changes}, ensure_ascii=False, default=str, indent=2))
                if args.apply:
                    db.commit()
                else:
                    db.rollback()
        finally:
            engine.dispose()
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
