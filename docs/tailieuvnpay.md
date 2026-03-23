# Tài liệu tích hợp VNPay Payment

> Tài liệu kỹ thuật mô tả cách hệ thống QHUN22 tích hợp cổng thanh toán VNPay.

---

## 1. Tổng quan

**VNPay** là cổng thanh toán trực tuyến hỗ trợ thanh toán qua thẻ ATM nội địa, thẻ quốc tế (Visa/MasterCard), và quét QR VNPay. Hệ thống sử dụng **VNPay API v2.1.0**.

### Môi trường

| Môi trường | Payment URL |
|:-----------|:------------|
| **Sandbox (test)** | `https://sandbox.vnpayment.vn/paymentv2/vpcpay.html` |
| **Production** | `https://pay.vnpay.vn/vpcpay.html` |

### File liên quan trong dự án

| File | Chức năng |
|:-----|:---------|
| `store/vnpay_utils.py` | Class `VNPayUtil` — tạo URL thanh toán + xác thực chữ ký |
| `store/views/payment_views.py` | View xử lý tạo đơn, return URL, IPN callback |
| `config/settings.py` | Cấu hình `VNPAY_CONFIG` |
| `config/urls.py` | URL routing cho VNPay return/IPN |
| `store/urls.py` | URL tạo thanh toán VNPay |

---

## 2. Cấu hình

### Biến môi trường (`.env`)

```env
VNPAY_TMN_CODE=your-merchant-code
VNPAY_HASH_SECRET=your-hash-secret
VNPAY_URL=https://sandbox.vnpayment.vn/paymentv2/vpcpay.html
VNPAY_RETURN_URL=http://localhost:8000/vnpay/return/
```

### Object cấu hình trong `settings.py`

```python
VNPAY_CONFIG = {
    'vnp_TmnCode': os.getenv('VNPAY_TMN_CODE'),
    'vnp_HashSecret': os.getenv('VNPAY_HASH_SECRET'),
    'vnp_Url': os.getenv('VNPAY_URL', 'https://sandbox.vnpayment.vn/paymentv2/vpcpay.html'),
    'vnp_ReturnUrl': os.getenv('VNPAY_RETURN_URL', 'http://localhost:8000/vnpay/return/'),
    'vnp_IpnUrl': os.getenv('VNPAY_IPN_URL', 'http://localhost:8000/vnpay/ipn/'),
    'vnp_OrderType': 'billpayment',
    'vnp_Version': '2.1.0',
    'vnp_Command': 'pay',
}
```

### Tham số cấu hình

| Tham số | Mô tả |
|:--------|:------|
| `vnp_TmnCode` | Mã website (merchant) do VNPay cấp |
| `vnp_HashSecret` | Chuỗi bí mật để tạo chữ ký HMAC |
| `vnp_Url` | URL cổng thanh toán VNPay |
| `vnp_ReturnUrl` | URL VNPay redirect về sau thanh toán |
| `vnp_IpnUrl` | URL VNPay gọi IPN callback |
| `vnp_OrderType` | Loại đơn hàng (`billpayment`) |
| `vnp_Version` | Phiên bản API (`2.1.0`) |
| `vnp_Command` | Lệnh thanh toán (`pay`) |

---

## 3. Luồng thanh toán

```
Khách hàng chọn "Thanh toán VNPay"
        ↓
[1] Server tạo URL thanh toán (gồm chữ ký HMAC SHA512)
        ↓
[2] Redirect khách sang trang VNPay
        ↓
[3] Khách chọn ngân hàng + nhập thông tin thẻ/OTP
        ↓
[4] VNPay redirect về RETURN_URL → server xác thực + hiển thị kết quả
    VNPay gọi IPN_URL (async) → server cập nhật đơn hàng
```

### Bước 1: Tạo mã đơn hàng

```python
order_code = VNPayUtil.generate_order_code()
# Kết quả: "QHun-20260323143022-A1B2C3D4"
# Format: QHun-YYYYMMDDHHmmss-RANDOM (max 50 ký tự)
```

### Bước 2: Xây dựng tham số thanh toán

```python
vnp_params = {
    'vnp_Version': '2.1.0',
    'vnp_Command': 'pay',
    'vnp_TmnCode': 'MERCHANT_CODE',
    'vnp_Amount': 150000000,           # = 1,500,000 VND × 100
    'vnp_CreateDate': '20260323143022',
    'vnp_CurrCode': 'VND',
    'vnp_IpAddr': '127.0.0.1',
    'vnp_Locale': 'vn',
    'vnp_OrderInfo': 'Thanh toan don hang QHun-...',
    'vnp_OrderType': 'billpayment',
    'vnp_ReturnUrl': 'http://localhost:8000/vnpay/return/',
    'vnp_TxnRef': 'QHun-20260323143022-A1B2C3D4',
}
```

**Lưu ý quan trọng:** `vnp_Amount` phải **nhân 100** (đơn vị xu). Ví dụ 1,500,000 VND → gửi `150000000`.

### Bước 3: Tạo chữ ký (HMAC SHA512)

**Quy trình:**

1. Sắp xếp tham số theo thứ tự **alphabet** theo key
2. Ghép chuỗi: `key1=value1&key2=value2&...`
3. Mỗi value được encode bằng `urllib.parse.quote_plus()`
4. Ký bằng HMAC SHA512 với `vnp_HashSecret`

```python
# Sắp xếp params theo key
sorted_keys = sorted(vnp_params.keys())

# Ghép chuỗi hash_data
hash_data = '&'.join(
    f"{k}={urllib.parse.quote_plus(str(vnp_params[k]))}"
    for k in sorted_keys
)

# Tạo chữ ký HMAC SHA512
signature = hmac.new(
    secret_key.encode(),
    hash_data.encode(),
    hashlib.sha512
).hexdigest()
```

### Bước 4: Tạo URL thanh toán

```python
payment_url = VNPayUtil.build_payment_url(
    amount=1500000,
    order_code='QHun-20260323143022-A1B2C3D4',
    order_description='Thanh toan don hang QHUN22',
    ip_address='127.0.0.1'
)
# Kết quả: https://sandbox.vnpayment.vn/paymentv2/vpcpay.html?vnp_Amount=150000000&...&vnp_SecureHash=abc123...
```

→ Redirect khách hàng đến URL này.

---

## 4. Xử lý kết quả trả về

### 4a. Return URL (`/vnpay/return/`)

Khi khách thanh toán xong, VNPay redirect về URL này kèm các query params:

```
/vnpay/return/?vnp_Amount=150000000&vnp_BankCode=NCB&vnp_OrderInfo=...
&vnp_ResponseCode=00&vnp_SecureHash=...&vnp_TransactionNo=...&vnp_TxnRef=...
```

**Xử lý:**

```python
is_valid, message = VNPayUtil.verify_payment_response(request.GET.dict())

if is_valid:
    # Thanh toán thành công
    order.status = 'processing'
    order.payment_status = 'paid'
    order.save()
else:
    # Thanh toán thất bại
    # message chứa lý do lỗi bằng tiếng Việt
```

### 4b. IPN Callback (`/vnpay/ipn/`)

VNPay gọi server-to-server (GET) để thông báo kết quả:

1. Xác thực chữ ký `vnp_SecureHash`
2. Kiểm tra `vnp_ResponseCode` (00 = thành công)
3. Cập nhật trạng thái đơn hàng
4. Trả về response cho VNPay:

```json
{"RspCode": "00", "Message": "Confirm Success"}
```

---

## 5. Xác thực chữ ký phản hồi

```python
def verify_payment_response(response_data, secret_key=None):
    # 1. Tách vnp_SecureHash ra khỏi data
    vnp_secure_hash = response_data.pop('vnp_SecureHash', '')
    response_data.pop('vnp_SecureHashType', None)

    # 2. Tính lại chữ ký từ các param còn lại
    expected_hash = calculate_checksum(response_data, secret_key)

    # 3. So sánh
    if vnp_secure_hash != expected_hash:
        return False, "Checksum không hợp lệ"

    # 4. Kiểm tra mã phản hồi
    if response_data['vnp_ResponseCode'] != '00':
        return False, get_response_message(response_data['vnp_ResponseCode'])

    return True, "OK"
```

---

## 6. URL Routing

| URL | Method | Đặt tại | Chức năng |
|:----|:-------|:--------|:---------|
| `/vnpay/create/` | POST | `store/urls.py` | Tạo URL thanh toán VNPay |
| `/vnpay/return/` | GET | `config/urls.py` | VNPay redirect về sau thanh toán |
| `/vnpay/ipn/` | GET | `config/urls.py` | VNPay gọi IPN callback (server-to-server) |

---

## 7. Mã phản hồi (Response Code)

| Code | Ý nghĩa |
|:-----|:---------|
| `00` | Giao dịch thành công |
| `01` | Giao dịch bị từ chối (liên quan đến thẻ/tài khoản) |
| `02` | Không liên lạc được ngân hàng phát hành thẻ |
| `03` | Merchant không hợp lệ |
| `04` | Đơn vị tiền tệ không được hỗ trợ |
| `06` | Lỗi trong quá trình xử lý giao dịch |
| `07` | Merchant không được phép thực hiện giao dịch này |
| `11` | Thẻ hết hạn hoặc bị khóa |
| `12` | Thẻ chưa đăng ký Internet Banking |
| `13` | Phương thức thanh toán không hợp lệ |
| `15` | Ngân hàng từ chối giao dịch |
| `99` | Người dùng hủy giao dịch |

---

## 8. Model lưu trữ giao dịch

### `VNPayPayment`

| Field | Type | Mô tả |
|:------|:-----|:------|
| `user` | ForeignKey | Người thanh toán |
| `amount` | Decimal | Số tiền |
| `order_code` | CharField (unique) | Mã giao dịch VNPay (`vnp_TxnRef`) |
| `transaction_no` | CharField | Mã giao dịch từ VNPay |
| `transaction_status` | CharField | Trạng thái giao dịch |
| `response_code` | CharField | Mã phản hồi |
| `response_message` | CharField | Thông báo phản hồi |
| `pay_method` | CharField | Phương thức thanh toán (ATM, QR, ...) |
| `status` | CharField | pending / paid / failed / cancelled |
| `paid_at` | DateTimeField | Thời gian thanh toán thành công |

---

## 9. So sánh VNPay vs MoMo

| Tiêu chí | VNPay | MoMo |
|:---------|:------|:-----|
| **Thuật toán ký** | HMAC SHA512 | HMAC SHA256 |
| **Đơn vị tiền** | Xu (× 100) | VND (nguyên) |
| **Request type** | Redirect (GET params) | POST JSON → nhận payUrl |
| **IPN method** | GET | POST |
| **Encoding** | UTF-8 + quote_plus | ASCII |

---

## 10. Lưu ý khi triển khai

- **Sandbox:** Dùng thẻ test do VNPay cung cấp (xem trang sandbox VNPay)
- **vnp_TxnRef:** Phải unique mỗi giao dịch — nếu trùng VNPay sẽ từ chối
- **vnp_Amount:** Luôn nhân 100 (1,500,000 VND → `150000000`)
- **vnp_IpAddr:** IP thực của khách (dùng `request.META`)
- **IPN URL:** Cần server public để VNPay gọi được (localhost không nhận IPN)
- **Return URL:** Đăng ký trong portal VNPay — URL không khớp sẽ bị từ chối
- **Production:** Thay `VNPAY_TMN_CODE` + `VNPAY_HASH_SECRET` + đổi URL sang production

---

> Tham khảo: [VNPay Sandbox Portal](https://sandbox.vnpayment.vn/apis/)
