#!/usr/bin/env python
"""
Kiểm tra số lượng bản ghi sau migration.
Chạy: python scripts/verify_data.py
"""
import os, sys
from pathlib import Path

if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')

BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
import django
django.setup()

from store.models import (
    CustomUser, Product, ProductVariant, ProductDetail,
    ProductSpecification, FolderColorImage, ImageFolder,
    Order, OrderItem, Cart, CartItem,
    Brand, Category, Banner, BlogPost,
    Coupon, CouponUsage, Address, Wishlist,
    ProductReview, HangingProduct, HotSaleProduct,
    VNPayPayment, PendingQRPayment, Newsletter,
    SiteVisit, UserBrowseLog,
)
from django.contrib.sites.models import Site
from allauth.socialaccount.models import SocialApp

EXPECTED = {
    'CustomUser': (CustomUser, 4),
    'Product': (Product, 22),
    'ProductVariant': (ProductVariant, 140),
    'ProductDetail': (ProductDetail, 22),
    'ProductSpecification': (ProductSpecification, 22),
    'FolderColorImage': (FolderColorImage, 472),
    'ImageFolder': (ImageFolder, 24),
    'Order': (Order, 27),
    'OrderItem': (OrderItem, 31),
    'Cart': (Cart, 4),
    'CartItem': (CartItem, 4),
    'Brand': (Brand, 10),
    'Category': (Category, 6),
    'Banner': (Banner, 13),
    'BlogPost': (BlogPost, 5),
    'Coupon': (Coupon, 3),
    'CouponUsage': (CouponUsage, 3),
    'Address': (Address, 4),
    'Wishlist': (Wishlist, 4),
    'ProductReview': (ProductReview, 5),
    'HangingProduct': (HangingProduct, 7),
    'HotSaleProduct': (HotSaleProduct, 20),
    'VNPayPayment': (VNPayPayment, 5),
    'PendingQRPayment': (PendingQRPayment, 8),
    'Newsletter': (Newsletter, 4),
    'SiteVisit': (SiteVisit, 596),
    'UserBrowseLog': (UserBrowseLog, 198),
    'Site': (Site, 1),
    'SocialApp': (SocialApp, 1),
}

print("=== Kiem tra du lieu sau migration ===\n")
all_ok = True
for name, (model, exp) in EXPECTED.items():
    try:
        count = model.objects.count()
        ok = count == exp
        mark = 'OK' if ok else 'FAIL'
        print(f"  [{mark}] {name:30s}: {count:5d} / {exp}")
        if not ok:
            all_ok = False
    except Exception as e:
        print(f"  [ERR] {name:30s}: ERROR - {e}")
        all_ok = False

print()
# Check superuser
admins = CustomUser.objects.filter(is_superuser=True)
print(f"Superusers: {admins.count()}")
for u in admins:
    print(f"  - {u.email} (active={u.is_active})")

print()
db_info = __import__('django').db.connection.settings_dict
engine = db_info.get('ENGINE', '?')
print(f"Database engine: {engine}")

print()
if all_ok:
    print(">>> TẤT CẢ DỮ LIỆU KHỚP - MIGRATION THÀNH CÔNG!")
else:
    print(">>> MỘT SỐ BẢNG CHƯA KHỚP - CẦN KIỂM TRA LẠI")
    sys.exit(1)
