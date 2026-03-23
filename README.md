# QHUN22 — Website bán điện thoại

> Báo cáo môn học · Django · Python  

---

## 1. Giới thiệu đề tài

**QHUN22** là website thương mại điện tử chuyên bán điện thoại di động, được xây dựng bằng **Django 4.2** (Python). Đồ án mô phỏng quy trình mua sắm online thực tế bao gồm: duyệt sản phẩm, thêm giỏ hàng, đặt hàng, thanh toán trực tuyến, và tích hợp chatbot AI tư vấn khách hàng.

### Mục tiêu

- Xây dựng hệ thống e-commerce hoàn chỉnh với đầy đủ tính năng mua bán
- Tích hợp nhiều cổng thanh toán (VNPay, MoMo, VietQR, COD)
- Ứng dụng AI (Claude API + RAG) vào chatbot hỗ trợ khách hàng
- Hệ thống quản trị (dashboard) cho admin quản lý toàn bộ cửa hàng

---

## 2. Công nghệ sử dụng

| Thành phần | Công nghệ |
| :---------- | :--------- |
| **Backend** | Python 3.10+, Django 4.2 |
| **Database** | SQLite3 (dev) · có thể nâng lên PostgreSQL |
| **Frontend** | HTML5, CSS3 (thuần), JavaScript (ES6) |
| **Authentication** | django-allauth (Email + Google OAuth2) |
| **Thanh toán** | VNPay API v2.1, MoMo API v2, VietQR, COD |
| **AI / Chatbot** | Claude API (Anthropic), FAISS, sentence-transformers |
| **CAPTCHA** | Cloudflare Turnstile |
| **Email** | SMTP (Gmail) |
| **Khác** | python-dotenv, openpyxl (xuất Excel), Remix Icon |

---

## 3. Cấu trúc thư mục

```text
qhun22/
├── config/                  # Cấu hình Django (settings, urls, wsgi)
├── store/                   # App chính
│   ├── models.py            # Tất cả model (User, Product, Order, ...)
│   ├── views/               # Views chia theo chức năng
│   │   ├── admin_views.py       # Dashboard, quản lý sản phẩm/đơn hàng
│   │   ├── auth_views.py        # Đăng nhập, đăng ký, profile
│   │   ├── product_views.py     # Trang chủ, chi tiết SP, tìm kiếm
│   │   ├── cart_views.py        # Giỏ hàng
│   │   ├── order_views.py       # Checkout, theo dõi đơn, hoàn tiền
│   │   ├── payment_views.py     # Xử lý thanh toán (VNPay, MoMo, VietQR)
│   │   ├── blog_views.py        # Blog
│   │   ├── chatbot_views.py     # API chatbot
│   │   ├── coupon_views.py      # Mã giảm giá
│   │   └── hotsale_views.py     # Sản phẩm khuyến mãi
│   ├── urls.py              # URL routing
│   ├── momo_utils.py        # Helper MoMo payment
│   ├── vnpay_utils.py       # Helper VNPay payment
│   ├── chatbot_service.py   # Orchestrator chatbot
│   ├── claude_service.py    # Gọi Claude API
│   └── migrations/          # Database migrations
├── ai/                      # Module AI riêng
│   ├── embeddings.py        # Tạo vector embedding (multilingual)
│   ├── vector_store.py      # FAISS vector database
│   ├── intent_model.py      # Phân loại ý định người dùng
│   ├── rag_pipeline.py      # RAG pipeline chính
│   ├── prompt_builder.py    # Xây dựng prompt cho Claude
│   ├── conversation_memory.py  # Quản lý lịch sử hội thoại
│   ├── claude_client.py     # HTTP client gọi Claude API
│   └── trainer.py           # Huấn luyện lại model
├── templates/store/         # Giao diện HTML
│   ├── pages/               # Trang công khai (home, product, blog, ...)
│   ├── auth/                # Đăng nhập / Đăng ký
│   ├── cart/                # Giỏ hàng, checkout
│   ├── payment/             # Trang thanh toán (VietQR, ...)
│   ├── user/                # Profile, theo dõi đơn hàng
│   ├── admin/               # Dashboard quản trị
│   └── fragments/           # Component tái sử dụng
├── static/                  # CSS, JS, logo, icon
├── media/                   # File upload (ảnh SP, banner, blog)
├── data/                    # Vector store, embedding cache
├── docs/                    # Tài liệu kỹ thuật
├── logs/                    # Log chatbot
├── manage.py
├── requirements.txt         # Thư viện chính
├── qhun22.bat               # Script cài đặt (Windows)
└── .env                     # Biến môi trường (không push lên git)
```

---

## 4. Database — Các model chính

| Model | Mô tả |
| :----- | :----- |
| `CustomUser` | Tài khoản người dùng (email làm username, hỗ trợ OAuth, xác thực Student/Teacher) |
| `Category` | Danh mục sản phẩm |
| `Brand` | Hãng sản xuất (Apple, Samsung, ...) |
| `Product` | Sản phẩm (tên, giá, ảnh, tồn kho, ...) |
| `ProductDetail` | Chi tiết SP (YouTube, mô tả dài, giá gốc) |
| `ProductVariant` | Biến thể SP (màu + dung lượng + giá riêng) |
| `ProductSpecification` | Thông số kỹ thuật (JSON) |
| `ProductImage` | Ảnh SP (cover, marketing, variant, gallery) |
| `Cart` / `CartItem` | Giỏ hàng (1 cart/user, nhiều item) |
| `Wishlist` | Danh sách yêu thích |
| `Address` | Sổ địa chỉ giao hàng |
| `Order` / `OrderItem` | Đơn hàng + chi tiết từng sản phẩm |
| `VNPayPayment` | Giao dịch VNPay |
| `PendingQRPayment` | Giao dịch VietQR (chờ duyệt) |
| `ProductReview` | Đánh giá sản phẩm (1 review/user/product) |
| `Banner` | Banner quảng cáo trang chủ |
| `BlogPost` | Bài viết blog |
| `HotSaleProduct` | Sản phẩm khuyến mãi nổi bật |
| `SiteVisit` | Thống kê lượt truy cập |
| `UserBrowseLog` | Log lịch sử duyệt SP (phục vụ gợi ý) |

---

## 5. Chức năng hệ thống

### 5.1. Phía khách hàng

| Chức năng | Mô tả |
| :--------- | :----- |
| Xem sản phẩm | Trang chủ, chi tiết SP, tìm kiếm, lọc theo hãng/giá |
| Giỏ hàng | Thêm/xóa/cập nhật SP, chọn màu + dung lượng |
| Yêu thích | Lưu SP yêu thích, toggle nhanh |
| So sánh SP | So sánh 2-3 sản phẩm cạnh nhau |
| Đặt hàng | Checkout với nhiều phương thức thanh toán |
| Theo dõi đơn | Xem trạng thái đơn hàng realtime |
| Đánh giá | Review SP sau khi mua thành công |
| Mã giảm giá | Áp dụng voucher khi checkout |
| Chatbot AI | Hỏi tư vấn SP, so sánh, hỏi giá 24/7 |
| Xác thực Edu | Xác thực email `.edu.vn` → nhận voucher giảm 50% |
| Hoàn tiền | Yêu cầu hoàn tiền cho đơn đã hủy |

### 5.2. Phía admin (Dashboard)

| Chức năng | Mô tả |
| :--------- | :----- |
| Quản lý SP | CRUD sản phẩm, biến thể, ảnh, thông số kỹ thuật |
| Quản lý đơn hàng | Xem/cập nhật trạng thái, duyệt hoàn tiền |
| Quản lý user | Thêm/sửa/xóa người dùng |
| Quản lý thương hiệu | CRUD hãng sản xuất |
| Mã giảm giá | Tạo/sửa/xóa coupon |
| Banner | Thay đổi banner trang chủ |
| Blog | Viết bài blog |
| Hot Sale | Quản lý SP khuyến mãi |
| Thống kê | Doanh thu, SP bán chạy, xuất Excel |

---

## 6. Thanh toán

Hệ thống hỗ trợ **4 phương thức** thanh toán:

| Phương thức | Mô tả |
| :----------- | :----- |
| **COD** | Thanh toán khi nhận hàng |
| **VNPay** | Chuyển hướng sang cổng VNPay, thanh toán bằng thẻ/QR, callback tự động |
| **MoMo** | Chuyển hướng sang MoMo app, thanh toán bằng ví MoMo |
| **VietQR** | Hiển thị mã QR chuyển khoản ngân hàng, admin duyệt thủ công |

> Chi tiết kỹ thuật thanh toán: xem [docs/tailieuvnpay.md](docs/tailieuvnpay.md) và [docs/tailieumomo.md](docs/tailieumomo.md)

---

## 7. Chatbot AI

### Kiến trúc

```text
Người dùng  →  Intent Classifier  →  Simple Intent?  →  Template Response
                                          ↓ No
                                   Vector Search (FAISS)
                                          ↓
                                   Build Context + Prompt
                                          ↓
                                   Claude API (Haiku)
                                          ↓
                                   Response → Lưu Memory
```

### Thành phần

| Module | Chức năng |
| :------ | :-------- |
| `intent_model.py` | Phân loại ý định: greeting, product_search, price_query, compare, ... |
| `embeddings.py` | Tạo embedding bằng `paraphrase-multilingual-MiniLM-L12-v2` (384 chiều) |
| `vector_store.py` | Lưu trữ FAISS index cho products, brands, content |
| `rag_pipeline.py` | Pipeline chính: intent → search → build prompt → gọi Claude → trả lời |
| `claude_client.py` | HTTP client gọi Claude API (model: claude-3-haiku) |
| `prompt_builder.py` | Xây dựng system prompt + context cho Claude |
| `conversation_memory.py` | Quản lý session + lịch sử hội thoại (timeout 1h, max 20 tin nhắn) |

### Phân loại ý định

- **Simple intents** (trả lời luôn, không cần AI): chào hỏi, hỏi danh tính, hỏi bảo hành, hỏi trả góp, ...
- **Complex intents** (cần Claude): tư vấn điện thoại, so sánh SP, hỏi thông số chi tiết, xử lý sự cố

---

## 8. Hướng dẫn cài đặt

### Yêu cầu

- **Python** 3.10 trở lên (khuyến nghị 3.11)
- **pip** 23.0+
- **OS**: Windows / Linux / macOS

### Cách 1: Dùng script (Windows)

```text
Chạy file qhun22.bat → chọn [0] Cài đặt lần đầu
```

Script sẽ tự động: kiểm tra Python → tạo venv → cài thư viện → chạy migrate.

### Cách 2: Cài thủ công

```bash
# 1. Tạo môi trường ảo
python -m venv venv
venv\Scripts\activate          # Windows
# source venv/bin/activate     # Linux/macOS

# 2. Cài thư viện
pip install --upgrade pip
pip install -r requirements.txt

# 3. (Tùy chọn) Cài thêm module AI
pip install -r ai/ai_requirements.txt

# 4. Tạo file .env (xem mẫu bên dưới)

# 5. Tạo database
python manage.py migrate

# 6. Tạo tài khoản admin
python manage.py createsuperuser

# 7. Chạy server
python manage.py runserver
```

Truy cập: <http://127.0.0.1:8000/>

### File `.env` mẫu

```env
# === Django ===
SECRET_KEY=your-secret-key-here
DEBUG=True
ALLOWED_HOSTS=127.0.0.1,localhost

# === VNPay (sandbox) ===
VNPAY_TMN_CODE=
VNPAY_HASH_SECRET=
VNPAY_URL=
VNPAY_RETURN_URL=

# === MoMo (test) ===
MOMO_PARTNER_CODE=MOMO
MOMO_ACCESS_KEY=
MOMO_SECRET_KEY=
MOMO_ENDPOINT=
MOMO_RETURN_URL=
MOMO_IPN_URL=

# === VietQR ===
BANK_ID=TCB
BANK_ACCOUNT_NO=your-account-number
BANK_ACCOUNT_NAME=your-name

# === Cloudflare Turnstile ===
CLOUDFLARE_TURNSTILE_SITE_KEY=
CLOUDFLARE_TURNSTILE_SECRET_KEY=

# === Google OAuth2 ===
GOOGLE_OAUTH2_CLIENT_ID=
GOOGLE_OAUTH2_CLIENT_SECRET=

# === Claude AI ===
ANTHROPIC_API_KEY=

# === Email (Gmail SMTP) ===
EMAIL_HOST_USER=
EMAIL_HOST_PASSWORD=
```

---

## 9. Lỗi thường gặp

| Lỗi | Cách sửa |
| :--- | :-------- |
| `No module named 'openpyxl'` | `pip install openpyxl` |
| `tzdata` conflict trên Linux | Bỏ qua — file requirements.txt tự skip trên Linux |
| `typing_extensions` error | Nâng cấp Python lên 3.10+ |
| `django-allauth` import error | `pip install -U django-allauth` |
| `.env not found` | Tạo file `.env` theo mẫu ở mục 8 |
| Chatbot không hoạt động | Kiểm tra `ANTHROPIC_API_KEY` trong `.env` |

---

## 10. Tài liệu tham khảo

- [docs/tailieuvnpay.md](docs/tailieuvnpay.md) — Tài liệu tích hợp VNPay
- [docs/tailieumomo.md](docs/tailieumomo.md) — Tài liệu tích hợp MoMo
- [Django Documentation](https://docs.djangoproject.com/en/4.2/)
- [VNPay Developer](https://sandbox.vnpayment.vn/apis/)
- [MoMo Developer](https://developers.momo.vn/)
- [Anthropic Claude API](https://docs.anthropic.com/)

---

## 11. Ghi chú

- Database mặc định là **SQLite** (cho development). Production nên chuyển sang PostgreSQL.
- Các tính năng VNPay, MoMo, Claude AI cần cấu hình API key trong `.env` mới hoạt động.
- File `db.sqlite3` đã có sẵn dữ liệu mẫu để test.
- Dự án dùng `>=` cho version package — không cần cài đúng version, chỉ cần Python 3.10+.

---

**Sinh viên thực hiện:** Trương Quang Huy  
**Email:** <qhun22@gmail.com>
