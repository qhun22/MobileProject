# RENDER DEPLOY AUDIT — QHUN22 Mobile Shop

> **Ngày kiểm tra:** 2026-10-21  
> **Trạng thái tổng quát:** ⚠️ CHƯA SẴN SÀNG — cần sửa 3 vấn đề bắt buộc trước khi deploy

---

## I. Tổng quan project

| Mục | Giá trị |
|---|---|
| **Tên project** | qhun22mobile (QHUN22 Mobile Shop) |
| **Django version** | 4.2.30 |
| **Python version** | 3.14.0 (venv hiện tại) |
| **Database** | SQLite (file `db.sqlite3`) |
| **Module WSGI** | `config.wsgi.application` |
| **ALLOWED_HOSTS** | Đọc từ env, mặc định: `qhun22.com,www.qhun22.com,127.0.0.1,localhost` |
| **WhiteNoise** | Có (middleware đã cấu hình) |
| **Gunicorn** | **KHÔNG CÓ** trong requirements.txt và venv |
| **AI/ML dependencies** | sentence-transformers, faiss-cpu, scikit-learn, numpy (cần 458MB model cache) |
| **Khả năng deploy** | Cần sửa 3 vấn đề bắt buộc + 5 khuyến nghị |

---

## II. Bảng kiểm tra

| STT | Hạng mục | Trạng thái | Bằng chứng trong source | Cách khắc phục |
|---|---|---|---|---|
| 1 | Cấu trúc Django hợp lệ | ✅ PASS | `manage.py`, `config/wsgi.py`, `config/settings.py`, `config/urls.py` đầy đủ | — |
| 2 | Module WSGI xác định đúng | ✅ PASS | `WSGI_APPLICATION = 'config.wsgi.application'` tại `settings.py:86` | — |
| 3 | `python manage.py check` | ✅ PASS | 0 issues (kiểm tra thực tế) | — |
| 4 | `python manage.py check --deploy` | ⚠️ WARNING | 4 cảnh báo bảo mật HTTPS (W004, W008, W012, W016) | Thêm security settings vào settings.py (xem mục III) |
| 5 | **Gunicorn** trong requirements.txt | ❌ FAIL | Không có dòng `gunicorn` nào trong `requirements.txt`; `pip show gunicorn` → NOT FOUND | Thêm `gunicorn>=20.1.0` vào `requirements.txt` |
| 6 | **Database — SQLite trên Render** | ❌ FAIL | `settings.py:89-94` dùng `sqlite3`, `NAME = BASE_DIR / 'db.sqlite3'` | SQLite không bền vững trên Render (filesystem ephemeral). Cần dùng PostgreSQL hoặc chấp nhận mất data mỗi lần deploy. |
| 7 | psycopg2 (PostgreSQL driver) | ⚠️ WARNING | Không có trong `requirements.txt`; `pip show psycopg2-binary` → NOT FOUND | Cần thêm nếu chuyển sang PostgreSQL |
| 8 | `SECRET_KEY` từ env | ✅ PASS | `settings.py:17`: `os.getenv('SECRET_KEY', 'django-insecure-...')` | Giá trị fallback vẫn là insecure key — phải set env var trên Render |
| 9 | `DEBUG=False` cho production | ✅ PASS | `settings.py:18`: `os.getenv('DEBUG', 'True')` — đọc từ env, cần set `DEBUG=False` trên Render | Set env var `DEBUG=False` trên Render |
| 10 | `ALLOWED_HOSTS` hỗ trợ Render | ⚠️ WARNING | `settings.py:19`: chỉ có `qhun22.com,www.qhun22.com,127.0.0.1,localhost` | Cần thêm domain `.onrender.com` vào ALLOWED_HOSTS env var khi cấu hình Render |
| 11 | `CSRF_TRUSTED_ORIGINS` Render | ⚠️ WARNING | `settings.py:20-25`: chỉ cấu hình cho `qhun22.com` và `localhost` | Cần thêm `https://*.onrender.com` vào list (sửa code) hoặc dùng biến môi trường |
| 12 | `STATIC_URL`, `STATIC_ROOT` | ✅ PASS | `settings.py:111-113`: `/static/`, `staticfiles/` đầy đủ | — |
| 13 | WhiteNoise middleware | ✅ PASS | `settings.py:53`: `whitenoise.middleware.WhiteNoiseMiddleware` đúng vị trí sau `SecurityMiddleware` | — |
| 14 | `STORAGES` với WhiteNoise compression | ⚠️ WARNING | Không có `STORAGES` hoặc `CompressedManifestStaticFilesStorage` trong settings | Nên thêm `STORAGES` để bật compression (tùy chọn) |
| 15 | `collectstatic` hoạt động | ✅ PASS | dry-run thành công không lỗi | — |
| 16 | staticfiles directory đã có | ✅ PASS | `staticfiles/` tồn tại với `css, js, icons, admin, account` | Cần chạy lại `collectstatic` trong build command |
| 17 | Media files (user uploads) | ⚠️ WARNING | `MEDIA_ROOT = BASE_DIR / 'media'` — `media/` có `banner, blog, products...` | Render filesystem ephemeral: media sẽ mất sau deploy. Cần giải pháp lưu trữ ngoài (Cloudflare R2, S3) nếu muốn giữ |
| 18 | Migrations đầy đủ | ✅ PASS | 48 migrations, tất cả `[X]` applied; `makemigrations --check` → "No changes detected" | — |
| 19 | **`requirements.txt` — AI/ML deps** | ❌ FAIL | `sentence-transformers`, `faiss-cpu`, `scikit-learn`, `numpy` có trong venv nhưng **KHÔNG** có trong `requirements.txt` | Thêm vào `requirements.txt` hoặc tạo 2 file riêng biệt |
| 20 | AI model cache (458MB) | ⚠️ WARNING | `data/embeddings_cache/` chiếm 458MB; bị gitignore → sẽ không có trên Render | Model sẽ tự download khi khởi động — cần build time dài, RAM và disk đủ |
| 21 | `data/intent_model.pkl` | ⚠️ WARNING | File `data/intent_model.pkl` bị gitignore → không có trên Render | Chatbot sẽ tự train lại khi start — tốn thời gian cold start |
| 22 | Render-specific files | ⚠️ WARNING | Không có `render.yaml`, `build.sh`, `.python-version` | Cần tạo `build.sh` và `.python-version` |
| 23 | `.env` files trong git | ❌ NGHIÊM TRỌNG | `.env.test2` bị track bởi git (`git ls-files` xác nhận); `.env`, `.env.production`, `.env.local` đã gitignore đúng | **Ngay lập tức**: `git rm --cached .env.test2` và commit. File này chứa test var, nhưng cần remove khỏi git history |
| 24 | Secrets hardcoded trong source | ⚠️ WARNING | `settings.py:182`: `MOMO_SECRET_KEY` có fallback hardcode `K951B6PE1waDMi640xX08PD3vg6EkVlz` (là sandbox key); `settings.py:17`: SECRET_KEY fallback insecure | Đây là sandbox keys nhưng cần đảm bảo set đúng env var trên Render |
| 25 | `.gitignore` coverage | ✅ PASS | `db.sqlite3`, `media/`, `staticfiles/`, `*.log`, `.env*` đều gitignored; `.venv/` gitignored | Chú ý `.env.test2` đã slip through (xem #23) |
| 26 | Không có Redis/Celery/WebSocket | ✅ PASS | Không tìm thấy Celery, Redis, Django Channels trong codebase | Không cần dịch vụ phụ trợ thêm |
| 27 | `tzdata` cho Linux | ✅ PASS | `requirements.txt`: `tzdata>=2024.1; sys_platform == "win32"` — nhưng Render là Linux! | **Cần sửa**: bỏ điều kiện `sys_platform == "win32"`, đổi thành không điều kiện hoặc `sys_platform != "win32"` sẽ bỏ qua trên Linux |
| 28 | LOGGING — file log trên Render | ⚠️ WARNING | `settings.py:224-231`: `chatbot_file` handler ghi vào `logs/chatbot.log` — `LOG_DIR.mkdir()` tự tạo | Hoạt động nhưng log file sẽ mất sau restart; nên dùng console-only trên Render |
| 29 | Google OAuth callback URL | ⚠️ WARNING | Google OAuth redirect phải cấu hình đúng domain trên Google Console | Phải update Authorized Redirect URIs trên Google API Console khi đổi domain |
| 30 | Python 3.14 compatibility | ⚠️ WARNING | Venv đang dùng Python 3.14 (beta/RC); Render Free hỗ trợ Python đến 3.12/3.13 | Khuyến nghị dùng Python 3.12 hoặc 3.13 trên Render để ổn định |

---

## III. Danh sách vấn đề cần xử lý

### 1. BẮT BUỘC sửa để deploy thành công

#### [FAIL-1] Thiếu `gunicorn` trong requirements.txt
- **File:** `requirements.txt`
- **Nguyên nhân:** Render chạy WSGI qua Gunicorn — nếu không có, Start Command sẽ fail ngay.
- **Sửa:** Thêm dòng vào `requirements.txt`:
  ```
  gunicorn>=20.1.0
  ```

#### [FAIL-2] Thiếu AI/ML dependencies trong requirements.txt
- **File:** `requirements.txt`
- **Nguyên nhân:** `sentence-transformers`, `faiss-cpu`, `scikit-learn`, `numpy` có trong venv nhưng không có trong `requirements.txt` → Render sẽ không install → import error khi chatbot khởi động.
- **Sửa:** Thêm vào `requirements.txt`:
  ```
  sentence-transformers>=2.2.0
  faiss-cpu>=1.7.0
  scikit-learn>=1.3.0
  numpy>=1.24.0
  ```
  > **Lưu ý quan trọng:** Các package này rất nặng (~800MB+). Render Free có RAM 512MB và build timeout 30 phút. Có thể gặp vấn đề bộ nhớ. Xem phần V để biết thêm.

#### [FAIL-3] `.env.test2` bị track bởi git
- **File:** `.env.test2` (git tracked)
- **Nguyên nhân:** `git ls-files` xác nhận file này đang trong git index. Dù nội dung chỉ là `MY_VAR_2=from_env`, nhưng **pattern nguy hiểm** — các file `.env.*` production có thể bị push nhầm.
- **Sửa:**
  ```bash
  git rm --cached .env.test2
  git commit -m "Remove .env.test2 from git tracking"
  ```
  Sau đó thêm `.env.test2` vào `.gitignore` (hiện tại chỉ có `.env.*.local`).

#### [FAIL-4] SQLite không bền vững trên Render
- **File:** `config/settings.py:89-94`
- **Nguyên nhân:** Render là container-based — filesystem reset sau mỗi deploy. SQLite sẽ **mất toàn bộ dữ liệu** khi redeploy.
- **Lựa chọn:**
  - **Option A (khuyến nghị):** Tạo PostgreSQL database trên Render, thêm `psycopg2-binary>=2.9.0` và `dj-database-url>=2.0.0` vào requirements, sửa settings để đọc `DATABASE_URL` từ env.
  - **Option B (tạm thời, chấp nhận mất data):** Giữ SQLite nhưng phải biết rằng data sẽ bị xóa mỗi lần deploy/restart.

---

### 2. KHUYẾN NGHỊ sửa để chạy ổn định

#### [WARN-1] Thêm security settings cho production
- **File:** `config/settings.py`
- **Nguyên nhân:** `check --deploy` báo 4 warnings (W004, W008, W012, W016)
- **Sửa:** Thêm vào cuối `settings.py`:
  ```python
  if not DEBUG:
      SECURE_HSTS_SECONDS = 31536000
      SECURE_HSTS_INCLUDE_SUBDOMAINS = True
      SECURE_SSL_REDIRECT = True
      SESSION_COOKIE_SECURE = True
      CSRF_COOKIE_SECURE = True
  ```

#### [WARN-2] ALLOWED_HOSTS và CSRF_TRUSTED_ORIGINS cho Render
- **File:** `config/settings.py:19-25`
- **Nguyên nhân:** Domain `.onrender.com` chưa có trong cấu hình.
- **Sửa:** Thêm vào `CSRF_TRUSTED_ORIGINS` trong settings:
  ```python
  CSRF_TRUSTED_ORIGINS = [
      'https://qhun22.com',
      'https://www.qhun22.com',
      'https://*.onrender.com',  # Thêm dòng này
      'http://localhost:8000',
      'http://127.0.0.1:8000',
  ]
  ```
  Và khi set env var trên Render: `ALLOWED_HOSTS=qhun22.com,www.qhun22.com,<your-app>.onrender.com`

#### [WARN-3] `tzdata` — bỏ điều kiện `sys_platform == "win32"`
- **File:** `requirements.txt`
- **Nguyên nhân:** `tzdata>=2024.1; sys_platform == "win32"` → trên Linux (Render) sẽ bị bỏ qua, nhưng Django 4.2 với `USE_TZ=True` cần `tzdata` trên Linux.
- **Sửa:** Đổi thành:
  ```
  tzdata>=2024.1
  ```

#### [WARN-4] Media files — cần giải pháp lưu trữ ngoài
- Render ephemeral filesystem: ảnh upload bởi user sẽ mất sau restart/redeploy.
- Giải pháp: Dùng Cloudflare R2 (miễn phí 10GB) hoặc AWS S3 với `django-storages`.
- Đây là việc cần làm **sau** khi deploy thành công lần đầu.

#### [WARN-5] Python version — dùng 3.12 thay 3.14
- Python 3.14 là bản beta/RC, chưa được test đầy đủ với toàn bộ dependencies.
- Render hỗ trợ Python 3.12 và 3.13 ổn định.
- Tạo file `.python-version` với nội dung `3.12.9` hoặc `3.13.2`.

---

### 3. Không cần sửa

- Cấu trúc Django, URL routing, migrations — đã hoàn chỉnh.
- WhiteNoise middleware — đã đúng vị trí.
- `collectstatic` — hoạt động tốt.
- Không có Redis/Celery/WebSocket — không cần thêm service.
- Email SMTP — cấu hình đúng, đọc từ env.
- Payment gateways (VNPay, MoMo, VietQR) — đọc từ env đúng cách.

---

## IV. Cấu hình Render đề xuất

| Mục | Giá trị |
|---|---|
| **Service Type** | Web Service |
| **Runtime/Language** | Python 3 |
| **Branch** | `main` |
| **Root Directory** | *(để trống — root của repo)* |
| **Build Command** | `pip install -r requirements.txt && python manage.py collectstatic --no-input && python manage.py migrate` |
| **Start Command** | `gunicorn config.wsgi:application --bind 0.0.0.0:$PORT --workers 2 --timeout 120` |
| **Instance Type** | Free (512MB RAM) — **chú ý:** AI deps nặng, có thể cần Starter ($7/tháng) |

### Environment Variables cần khai báo trên Render

| Variable | Ghi chú |
|---|---|
| `SECRET_KEY` | Tạo key mới an toàn (dùng `python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"`) |
| `DEBUG` | `False` |
| `ALLOWED_HOSTS` | `qhun22.com,www.qhun22.com,<your-app>.onrender.com` |
| `DATABASE_URL` | Cung cấp bởi Render PostgreSQL (nếu dùng) |
| `ANTHROPIC_API_KEY` | API key của Claude |
| `GOOGLE_OAUTH2_CLIENT_ID` | Google OAuth |
| `GOOGLE_OAUTH2_CLIENT_SECRET` | Google OAuth |
| `CLOUDFLARE_TURNSTILE_SITE_KEY` | Turnstile |
| `CLOUDFLARE_TURNSTILE_SECRET_KEY` | Turnstile |
| `EMAIL_HOST_USER` | Gmail |
| `EMAIL_HOST_PASSWORD` | Gmail App Password |
| `VNPAY_TMN_CODE` | VNPay |
| `VNPAY_HASH_SECRET` | VNPay |
| `MOMO_ACCESS_KEY` | MoMo |
| `MOMO_SECRET_KEY` | MoMo |
| `TELEGRAM_BOT_TOKEN` | Telegram |
| `TELEGRAM_CHAT_ID` | Telegram |
| `BANK_ACCOUNT_NO` | VietQR |
| `BANK_ACCOUNT_NAME` | VietQR |

### Database
- **Khuyến nghị:** Tạo Render PostgreSQL (Free tier: 256MB, 90 ngày). Sau 90 ngày cần upgrade hoặc migrate sang ngoài (Supabase, Neon — cả hai có free tier lâu dài).
- **Nếu giữ SQLite tạm thời:** Chấp nhận mất data mỗi lần deploy.

---

## V. Kết luận

### PROJECT HIỆN TẠI **CHƯA SẴN SÀNG** DEPLOY LÊN RENDER

**4 thay đổi bắt buộc theo thứ tự ưu tiên:**

1. **[Quan trọng nhất]** Xóa `.env.test2` khỏi git tracking:
   ```bash
   git rm --cached .env.test2
   ```

2. **Thêm `gunicorn` vào `requirements.txt`** — không có thì deploy chắc chắn fail.

3. **Thêm AI/ML deps vào `requirements.txt`** — `sentence-transformers`, `faiss-cpu`, `scikit-learn`, `numpy`.
   > ⚠️ **Cảnh báo riêng:** `sentence-transformers` sẽ download model ~430MB khi khởi động lần đầu. Render Free (512MB RAM) **có thể không đủ RAM** để load model. Cần kiểm tra thực tế hoặc nâng lên Starter plan. Nếu chatbot AI là tính năng phụ, có thể cân nhắc disable khi không có đủ RAM.

4. **Quyết định về database:** SQLite tạm thời (data mất khi redeploy) hoặc chuyển sang PostgreSQL (bền vững).

**Sau khi sửa 4 vấn đề trên, các bước deploy:**

1. Sửa `requirements.txt` (gunicorn + AI deps + tzdata fix)
2. Sửa `CSRF_TRUSTED_ORIGINS` trong settings.py để thêm `*.onrender.com`
3. Tạo file `.python-version` với nội dung `3.12.9`
4. Tạo file `build.sh` (tùy chọn) hoặc dùng Build Command trực tiếp trên Render
5. Tạo PostgreSQL database trên Render (nếu muốn dữ liệu bền vững)
6. Push lên GitHub
7. Tạo Web Service trên Render, khai báo đầy đủ environment variables
8. Trigger deploy và theo dõi build logs
9. Sau deploy: test Google OAuth, payment callbacks, chatbot AI

---

*Báo cáo này chỉ ghi nhận trạng thái kiểm tra. Không có thay đổi nào được thực hiện trong source code.*
