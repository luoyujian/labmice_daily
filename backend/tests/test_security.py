import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from backend.app.auth import create_access_token
from backend.app.spa import resolve_spa_file


class SecurityTests(unittest.TestCase):
    def test_jwt_rejects_missing_and_known_default_secrets(self):
        for environment in ({}, {'SECRET_KEY': 'mouse-secret-key-2026'}):
            with self.subTest(environment=environment), patch.dict('os.environ', environment, clear=True):
                with self.assertRaisesRegex(RuntimeError, 'SECRET_KEY'):
                    create_access_token({'sub': 'admin'})

    def test_http_spa_does_not_serve_outside_files(self):
        code = r"""
from pathlib import Path
import os
from fastapi.testclient import TestClient
from backend.app import database
root = Path(os.environ['DATA_DIR'])
database.BASE_DIR = str(root)
dist = root / 'frontend' / 'dist'
(dist / 'assets').mkdir(parents=True)
(dist / 'index.html').write_text('SAFE-SPA')
(root / 'private.txt').write_text('PRIVATE-CONTENT')
(dist / 'escape.txt').symlink_to(root / 'private.txt')
from backend.app.main import app
with TestClient(app) as client:
    for path in ('/%2e%2e%2f%2e%2e%2fprivate.txt', '/escape.txt', '/assets/%2e%2e%2f%2e%2e%2fprivate.txt'):
        response = client.get(path)
        assert 'PRIVATE-CONTENT' not in response.text, path
        assert response.status_code in (200, 404), (path, response.status_code)
    assert client.get('/').text == 'SAFE-SPA'
"""
        with tempfile.TemporaryDirectory() as directory:
            result = subprocess.run([sys.executable, '-c', code], capture_output=True, text=True,
                                    env={**os.environ, 'DATA_DIR': directory,
                                         'SECRET_KEY': 'Test-only-key-ABCDEFGHIJKLMNOPQRSTUVWXYZ-0123456789',
                                         'ADMIN_PASSWORD': 'Initial-Test-Pw-2026'})
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_spa_file_resolution_rejects_traversal_absolute_paths_and_symlinks(self):
        with tempfile.TemporaryDirectory() as temporary_directory:
            base = Path(temporary_directory)
            frontend = base / 'dist'
            frontend.mkdir()
            (frontend / 'index.html').write_text('index', encoding='utf-8')
            outside = base / 'private.txt'
            outside.write_text('private', encoding='utf-8')

            self.assertEqual(resolve_spa_file(str(frontend), 'index.html'), frontend / 'index.html')
            self.assertIsNone(resolve_spa_file(str(frontend), '../private.txt'))
            self.assertIsNone(resolve_spa_file(str(frontend), str(outside)))

            link = frontend / 'linked.txt'
            try:
                link.symlink_to(outside)
            except OSError:
                self.skipTest('symbolic links are unavailable')
            self.assertIsNone(resolve_spa_file(str(frontend), 'linked.txt'))


if __name__ == '__main__':
    unittest.main()
