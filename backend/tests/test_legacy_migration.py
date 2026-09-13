import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from backend.app.database import Base
from backend.app.models.models import Cage, Mouse, GenotypeRecord

ROOT = Path(__file__).resolve().parents[2]


class LegacyMigrationTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.path = Path(self.temp.name)
        self.engine = create_engine(f'sqlite:///{self.path / "mouse-manager.db"}')
        Base.metadata.create_all(self.engine)
        import sqlite3
        with sqlite3.connect(self.path / 'accounts.db') as connection:
            connection.execute('CREATE TABLE marker (value TEXT)')
            connection.execute("INSERT INTO marker VALUES ('keep accounts')")
        with Session(self.engine) as db:
            cage = Cage(room='常规鼠房', cage_code='A1')
            db.add(cage)
            db.flush()
            mouse = Mouse(mouse_code='C57', cage_id=cage.id, status='在笼')
            db.add(mouse)
            db.flush()
            db.add(GenotypeRecord(mouse_id=mouse.id, mouse_code='C57'))
            db.commit()

    def tearDown(self):
        self.engine.dispose()
        self.temp.cleanup()

    def run_tool(self, *args):
        return subprocess.run([sys.executable, str(ROOT / 'tools/migrate_legacy_imports.py'),
                               '--data-dir', str(self.path), *args], cwd=ROOT,
                              text=True, capture_output=True)

    def test_requires_explicit_selection(self):
        self.assertEqual(self.run_tool().returncode, 2)

    def test_preview_keeps_both_databases_byte_identical(self):
        before = {p.name: p.read_bytes() for p in self.path.glob('*.db')}
        result = self.run_tool('--invalid-codes')
        self.assertEqual(result.returncode, 0, result.stderr)
        changes = json.loads(result.stdout)['changes']
        self.assertEqual(len(changes['mice']['removed']), 1)
        self.assertEqual(len(changes['genotype_records']['removed']), 1)
        self.assertEqual(before, {p.name: p.read_bytes() for p in self.path.glob('*.db')})

    def test_apply_backs_up_both_databases_before_cleanup(self):
        result = self.run_tool('--invalid-codes', '--apply')
        self.assertEqual(result.returncode, 0, result.stderr)
        with Session(self.engine) as db:
            self.assertEqual(db.query(Mouse).count(), 0)
            self.assertEqual(db.query(GenotypeRecord).count(), 0)
            self.assertEqual(db.query(Cage).count(), 1)
        backup = next((self.path / 'backups').iterdir())
        self.assertTrue((backup / 'accounts.db').is_file())
        backup_engine = create_engine(f'sqlite:///{backup / "mouse-manager.db"}')
        with Session(backup_engine) as db:
            self.assertEqual(db.query(Mouse).one().mouse_code, 'C57')
            self.assertEqual(db.query(GenotypeRecord).count(), 1)
        backup_engine.dispose()

    def test_room_cleanup_is_explicit(self):
        result = self.run_tool('--rooms', 'some other room', '--apply')
        self.assertEqual(result.returncode, 0, result.stderr)
        with Session(self.engine) as db:
            self.assertEqual(db.query(Cage).count(), 1)
            self.assertEqual(db.query(Mouse).count(), 1)

    def test_startup_and_excel_import_preserve_existing_records(self):
        code = '''
import tempfile
from pathlib import Path
from fastapi.testclient import TestClient
from openpyxl import Workbook
from backend.app.main import app
from backend.app.database import SessionLocal
from backend.app.models.models import Mouse, Cage, GenotypeRecord
from backend.app.services.importer import import_single_excel_file, import_local_excel_folder
for _ in range(2):
    with TestClient(app) as client:
        assert client.get('/api/health').status_code == 200
with tempfile.TemporaryDirectory() as folder:
    file = Path(folder) / 'empty.xlsx'
    Workbook().save(file)
    with SessionLocal() as db:
        import_single_excel_file(db, str(file))
        import_local_excel_folder(db, folder)
        assert db.query(Mouse).filter_by(mouse_code='C57').count() == 1
        assert db.query(Cage).filter_by(room='常规鼠房').count() == 1
        assert db.query(GenotypeRecord).filter_by(mouse_code='C57').count() == 1
'''
        result = subprocess.run([sys.executable, '-c', code], cwd=ROOT, capture_output=True, text=True,
                                env={**os.environ, 'DATA_DIR': str(self.path),
                                     'SECRET_KEY': 'Test-only-key-ABCDEFGHIJKLMNOPQRSTUVWXYZ-0123456789',
                                     'ADMIN_PASSWORD': 'Initial-Test-Pw-2026'})
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
