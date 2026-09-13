"""Run the browser-test server using disposable data, never an existing database."""
import os
from pathlib import Path
import secrets
import sys
import tempfile

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
with tempfile.TemporaryDirectory(prefix='labmice-browser-') as data:
    os.environ['DATA_DIR'] = data
    os.environ['SECRET_KEY'] = secrets.token_urlsafe(48)
    os.environ['ADMIN_PASSWORD'] = 'Browser-Fixture-Pw-2026'
    from backend.app.main import app
    from backend.app.database import SessionLocal
    from backend.app.models.models import Cage, Mouse, Room
    with SessionLocal() as db:
        db.add(Room(name='浏览器测试鼠房', category='繁育鼠房'))
        cage = Cage(room='浏览器测试鼠房', cage_code='Test-A1')
        db.add(cage)
        db.flush()
        db.add_all(Mouse(mouse_code=f'Test-{i:04d}', cage_id=cage.id, strain='WT', gender='M', status='在笼') for i in range(501))
        db.commit()
    import uvicorn
    uvicorn.run(app, host='127.0.0.1', port=8000)
