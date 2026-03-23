# Tài liệu tích hợp MoMo Payment

> Tài liệu kỹ thuật mô tả cách hệ thống QHUN22 tích hợp cổng thanh toán MoMo.

---

## 1. Tổng quan

**MoMo** là ví điện tử phổ biến tại Việt Nam. Hệ thống sử dụng **MoMo Payment Gateway API v2** với phương thức `payWithMethod` (hỗ trợ thanh toán bằng ví MoMo, thẻ ATM, thẻ tín dụng).

### Môi trường

| Môi trường | Endpoint |
|:-----------|:---------|
| **Sandbox (test)** | `https://test-payment.momo.vn/v2/gateway/api/create` |
| **Production** | `https://payment.momo.vn/v2/gateway/api/create` |

### File liên quan trong dự án

| File | Chức năng |
|:-----|:---------|
| `store/momo_utils.py` | Class `MoMoUtil` — tạo thanh toán + xác thực chữ ký |
| `store/views/payment_views.py` | View xử lý tạo đơn, return URL, IPN callback |
| `config/settings.py` | Cấu hình biến MoMo |
| `store/urls.py` | URL routing cho MoMo |

---

## 2. Cấu hình

### Biến môi trường (`.env`)

```env
MOMO_PARTNER_CODE=MOMO
MOMO_ACCESS_KEY=xxx
MOMO_SECRET_KEY=xxx
MOMO_ENDPOINT=https://test-payment.momo.vn/v2/gateway/api/create
MOMO_RETURN_URL=http://localhost:8000/momo/return/
MOMO_IPN_URL=http://localhost:8000/momo/ipn/
```

> **Lưu ý:** Các giá trị trên là tài khoản **sandbox** của MoMo dùng để test. Khi lên production cần thay bằng thông tin merchant thật.

### Tham số cấu hình

| Tham số | Mô tả |
|:--------|:------|
| `MOMO_PARTNER_CODE` | Mã đối tác do MoMo cấp |
| `MOMO_ACCESS_KEY` | Access key để xác thực |
| `MOMO_SECRET_KEY` | Secret key để tạo chữ ký HMAC |
| `MOMO_ENDPOINT` | URL API tạo thanh toán |
| `MOMO_RETURN_URL` | URL MoMo redirect về sau khi thanh toán |
| `MOMO_IPN_URL` | URL MoMo gọi callback (server-to-server) |

---

## 3. Luồng thanh toán

```
Khách hàng chọn "Thanh toán MoMo"
        ↓
[1] Server tạo request → gửi POST đến MoMo API
        ↓
[2] MoMo trả về payUrl → redirect khách sang trang MoMo
        ↓
[3] Khách thanh toán trên MoMo (quét QR / nhập OTP)
        ↓
[4] MoMo redirect về RETURN_URL → hiển thị kết quả
    MoMo gọi IPN_URL (async) → server cập nhật đơn hàng
```

### Bước 1: Tạo yêu cầu thanh toán

Server gọi `MoMoUtil.create_payment()` với các thông tin:

```python
MoMoUtil.build_payment_url(
    amount=1500000,                    # Số tiền (VND)
    order_id='MOMO-20260323-ABC123',   # Mã đơn hàng (unique)
    order_info='Thanh toán đơn hàng QHUN22'
)
```

### Bước 2: Tạo chữ ký (signature)

**Chuỗi raw để ký:**

```
accessKey={access_key}&amount={amount}&extraData={extra_data}&ipnUrl={ipn_url}
&orderId={order_id}&orderInfo={order_info}&partnerCode={partner_code}
&redirectUrl={redirect_url}&requestId={request_id}&requestType=payWithMethod
```

**Thuật toán:** HMAC SHA256, key = `MOMO_SECRET_KEY`, encoding = ASCII

```python
signature = hmac.new(
    bytes(secret_key, 'ascii'),
    bytes(raw_signature, 'ascii'),
    hashlib.sha256
).hexdigest()
```

### Bước 3: Gửi request đến MoMo

**Method:** `POST`  
**Content-Type:** `application/json`  
**URL:** `https://test-payment.momo.vn/v2/gateway/api/create`

**Request body:**

```json
{
    "partnerCode": "MOMO",
    "partnerName": "Test",
    "storeId": "MomoTestStore",
    "requestId": "uuid-random",
    "amount": "1500000",
    "orderId": "MOMO-20260323-ABC123",
    "orderInfo": "Thanh toán đơn hàng QHUN22",
    "redirectUrl": "http://localhost:8000/momo/return/",
    "ipnUrl": "http://localhost:8000/momo/ipn/",
    "lang": "vi",
    "extraData": "",
    "requestType": "payWithMethod",
    "orderGroupId": "",
    "autoCapture": true,
    "signature": "abc123..."
}
```

**Response thành công:**

```json
{
    "partnerCode": "MOMO",
    "orderId": "MOMO-20260323-ABC123",
    "requestId": "uuid-random",
    "amount": 1500000,
    "responseTime": 1679580000000,
    "message": "Thành công.",
    "resultCode": 0,
    "payUrl": "https://test-payment.momo.vn/pay/...",
    "shortLink": "https://test-payment.momo.vn/shortlink/..."
}
```

→ Redirect khách hàng đến `payUrl`.

### Bước 4: Xử lý kết quả trả về

#### 4a. Return URL (`/momo/return/`)

Khi khách thanh toán xong, MoMo redirect về URL này với các tham số trên query string. Server:

1. Lấy các tham số từ `request.GET`
2. Xác thực chữ ký (verify signature)
3. Kiểm tra `resultCode` (0 = thành công)
4. Cập nhật trạng thái đơn hàng
5. Hiển thị trang kết quả cho khách

#### 4b. IPN Callback (`/momo/ipn/`)

MoMo gọi server-to-server (POST) để thông báo kết quả. Xử lý tương tự return nhưng:

- Đây là callback **bất đồng bộ** — luôn chạy ngay cả khi khách đóng trình duyệt
- Server phải trả về HTTP 200 + JSON `{"resultCode": 0}` để MoMo biết đã nhận

---

## 4. Xác thực chữ ký phản hồi

**Chuỗi raw để verify:**

```
accessKey={access_key}&amount={amount}&extraData={extraData}
&orderId={orderId}&orderInfo={orderInfo}&partnerCode={partnerCode}
&requestId={requestId}
```

**So sánh:**

```python
expected_signature = hmac.new(
    bytes(secret_key, 'ascii'),
    bytes(raw_signature, 'ascii'),
    hashlib.sha256
).hexdigest()

is_valid = (data['signature'] == expected_signature)
```

---

## 5. URL Routing

| URL | Method | Chức năng |
|:----|:-------|:---------|
| `/momo/create/` | POST | Tạo thanh toán MoMo |
| `/momo/return/` | GET | MoMo redirect về sau thanh toán |
| `/momo/ipn/` | POST | MoMo gọi callback (server-to-server) |

---

## 6. Xử lý lỗi

| resultCode | Ý nghĩa |
|:-----------|:---------|
| `0` | Thành công |
| `1006` | Người dùng hủy giao dịch |
| `1005` | URL thanh toán hết hạn |
| `1001` | Giao dịch thất bại do thiếu thông tin |
| `Khác` | Lỗi khác — xem [MoMo Docs](https://developers.momo.vn/) |

---

## 7. Lưu ý khi triển khai

- **Sandbox:** Dùng app MoMo Test để quét QR (không dùng app MoMo thật)
- **IPN URL:** Cần server public (hoặc dùng ngrok khi dev) để MoMo gọi được
- **Idempotency:** `orderId` phải unique — nếu trùng MoMo sẽ trả lỗi
- **Amount:** Gửi dạng string, đơn vị VND (không nhân 100 như VNPay)
- **Production:** Thay toàn bộ credential sandbox bằng credential thật từ MoMo Business

---

> Tham khảo: [MoMo Developer Documentation](https://developers.momo.vn/)
