import hmac
import hashlib
import uuid
import json
import requests
from django.conf import settings


class MoMoUtil:
    def __init__(self):
        self.partner_code = getattr(settings, 'MOMO_PARTNER_CODE', 'MOMO')
        self.access_key = getattr(settings, 'MOMO_ACCESS_KEY', 'F8BBA842ECF85')
        self.secret_key = getattr(settings, 'MOMO_SECRET_KEY', 'K951B6PE1waDMi640xX08PD3vg6EkVlz')
        self.endpoint = getattr(settings, 'MOMO_ENDPOINT', 'https://test-payment.momo.vn/v2/gateway/api/create')
        self.redirect_url = getattr(settings, 'MOMO_RETURN_URL', 'http://localhost:8000/momo/return/')
        self.ipn_url = getattr(settings, 'MOMO_IPN_URL', 'http://localhost:8000/momo/ipn/')

    def create_payment(self, amount, order_id, order_info, extra_data=''):
        request_id = str(uuid.uuid4())

        # Signature format theo MoMo SDK chinh thuc
        # Dung payWithMethod de ho tro ATM/Card
        raw_signature = (
            f"accessKey={self.access_key}&amount={amount}&extraData={extra_data}&ipnUrl={self.ipn_url}"
            f"&orderId={order_id}&orderInfo={order_info}&partnerCode={self.partner_code}"
            f"&redirectUrl={self.redirect_url}&requestId={request_id}&requestType=payWithMethod"
        )

        # Dung ascii nhu MoMo SDK
        signature = self._sign(raw_signature)

        data = {
            'partnerCode': self.partner_code,
            'partnerName': 'Test',
            'storeId': 'MomoTestStore',
            'requestId': request_id,
            'amount': str(amount),
            'orderId': order_id,
            'orderInfo': order_info,
            'redirectUrl': self.redirect_url,
            'ipnUrl': self.ipn_url,
            'lang': 'vi',
            'extraData': extra_data,
            'requestType': 'payWithMethod',
            'orderGroupId': '',
            'autoCapture': True,
            'signature': signature
        }

        try:
            response = requests.post(
                self.endpoint,
                data=json.dumps(data),
                headers={'Content-Type': 'application/json'}
            )
            result = response.json()
            print(f"[MoMo] Response: {result}")  # Debug
            return result
        except Exception as e:
            print(f"[MoMo] Error: {e}")  # Debug
            return {'error': True, 'message': str(e)}

    def verify_signature(self, data):
        return self.verify_return_signature(data)

    def verify_return_signature(self, data):
        access_key = data.get('accessKey', self.access_key)
        raw_signature = (
            f"accessKey={access_key}&amount={data.get('amount', '')}"
            f"&extraData={data.get('extraData', '')}&message={data.get('message', '')}"
            f"&orderId={data.get('orderId', '')}&orderInfo={data.get('orderInfo', '')}"
            f"&orderType={data.get('orderType', '')}&partnerCode={data.get('partnerCode', '')}"
            f"&payType={data.get('payType', '')}&requestId={data.get('requestId', '')}"
            f"&responseTime={data.get('responseTime', '')}"
            f"&resultCode={data.get('resultCode', '')}&transId={data.get('transId', '')}"
        )

        expected_signature = self._sign(raw_signature)
        return data.get('signature') == expected_signature

    def verify_ipn_signature(self, data):
        return self.verify_return_signature(data)

    def _sign(self, raw_signature):
        return hmac.new(
            bytes(self.secret_key, 'ascii'),
            bytes(raw_signature, 'ascii'),
            hashlib.sha256
        ).hexdigest()

    @staticmethod
    def build_payment_url(amount, order_id, order_info):
        momo = MoMoUtil()
        return momo.create_payment(amount, order_id, order_info)
