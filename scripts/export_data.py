#!/usr/bin/env python
"""
Export toàn bộ dữ liệu từ SQLite ra JSON (UTF-8 safe).
Chạy từ thư mục gốc project: python scripts/export_data.py
Output: scripts/data_export/dump_YYYYMMDD_HHMMSS.json
"""
import os
import sys
import json
import sqlite3
from datetime import datetime
from pathlib import Path

# Fix Windows console encoding
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
    sys.stderr.reconfigure(encoding='utf-8', errors='replace')

# Setup Django
BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

import django
django.setup()

from django.core.management import call_command

EXPORT_DIR = BASE_DIR / 'scripts' / 'data_export'
EXPORT_DIR.mkdir(parents=True, exist_ok=True)

timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
output_file = EXPORT_DIR / f'dump_{timestamp}.json'

# Apps cần dump — theo thứ tự tránh FK conflict
APPS_TO_DUMP = [
    'contenttypes',
    'auth.group',
    'sites',
    'socialaccount.socialapp',
    'store',
]

print(f"Bắt đầu export dữ liệu...")
print(f"Output: {output_file}")
print()

all_objects = []

for app in APPS_TO_DUMP:
    import io
    buf = io.StringIO()
    try:
        call_command(
            'dumpdata', app,
            natural_foreign=True,
            natural_primary=True,
            indent=0,
            stdout=buf,
        )
        buf.seek(0)
        data = json.loads(buf.read())
        count = len(data)
        all_objects.extend(data)
        print(f"  {app:35s} {count:5d} objects")
    except Exception as e:
        print(f"  {app:35s} ERROR: {e}")

print()
print(f"Tổng: {len(all_objects)} objects")

# Ghi ra file UTF-8
with open(output_file, 'w', encoding='utf-8') as f:
    json.dump(all_objects, f, ensure_ascii=False, indent=2)

file_size = output_file.stat().st_size
print(f"File: {output_file} ({file_size:,} bytes)")

# Verify — đọc lại để chắc chắn
with open(output_file, 'r', encoding='utf-8') as f:
    verify = json.load(f)
print(f"Verify: {len(verify)} objects đọc lại thành công")

# Tạo latest symlink (ghi đường dẫn mới nhất)
latest_file = EXPORT_DIR / 'latest_dump.json'
import shutil
shutil.copy2(output_file, latest_file)
print(f"Latest: {latest_file}")

# In record counts
print()
print("=== Record counts ===")
db_path = BASE_DIR / 'db.sqlite3'
conn = sqlite3.connect(str(db_path))
cur = conn.cursor()
cur.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")
tables = [r[0] for r in cur.fetchall() if not r[0].startswith('sqlite_')]
total = 0
for t in tables:
    cur.execute(f'SELECT COUNT(*) FROM "{t}"')
    c = cur.fetchone()[0]
    if c > 0:
        print(f"  {t:50s} {c:6d}")
        total += c
conn.close()
print(f"  {'TOTAL':50s} {total:6d}")
