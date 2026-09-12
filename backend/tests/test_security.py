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
