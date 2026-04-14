# QHUN22 - Website ban dien thoai di dong (Django)

Do an mon hoc Phat trien ung dung Python.

## 1. Muc tieu va pham vi

### Muc tieu
- Xay dung he thong web ban dien thoai hoan chinh, chay duoc thuc te.
- Co day du CSDL, giao dien, nghiep vu va phan quyen.
- Minh hoa quy trinh mua hang end-to-end: tim kiem -> dat hang -> thanh toan -> theo doi don.

### Pham vi
- He thong gom nhieu nhom nguoi dung: Guest, User, Admin.
- Co it nhat 5 thuc the du lieu co quan he.
- Co CRUD cho cac bang du lieu chinh, tim kiem/loc/sap xep.
- Co thong ke bao cao va test co ban.

## 2. Vai tro nguoi dung

### Guest
- Xem trang chu, danh sach san pham, chi tiet san pham.
- Tim kiem va loc san pham.
- Dang ky, dang nhap, quen mat khau.

### User (da dang nhap)
- Quan ly ho so ca nhan, so dia chi.
- Them vao gio hang, dat hang, theo doi don.
- Danh gia san pham, wishlist, so sanh san pham.
- Su dung coupon va thanh toan (COD, VNPay, MoMo, VietQR).

### Admin
- Quan ly user, phan quyen truy cap dashboard.
- CRUD san pham, hang, blog, banner, hot sale, coupon.
- Quan ly don hang, cap nhat trang thai, duyet thanh toan/hoan tien.
- Xem thong ke doanh thu, san pham ban chay, xuat file Excel.

## 3. Chuc nang he thong (tom tat)

He thong dap ung cac nhom chuc nang dong chinh:

1. Xac thuc va phan quyen
- Dang ky, dang nhap, dang xuat.
- Quen mat khau qua OTP va dat lai mat khau.
- Kiem soat truy cap theo vai tro Guest/User/Admin.

2. CRUD du lieu
- CRUD San pham.
- CRUD Thuong hieu.
- CRUD User (dashboard).
- CRUD Blog/Banner/HotSale/Coupon.

3. Tim kiem, loc, sap xep
- Tim kiem san pham theo ten/tu khoa.
- Loc theo hang, khoang gia, thuoc tinh.
- Autocomplete tim kiem.

4. Nghiep vu dac thu
- Luong dat hang va thanh toan (COD, VNPay, MoMo, VietQR).
- Luong duyet/huy/hoan tien voi trang thai xu ly.

5. Upload va xu ly tep/anh
- Upload anh san pham, banner, media noi dung.
- Quan ly thu muc anh va cac thao tac them/xoa/sua ten.

6. Thong ke bao cao
- Dashboard doanh thu theo thang/nam.
- Bang tong hop don hang, san pham ban chay.

7. AI chatbot
- Tu van san pham bang RAG + Claude API.
- Luu nho hoi thoai va tra loi theo ngu canh.

## 4. Cong nghe su dung

| Thanh phan | Cong nghe |
| :-- | :-- |
| Backend | Python 3.10+, Django 4.2 |
| CSDL | SQLite3 (dev), co the nang cap PostgreSQL |
| Frontend | HTML, CSS, JavaScript |
| Xac thuc | django-allauth + OAuth2 |
| Thanh toan | VNPay, MoMo, VietQR, COD |
| AI | Anthropic Claude API, FAISS, sentence-transformers |
| Bao mat bo sung | Cloudflare Turnstile |
| Thu vien khac | python-dotenv, openpyxl |

## 5. Kien truc tong quan

- Mo hinh MVC/MVT cua Django.
- Tach lop theo module:
  - config: cau hinh du an.
  - store: app nghiep vu chinh (model/view/url/service).
  - ai: module chatbot RAG.
  - templates/static/media: giao dien va tai nguyen.
- Duong dan URL trung tam:
  - config/urls.py
  - store/urls.py

## 6. Thiet ke CSDL (thuc the chinh)

He thong co tren 5 bang va quan he ro rang, vi du:

- CustomUser
- Product
- Brand
- Category
- Order
- OrderItem
- Cart
- CartItem
- Coupon
- ProductReview
- PendingQRPayment

Quan he tieu bieu:
- 1-n: User -> Order, Order -> OrderItem, Brand -> Product.
- n-n (thong qua bang trung gian): Product va gio hang qua CartItem.

## 7. Cac route nghiep vu quan trong

### Xac thuc
- /login/
- /register/
- /forgot-password/
- /send-otp-forgot-password/
- /verify-otp-forgot-password/
- /reset-password/

### Dat hang va thanh toan
- /checkout/
- /order/place/
- /vnpay/create/
- /momo/create/
- /vietqr/create-order/
- /vietqr-payment/<order_id>/

### Dashboard quan tri
- /dashboard/
- /api/admin/orders/
- /api/admin/order-update-status/
- /best-sellers/

## 8. Huong dan cai dat va chay

### Yeu cau
- Python 3.10+
- pip moi
- He dieu hanh: Windows/Linux/macOS

### Cach 1 (Windows, khuyen nghi)
- Chay file qhun22.bat.
- Chon [0] setup full tu dong.

### Cach 2 (thu cong)

```bash
python -m venv .venv
.venv\Scripts\activate
pip install --upgrade pip
pip install -r requirements.txt
pip install -r ai/ai_requirements.txt
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

Truy cap: http://127.0.0.1:8000/

## 9. Cau hinh moi truong (.env)

Tao file .env tai thu muc goc voi noi dung mau:

```env
SECRET_KEY=your-secret-key
DEBUG=True
ALLOWED_HOSTS=127.0.0.1,localhost

VNPAY_TMN_CODE=
VNPAY_HASH_SECRET=
VNPAY_URL=https://sandbox.vnpayment.vn/paymentv2/vpcpay.html
VNPAY_RETURN_URL=http://localhost:8000/vnpay/return/
VNPAY_IPN_URL=http://localhost:8000/vnpay/ipn/

MOMO_PARTNER_CODE=MOMO
MOMO_ACCESS_KEY=
MOMO_SECRET_KEY=
MOMO_ENDPOINT=
MOMO_RETURN_URL=
MOMO_IPN_URL=

BANK_ID=TCB
BANK_ACCOUNT_NO=
BANK_ACCOUNT_NAME=

CLOUDFLARE_TURNSTILE_SITE_KEY=
CLOUDFLARE_TURNSTILE_SECRET_KEY=

GOOGLE_OAUTH2_CLIENT_ID=
GOOGLE_OAUTH2_CLIENT_SECRET=

ANTHROPIC_API_KEY=

EMAIL_HOST_USER=
EMAIL_HOST_PASSWORD=
```

## 10. Du lieu mau va tai khoan mau

- Du lieu mau da co san trong db.sqlite3 de test nhanh.
- Tai khoan admin tao bang lenh:

```bash
python manage.py createsuperuser
```

- Tai khoan user thu nghiem co the tao truc tiep tren trang /register/.

## 11. Kiem thu

Da co test trong store/tests:
- test_vietqr_payment.py
- test_chatbot_orchestrator.py

Chay test:

```bash
python manage.py test
```

## 12. Minh chung cho giang vien cham

- Bao cao tong hop: docs/BAI DU AN_PTUD Python_Nhom 06.pdf
- Tai lieu thanh toan test hoc phan: docs/dulieuthanhtoan.md
- Ma nguon day du tren Git, lich su commit theo tien do.

## 13. Doi chieu tieu chi hoc phan (tom tat)

- He thong co CSDL quan he nhieu bang va khoa PK/FK.
- Co role Guest/User/Admin va phan quyen.
- Co CRUD cho cac nhom du lieu chinh.
- Co tim kiem/loc/sap xep.
- Co nghiep vu dat hang + xu ly trang thai thanh toan.
- Co dashboard thong ke va bao cao.
- Co test co ban va huong dan chay ro rang.

## 14. Luu y

- Moi thong tin API key/chung thuc de trong .env, khong hard-code vao source.
- Moi truong production nen dung PostgreSQL va cau hinh ALLOWED_HOSTS/DEBUG phu hop.
- Tai lieu nay uu tien tinh de cham, de cai dat va de demo.

---

Sinh vien thuc hien: Truong Quang Huy
