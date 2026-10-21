# KẾ HOẠCH CHUYỂN ĐỔI DỮ LIỆU & DEPLOY LÊN RENDER

> **Ngày lập:** 2026-10-21  
> **Trạng thái:** Chờ phê duyệt — CHƯA thực hiện bất kỳ thay đổi nào  
> **Mục tiêu:** Deploy Django lên Render với toàn bộ dữ liệu từ SQLite được giữ nguyên

---

## PHẦN 1 — THỰC TRẠNG DATABASE SQLite

### 1.1 Thông tin database

| Mục | Giá trị |
|---|---|
| **Vị trí** | `D:\DataFolder\ProjectPython\qhun22mobile\db.sqlite3` |
| **Kích thước** | 1.04 MB |
| **Tổng số bảng** | 49 bảng (bao gồm Django system tables) |
| **Không có BLOB** | Tất cả dữ liệu là text/integer/float — không có binary blob |
| **Trường JSON** | `store_productspecification.spec_json`, `store_productreview.images` (lưu dạng TEXT) |

### 1.2 Số lượng bản ghi theo bảng

| Bảng | Rows | Ý nghĩa |
|---|---|---|
| **store_customuser** | **4** | Tài khoản user (1 admin + 3 user thường) |
| store_product | 22 | Sản phẩm |
| store_productdetail | 22 | Chi tiết sản phẩm |
| store_productspecification | 22 | Thông số kỹ thuật (JSON) |
| store_productvariant | 140 | Biến thể màu/dung lượng |
| store_productcontent | 22 | Nội dung mô tả sản phẩm |
| store_productimage | 0 | Không có ảnh từ bảng này |
| store_foldercolorimage | 472 | Ảnh sản phẩm theo màu |
| store_imagefolder | 24 | Folder ảnh |
| store_brand | 10 | Hãng sản xuất |
| store_category | 6 | Danh mục |
| store_banner | 13 | Banner trang chủ |
| store_blogpost | 5 | Bài viết blog |
| **store_order** | **27** | Đơn hàng |
| store_orderitem | 31 | Chi tiết đơn hàng |
| store_cart | 4 | Giỏ hàng |
| store_cartitem | 4 | Item trong giỏ |
| store_coupon | 3 | Mã giảm giá |
| store_couponusage | 3 | Lịch sử dùng coupon |
| store_address | 4 | Địa chỉ giao hàng |
| store_wishlist | 4 | Danh sách yêu thích |
| store_wishlist_products | 1 | M2M wishlist-product |
| store_productreview | 5 | Đánh giá sản phẩm |
| store_hangingproduct | 7 | Sản phẩm treo banner |
| store_hotsaleproduct | 20 | Sản phẩm hot sale |
| store_vnpaypayment | 5 | Lịch sử thanh toán VNPay |
| store_pendingqrpayment | 8 | Thanh toán QR đang chờ |
| store_newsletter | 4 | Đăng ký nhận tin |
| store_sitevisit | 596 | Lượt xem trang |
| store_userbrowselog | 198 | Lịch sử duyệt web user |
| django_session | 23 | Session đăng nhập |
| auth_permission | 168 | Quyền hệ thống Django |
| django_content_type | 42 | Content types |
| django_migrations | 83 | Lịch sử migration |
| socialaccount_socialapp | 1 | Google OAuth app config |
| django_site | 1 | Site config |
| *Bảng 0 rows* | 0 | account_*, auth_group, admin_log, passwordhistory, productimage, emailverification |

### 1.3 Tài khoản người dùng

| ID | Email | Role |
|---|---|---|
| 43 | admin@hotmail.com | Superuser + Staff |
| 44 | qhunsean@gmail.com | User thường |
| 45 | huyt2425@gmail.com | User thường |
| 57 | dtc235200981@ictu.edu.vn | User thường (OAuth?) |

> Mật khẩu lưu dạng `pbkdf2_sha256` hash — **sẽ giữ nguyên sau khi chuyển sang PostgreSQL, đăng nhập vẫn hoạt động bình thường.**

### 1.4 Đơn hàng theo trạng thái

| Status | Số đơn |
|---|---|
| delivered | 8 |
| payment_expired | 7 |
| awaiting_payment | 4 |
| cancelled | 4 |
| pending | 3 |
| processing | 1 |

### 1.5 Dữ liệu ngoài SQLite

| Loại | Vị trí | Kích thước | Ghi chú |
|---|---|---|---|
| **Media files** | `media/` | **42.44 MB** | Ảnh sản phẩm, banner, blog — KHÔNG lưu trong DB |
| media.zip | `media/media.zip` | 21.18 MB | File zip backup (không cần thiết) |
| AI Vector store | `data/vector_store/` | ~55 KB | FAISS index nhỏ — có thể include vào git |
| AI Intent model | `data/intent_model.pkl` | 228 KB | Model ML đã train |
| AI Embeddings cache | `data/embeddings_cache/` | **458 MB** | Cache lớn — bị gitignore, sẽ tự rebuild |
| Conversations | `data/conversations/` | 0 files | Không có dữ liệu |

> **Rủi ro media:** Render ephemeral filesystem — ảnh upload sẽ mất sau redeploy. Cần giải pháp lưu trữ ngoài (xem Phần 4).

---

## PHẦN 2 — ĐÁNH GIÁ DUMPDATA/LOADDATA

### 2.1 Kết luận: DÙNG ĐƯỢC, với điều kiện

**Kiểm tra thực tế (dry-run, không thay đổi DB):**

| App | Objects | Kết quả |
|---|---|---|
| contenttypes | 42 | ✅ OK |
| auth | 168 | ✅ OK |
| sites | 1 | ✅ OK |
| account | 0 | ✅ OK |
| socialaccount | 1 | ✅ OK |
| store | 1,685 | ✅ OK |

**Tổng:** 1,897 objects serialize thành công.

### 2.2 Vấn đề phát hiện: Encoding trên Windows

`python manage.py dumpdata ... > file.json` **FAIL** trên Windows vì console dùng cp1252 không encode được tiếng Việt (ký tự `Đ`, `ơ`, `ồ`...).

**Giải pháp đã kiểm chứng:** Gọi `dumpdata` qua Python API với `stdout=open(file, 'w', encoding='utf-8')` — **hoạt động hoàn hảo**, xuất 580KB dữ liệu store đúng UTF-8.

### 2.3 Thứ tự dump/load quan trọng

Do ForeignKey dependencies, phải dump và load theo thứ tự:

```
1. contenttypes
2. auth (permissions, groups)
3. sites
4. store.customuser          (user trước)
5. store.brand, store.category
6. store.product
7. store.productdetail, store.productcontent
8. store.productspecification, store.productvariant, store.productimage
9. store.imagefolder, store.foldercolorimage
10. store.order, store.orderitem
11. store.cart, store.cartitem
12. store.coupon, store.couponusage
13. store.address, store.wishlist, store.wishlist_products
14. store.productreview, store.banner, store.blogpost
15. store.hangingproduct, store.hotsaleproduct
16. store.vnpaypayment, store.pendingqrpayment
17. store.newsletter, store.sitevisit, store.userbrowselog
18. account, socialaccount (sau customuser)
19. django_session (cuối)
```

> **Thực tế:** Dùng `--natural-foreign --natural-primary` và dump cả app trong 1 lần, Django tự xử lý thứ tự. Đã test thành công.

### 2.4 Rủi ro dumpdata/loaddata và cách xử lý

| Rủi ro | Mức độ | Cách xử lý |
|---|---|---|
| ContentType ID khác nhau giữa SQLite và PostgreSQL | **CAO** | Dùng `--natural-foreign --natural-primary` — dùng tên model thay ID số |
| `django_session` không tương thích | Thấp | Không dump sessions — user login lại sau migrate |
| `django_migrations` không nên dump | Thấp | Không dump — chạy migrate bình thường trên PostgreSQL |
| `auth_permission` tự tạo lại | Thấp | Không dump auth_permission — Django tự tạo khi migrate |
| `sqlite_sequence` | Không áp dụng | Không có trên PostgreSQL |
| Encoding tiếng Việt | **CAO** | Dùng Python API, không dùng redirect console |
| `spec_json` TEXT trên SQLite vs JSONField trên PostgreSQL | Trung bình | Kiểm tra model — nếu là `JSONField`, PostgreSQL lưu native JSON |

---

## PHẦN 3 — NHỮNG FILE CẦN CHỈNH SỬA

### 3.1 `requirements.txt` — thêm dependencies bắt buộc

**Thêm 6 dòng:**
```
gunicorn>=20.1.0
psycopg2-binary>=2.9.0
dj-database-url>=2.1.0
sentence-transformers>=2.2.0
faiss-cpu>=1.7.0
scikit-learn>=1.3.0
numpy>=1.24.0
```
**Sửa 1 dòng:**
```
# CŨ:
tzdata>=2024.1; sys_platform == "win32"
# MỚI (Render là Linux, cần tzdata):
tzdata>=2024.1
```

### 3.2 `config/settings.py` — 3 thay đổi

**Thay đổi 1: Database config — đọc từ DATABASE_URL**
```python
# Thêm vào đầu file (sau import os):
import dj_database_url

# Thay DATABASES block hiện tại:
DATABASES = {
    'default': dj_database_url.config(
        default=f"sqlite:///{BASE_DIR / 'db.sqlite3'}",
        conn_max_age=600,
        conn_health_checks=True,
    )
}
```
> Khi `DATABASE_URL` không được set → fallback SQLite (dev vẫn hoạt động bình thường).

**Thay đổi 2: CSRF_TRUSTED_ORIGINS — thêm Render domain**
```python
CSRF_TRUSTED_ORIGINS = [
    'https://qhun22.com',
    'https://www.qhun22.com',
    'https://*.onrender.com',   # <-- thêm dòng này
    'http://localhost:8000',
    'http://127.0.0.1:8000',
]
```

**Thay đổi 3: Security settings cho production**
```python
# Thêm vào cuối settings.py:
if not DEBUG:
    SECURE_HSTS_SECONDS = 31536000
    SECURE_HSTS_INCLUDE_SUBDOMAINS = True
    SECURE_SSL_REDIRECT = True
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
    SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
```
> `SECURE_PROXY_SSL_HEADER` cần thiết vì Render dùng reverse proxy.

### 3.3 Tạo file `.python-version`
```
3.12.9
```
> Render sẽ dùng Python 3.12 thay vì Python 3.14 (beta).

### 3.4 Tạo file `build.sh`
```bash
#!/usr/bin/env bash
set -o errexit
pip install -r requirements.txt
python manage.py collectstatic --no-input
python manage.py migrate
```
> Build Command trên Render sẽ là: `./build.sh`

### 3.5 Xử lý `.env.test2` trong git
```bash
git rm --cached .env.test2
# Thêm vào .gitignore: .env.test2
git add .gitignore
git commit -m "Remove .env.test2 from git tracking"
```

### 3.6 Thêm `data/vector_store/` và `data/*.pkl` vào git (QUAN TRỌNG cho chatbot)
```gitignore
# Trong .gitignore, SỬA THÀNH:
data/embeddings_cache/      ← giữ nguyên (quá lớn)
# KHÔNG gitignore:
# data/vector_store/        ← cần để chatbot hoạt động ngay
# data/intent_model.pkl     ← cần để chatbot không phải train lại
```
> Hiện tại `data/*.pkl` bị gitignore → `data/intent_model.pkl` sẽ không lên Render → chatbot sẽ tự train lại (tốn ~60s cold start).  
> **Khuyến nghị:** Bỏ `data/*.pkl` khỏi gitignore (hoặc add explicitly) để push cả model lên.

---

## PHẦN 4 — QUY TRÌNH CHUYỂN ĐỔI AN TOÀN (SQLite → PostgreSQL)

### Giai đoạn A: Chuẩn bị (thực hiện trên máy local)

```
A1. Sao lưu SQLite gốc
A2. Export dữ liệu ra JSON
A3. Sửa code (requirements.txt, settings.py)
A4. Push lên GitHub
```

### Giai đoạn B: Render (thực hiện trên Render dashboard)

```
B1. Tạo PostgreSQL database trên Render
B2. Tạo Web Service, khai báo env vars
B3. Deploy lần đầu (chỉ tạo cấu trúc DB)
B4. Import dữ liệu từ JSON vào PostgreSQL
B5. Upload media files
B6. Test toàn bộ chức năng
```

---

### CHI TIẾT TỪNG BƯỚC

#### A1. Sao lưu SQLite gốc
```bash
# Chạy trên máy local — tạo backup với timestamp
copy db.sqlite3 db.sqlite3.backup_20261021
```
> **KHÔNG XÓA** `db.sqlite3` gốc cho đến khi PostgreSQL đã verified OK.

#### A2. Export dữ liệu ra JSON (script sẽ được tạo: `export_data.py`)
```python
# Script export dùng Python API (tránh encoding issue Windows)
# Export ra file: data_export/dump_YYYYMMDD.json
# Không dump: django_session, django_migrations, auth_permission, sqlite_sequence
# Dump với: --natural-foreign --natural-primary
```
**Các app cần dump:**
1. `contenttypes` — cần cho FK tham chiếu
2. `auth.group` — nếu có
3. `sites` — django_site (cần cho allauth)
4. `socialaccount.socialapp` — Google OAuth config
5. `store` — toàn bộ dữ liệu nghiệp vụ

**KHÔNG dump:**
- `django_migrations` — chạy migrate bình thường
- `auth.permission` — tự tạo lại khi migrate
- `django_session` — không cần giữ sessions
- `django_admin_log` — không có dữ liệu
- `contenttypes` — **CÓ THỂ gây conflict**, dùng `--natural-foreign` để tránh

#### A3. Sửa code (đã liệt kê ở Phần 3)

#### A4. Push lên GitHub
```bash
git add requirements.txt config/settings.py .python-version build.sh .gitignore
git rm --cached .env.test2
git commit -m "Chuẩn bị deploy Render: PostgreSQL, gunicorn, security"
git push origin main
```

#### B1. Tạo PostgreSQL trên Render
- Render dashboard → New → PostgreSQL
- Plan: Free (256MB, đủ cho 1.04MB data)
- Lấy `Internal Database URL` (dùng trong Web Service)

#### B2. Tạo Web Service trên Render
- Repository: GitHub repo của project
- Branch: `main`
- Root Directory: *(để trống)*
- Build Command: `./build.sh`
- Start Command: `gunicorn config.wsgi:application --bind 0.0.0.0:$PORT --workers 2 --timeout 120`

**Environment Variables:**
```
SECRET_KEY=<tạo mới bằng get_random_secret_key()>
DEBUG=False
ALLOWED_HOSTS=qhun22.com,www.qhun22.com,<app>.onrender.com
DATABASE_URL=<Internal URL từ Render PostgreSQL>
ANTHROPIC_API_KEY=<từ .env>
GOOGLE_OAUTH2_CLIENT_ID=<từ .env>
GOOGLE_OAUTH2_CLIENT_SECRET=<từ .env>
CLOUDFLARE_TURNSTILE_SITE_KEY=<từ .env>
CLOUDFLARE_TURNSTILE_SECRET_KEY=<từ .env>
EMAIL_HOST_USER=<từ .env>
EMAIL_HOST_PASSWORD=<từ .env>
VNPAY_TMN_CODE=<từ .env>
VNPAY_HASH_SECRET=<từ .env>
MOMO_ACCESS_KEY=<từ .env>
MOMO_SECRET_KEY=<từ .env>
TELEGRAM_BOT_TOKEN=<từ .env>
TELEGRAM_CHAT_ID=<từ .env>
BANK_ACCOUNT_NO=<từ .env>
BANK_ACCOUNT_NAME=<từ .env>
```

> ⚠️ **QUAN TRỌNG:** File `.env` và `.env.production` hiện tại chứa key thật đang dùng.  
> Sau khi khai báo trên Render, **KHÔNG** cần thay key (trừ SECRET_KEY nên dùng key mới an toàn hơn).  
> Sau khi deploy xong, nên rotate (đổi) `SECRET_KEY` trên Render.

#### B3. Deploy lần đầu — chỉ tạo cấu trúc
- Lần deploy đầu: `build.sh` chạy `migrate` → tạo 49 bảng rỗng trên PostgreSQL
- Kiểm tra logs xem migrate thành công chưa

#### B4. Import dữ liệu vào PostgreSQL
Có 2 cách:

**Cách 1 (Khuyến nghị): Chạy từ máy local, kết nối trực tiếp vào PostgreSQL Render**
```bash
# 1. Dùng External Database URL (có trên Render dashboard)
# 2. Chạy script trên máy local:
DATABASE_URL=<External URL> python manage.py loaddata dump_store.json
```
> Ưu điểm: không cần upload file, chạy từ local, dễ debug.

**Cách 2: Upload script lên Render và chạy qua Shell**
```bash
# Render dashboard → Web Service → Shell
python manage.py loaddata /tmp/dump_store.json
```

**Thứ tự loaddata:**
```bash
python manage.py loaddata dump_contenttypes.json
python manage.py loaddata dump_sites.json
python manage.py loaddata dump_socialaccount.json
python manage.py loaddata dump_store.json
```

#### B5. Upload media files lên Cloudflare R2 (QUAN TRỌNG)
Media files (42MB ảnh) cần lưu ở nơi bền vững:

**Option A: Cloudflare R2 (miễn phí 10GB)**
- Cần thêm `django-storages[s3]` và `boto3` vào requirements
- Cấu hình `DEFAULT_FILE_STORAGE`

**Option B: Tạm thời** — Upload media lên Render lần đầu, chấp nhận mất sau redeploy.  
Dùng Render Shell để upload, hoặc kết nối SFTP/rsync.

**Option C: Bắt đầu không có media, upload lại thủ công từng ảnh qua admin.**

> **Khuyến nghị tối thiểu:** Dùng Option B cho lần deploy đầu, triển khai R2 sau.

#### B6. Kiểm chứng sau import

**Kiểm tra số lượng records:**
```bash
# Chạy trên Render Shell hoặc từ local với External URL
python manage.py shell -c "
from store.models import *
print('Users:', CustomUser.objects.count())
print('Products:', Product.objects.count())
print('Orders:', Order.objects.count())
print('ProductVariants:', ProductVariant.objects.count())
print('FolderColorImages:', FolderColorImage.objects.count())
print('SiteVisits:', SiteVisit.objects.count())
"
```

**Kết quả mong đợi:**
```
Users: 4
Products: 22
Orders: 27
ProductVariants: 140
FolderColorImages: 472
SiteVisits: 596
```

**Kiểm tra đăng nhập:**
- Thử đăng nhập với `admin@hotmail.com` — mật khẩu giữ nguyên hash
- Kiểm tra Django admin panel
- Kiểm tra Google OAuth

---

## PHẦN 5 — RỦI RO VÀ PHƯƠNG ÁN KHÔI PHỤC

### 5.1 Các rủi ro chính

| Rủi ro | Khả năng | Phương án xử lý |
|---|---|---|
| Mất dữ liệu SQLite gốc | **Thấp** | Backup `db.sqlite3.backup_YYYYMMDD` trước khi làm gì |
| ContentType ID conflict khi loaddata | **Trung bình** | Dùng `--natural-foreign`, test với PostgreSQL local trước |
| AI model không load (RAM 512MB) | **Cao** | sentence-transformers cần ~430MB RAM. Nếu fail → nâng lên Starter ($7) hoặc disable AI khi không có RAM |
| Media files mất sau redeploy | **Chắc chắn** | Cần Cloudflare R2 cho solution lâu dài |
| `data/intent_model.pkl` không có trên Render | **Cao** | Bỏ gitignore cho file này, hoặc chatbot tự train lại (~60s) |
| `data/vector_store/` không có trên Render | **Cao** | Bỏ gitignore, push lên git (chỉ 55KB) |
| Embeddings cache 458MB không có | **Chắc chắn** | Sẽ tự download khi cold start (10-15 phút lần đầu) |
| Google OAuth redirect URL lỗi | **Cao** | Phải update Authorized Redirect URIs trên Google Console |

### 5.2 Phương án khôi phục nếu lỗi

**Nếu loaddata thất bại:**
1. Drop tất cả tables trên PostgreSQL: `python manage.py migrate --run-syncdb` với DB rỗng mới
2. Chạy lại migrate + loaddata
3. SQLite gốc trên máy local vẫn nguyên vẹn — không có gì bị mất

**Nếu PostgreSQL có vấn đề:**
1. Xóa `DATABASE_URL` env var trên Render → Django fallback về SQLite (nhưng SQLite không có trên Render)
2. Rollback: dùng deploy cũ (Render giữ lịch sử deploy)

**Backup SQLite định kỳ:**
```bash
# Trên máy local, trước mỗi lần làm gì lớn:
copy db.sqlite3 "db.sqlite3.backup_$(date +%Y%m%d_%H%M%S)"
```

---

## PHẦN 6 — BẢO MẬT: XỬ LÝ SECRETS

### 6.1 File `.env.test2` trong git
- Nội dung: `MY_VAR_2=from_env` — không nguy hiểm
- Nhưng cần xóa khỏi git: `git rm --cached .env.test2`

### 6.2 Các keys trong `.env` và `.env.production`
- Hai file này **KHÔNG** bị git track (đã gitignore) — **AN TOÀN**
- Không push lên GitHub — chỉ khai báo thủ công trên Render

### 6.3 Keys hardcode trong source (sandbox keys)
- `MOMO_SECRET_KEY` fallback trong `settings.py:182` — là key sandbox test của MoMo
- Không nguy hiểm nhưng nên clean
- Sẽ bị override bởi env var trên Render

### 6.4 Sau khi deploy: nên rotate
- Tạo `SECRET_KEY` mới cho production
- Đổi email app password nếu lo lộ

---

## PHẦN 7 — TÓM TẮT: NHỮNG VIỆC CẦN LÀM THEO THỨ TỰ

### Phase 1: Sửa code (máy local) — Chờ phê duyệt

1. [ ] Sửa `requirements.txt`: thêm gunicorn, psycopg2-binary, dj-database-url, AI/ML deps, fix tzdata
2. [ ] Sửa `config/settings.py`: DATABASE_URL config, CSRF_TRUSTED_ORIGINS, security headers
3. [ ] Tạo `.python-version` (nội dung: `3.12.9`)
4. [ ] Tạo `build.sh`
5. [ ] Sửa `.gitignore`: bỏ `.env.test2`, bỏ ignore `data/vector_store/` và `data/intent_model.pkl`
6. [ ] `git rm --cached .env.test2`
7. [ ] Tạo script `export_data.py` để export SQLite an toàn (UTF-8)
8. [ ] Sao lưu `db.sqlite3` → `db.sqlite3.backup_20261021`
9. [ ] Commit và push lên GitHub

### Phase 2: Render setup

10. [ ] Tạo PostgreSQL database trên Render (Free)
11. [ ] Tạo Web Service, điền env vars
12. [ ] Deploy lần đầu (kiểm tra migrate thành công)

### Phase 3: Import dữ liệu

13. [ ] Chạy `export_data.py` → xuất JSON từ SQLite local
14. [ ] Kết nối PostgreSQL Render qua External URL
15. [ ] Chạy `loaddata` với từng file JSON
16. [ ] Kiểm chứng số lượng records

### Phase 4: Media & Testing

17. [ ] Upload media files lên Render (tạm thời) hoặc Cloudflare R2
18. [ ] Test đăng nhập, đơn hàng, chatbot, thanh toán
19. [ ] Update Google OAuth Authorized Redirect URIs
20. [ ] Cấu hình custom domain `qhun22.com` trên Render (nếu muốn)

---

*Kế hoạch này chỉ để đánh giá và phê duyệt. CHƯA có thay đổi nào được thực hiện.*
