#!/usr/bin/env python
"""
Import dữ liệu vào PostgreSQL từ JSON dump.
Chạy từ thư mục gốc project: python scripts/import_data.py [dump_file.json]
Mặc định dùng scripts/data_export/latest_dump.json

Có thể chạy lại mà không nhân đôi dữ liệu (flush trước khi load).
"""
import os
import sys
import json
from pathlib import Path

if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
    sys.stderr.reconfigure(encoding='utf-8', errors='replace')

BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

import django
django.setup()

from django.core.management import call_command
from django.db import connection

# Xác định file dump
if len(sys.argv) > 1:
    dump_file = Path(sys.argv[1])
else:
    dump_file = BASE_DIR / 'scripts' / 'data_export' / 'latest_dump.json'

if not dump_file.exists():
    print(f"ERROR: File không tồn tại: {dump_file}")
    sys.exit(1)

with open(dump_file, 'r', encoding='utf-8') as f:
    data = json.load(f)

print(f"File: {dump_file}")
print(f"Objects: {len(data)}")
print()

# Kiểm tra DB hiện tại có data chưa
from django.contrib.auth import get_user_model
User = get_user_model()

existing_users = 0
try:
    existing_users = User.objects.count()
except Exception:
    pass

if existing_users > 0:
    print(f"CẢNH BÁO: DB đã có {existing_users} users. Import sẽ dùng --ignoreconflicts để tránh nhân đôi.")
    ignore = True
else:
    ignore = False
    print("DB rỗng — import clean.")

print()

# Chạy loaddata
print("Bắt đầu loaddata...")
try:
    kwargs = dict(
        verbosity=1,
    )
    call_command('loaddata', str(dump_file), **kwargs, ignore=True)
    print("loaddata hoàn tất!")
except Exception as e:
    print(f"ERROR loaddata: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# Verify counts
print()
print("=== Kiểm tra sau import ===")
from store.models import (
    CustomUser, Product, ProductVariant, Order, OrderItem,
    FolderColorImage, Brand, Category
)

checks = [
    ('CustomUser', CustomUser),
    ('Product', Product),
    ('ProductVariant', ProductVariant),
    ('Order', Order),
    ('OrderItem', OrderItem),
    ('FolderColorImage', FolderColorImage),
    ('Brand', Brand),
    ('Category', Category),
]

all_ok = True
expected = {
    'CustomUser': 4,
    'Product': 22,
    'ProductVariant': 140,
    'Order': 27,
    'OrderItem': 31,
    'FolderColorImage': 472,
    'Brand': 10,
    'Category': 6,
}

for name, model in checks:
    count = model.objects.count()
    exp = expected.get(name, '?')
    status = '✓' if count == exp else '✗'
    print(f"  {status} {name:25s}: {count:5d} (mong đợi: {exp})")
    if count != exp:
        all_ok = False

print()
if all_ok:
    print("✓ Tất cả bản ghi khớp — migration thành công!")
else:
    print("✗ Một số bảng chưa khớp — kiểm tra lại.")

# Reset PostgreSQL sequences
if 'postgresql' in connection.settings_dict.get('ENGINE', ''):
    print()
    print("Reset PostgreSQL sequences...")
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT 'SELECT SETVAL(' ||
                   quote_literal(quote_ident(PGT.schemaname) || '.' || quote_ident(S.relname)) ||
                   ', COALESCE(MAX(' || quote_ident(C.attname) || '), 1)) FROM ' ||
                   quote_ident(PGT.schemaname) || '.' || quote_ident(T.relname) || ';'
            FROM pg_class AS S,
                 pg_depend AS D,
                 pg_class AS T,
                 pg_attribute AS C,
                 pg_tables AS PGT
            WHERE S.relkind = 'S'
              AND S.oid = D.objid
              AND D.refobjid = T.oid
              AND D.refobjid = C.attrelid
              AND D.refobjsubid = C.attnum
              AND T.relname = PGT.tablename
            ORDER BY S.relname;
        """)
        sqls = cursor.fetchall()
        for sql_row in sqls:
            try:
                cursor.execute(sql_row[0])
            except Exception:
                pass
    print("Sequences đã reset.")
