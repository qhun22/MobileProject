#!/usr/bin/env python
"""
Upload toàn bộ media/ lên Cloudflare R2.
Chạy: python scripts/upload_media_r2.py

Yêu cầu: R2_ACCOUNT_ID, R2_ACCESS_KEY_ID, R2_SECRET_ACCESS_KEY, R2_BUCKET_NAME trong .env
"""
import os
import sys
from pathlib import Path

if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
    sys.stderr.reconfigure(encoding='utf-8', errors='replace')

BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))

# Load .env
from dotenv import load_dotenv
load_dotenv(BASE_DIR / '.env')

import boto3
from botocore.exceptions import ClientError

ACCOUNT_ID = os.getenv('R2_ACCOUNT_ID', '')
ACCESS_KEY = os.getenv('R2_ACCESS_KEY_ID', '')
SECRET_KEY = os.getenv('R2_SECRET_ACCESS_KEY', '')
BUCKET = os.getenv('R2_BUCKET_NAME', '')

if not all([ACCOUNT_ID, ACCESS_KEY, SECRET_KEY, BUCKET]):
    print("ERROR: Thiếu R2 credentials. Cần set trong .env:")
    print("  R2_ACCOUNT_ID=...")
    print("  R2_ACCESS_KEY_ID=...")
    print("  R2_SECRET_ACCESS_KEY=...")
    print("  R2_BUCKET_NAME=...")
    sys.exit(1)

s3 = boto3.client(
    's3',
    endpoint_url=f'https://{ACCOUNT_ID}.r2.cloudflarestorage.com',
    aws_access_key_id=ACCESS_KEY,
    aws_secret_access_key=SECRET_KEY,
    region_name='auto',
)

MEDIA_ROOT = BASE_DIR / 'media'

if not MEDIA_ROOT.exists():
    print(f"ERROR: Media folder không tồn tại: {MEDIA_ROOT}")
    sys.exit(1)

# Collect all files
all_files = list(MEDIA_ROOT.rglob('*'))
files = [f for f in all_files if f.is_file()]
total = len(files)
total_size = sum(f.stat().st_size for f in files)
print(f"Upload {total} files ({total_size / 1024 / 1024:.1f} MB) lên R2 bucket '{BUCKET}'")
print()

import mimetypes
# Windows mimetypes missing some types — add manually
mimetypes.add_type('image/webp', '.webp')
mimetypes.add_type('image/avif', '.avif')
mimetypes.add_type('image/heic', '.heic')

uploaded = 0
skipped = 0
errors = 0

for i, filepath in enumerate(files, 1):
    key = str(filepath.relative_to(MEDIA_ROOT)).replace('\\', '/')
    content_type, _ = mimetypes.guess_type(str(filepath))
    content_type = content_type or 'application/octet-stream'

    try:
        s3.upload_file(
            str(filepath),
            BUCKET,
            key,
            ExtraArgs={'ContentType': content_type},
        )
        uploaded += 1
        if i % 50 == 0 or i == total:
            print(f"  [{i}/{total}] {key}")
    except ClientError as e:
        print(f"  [ERROR] {key}: {e}")
        errors += 1

print()
print(f"Kết quả: {uploaded} uploaded, {skipped} skipped, {errors} errors")

if errors == 0:
    print("✓ Upload hoàn tất!")
else:
    print(f"✗ {errors} lỗi — kiểm tra lại.")
    sys.exit(1)
