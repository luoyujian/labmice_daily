"""Small dependency-free smoke check; full unittest suite remains the release gate."""
from pathlib import Path
import sys
import tempfile
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from backend.app.spa import resolve_spa_file

with tempfile.TemporaryDirectory() as folder:
    root = Path(folder)
    dist = root / 'dist'
    dist.mkdir()
    (dist / 'index.html').write_text('index')
    (root / 'private').write_text('private')
    (dist / 'escape').symlink_to(root / 'private')
    assert resolve_spa_file(dist, 'index.html') == dist / 'index.html'
    for path in ('../private', 'escape', str(root / 'private'), 'missing', '\x00'):
        assert resolve_spa_file(dist, path) is None, path
suite = unittest.defaultTestLoader.discover(str(Path(__file__).resolve().parents[1] / 'backend/tests'), pattern='test_credentials.py')
raise SystemExit(not unittest.TextTestRunner(verbosity=2).run(suite).wasSuccessful())
