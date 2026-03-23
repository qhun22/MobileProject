"""
Tests for VietQR payment flow — expire, cancel, mark paid.
Covers the 3 main VietQR payment outcomes.
"""
import json
from datetime import timedelta
from decimal import Decimal

from django.test import TestCase, RequestFactory
from django.utils import timezone

from store.models import CustomUser, Order


class VietQRExpireTests(TestCase):
    """Test vietqr_expire view for expired and cancelled payments."""

    def setUp(self):
        self.user = CustomUser.objects.create_user(
            email='test@example.com',
            password='testpass123',
        )
        self.order = Order.objects.create(
            user=self.user,
            order_code='QHUN99901',
            total_amount=Decimal('5000000'),
            payment_method='vietqr',
            status='awaiting_payment',
            payment_status='pending',
            payment_code='QHUN88801',
            expires_at=timezone.now() + timedelta(minutes=15),
        )

    def test_expire_timer_sets_payment_expired(self):
        """Timer hết hạn → order.status='payment_expired', payment_status='expired'."""
        self.client.login(email='test@example.com', password='testpass123')
        resp = self.client.post(
            '/vietqr/expire/',
            data=json.dumps({'order_id': self.order.id, 'reason': 'expired'}),
            content_type='application/json',
        )
        self.assertEqual(resp.status_code, 200)
        self.order.refresh_from_db()
        self.assertEqual(self.order.status, 'payment_expired')
        self.assertEqual(self.order.payment_status, 'expired')

    def test_cancel_sets_payment_cancelled(self):
        """Khách chủ động hủy → order.status='payment_expired', payment_status='cancelled'."""
        self.client.login(email='test@example.com', password='testpass123')
        resp = self.client.post(
            '/vietqr/expire/',
            data=json.dumps({'order_id': self.order.id, 'reason': 'cancelled'}),
            content_type='application/json',
        )
        self.assertEqual(resp.status_code, 200)
        self.order.refresh_from_db()
        self.assertEqual(self.order.status, 'payment_expired')
        self.assertEqual(self.order.payment_status, 'cancelled')

    def test_mark_paid_sets_processing(self):
        """Khách báo đã chuyển khoản → order.status='processing', payment_status='paid'."""
        self.client.login(email='test@example.com', password='testpass123')
        resp = self.client.post(
            '/vietqr/mark-paid/',
            data=json.dumps({'order_id': self.order.id}),
            content_type='application/json',
        )
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertTrue(data['success'])
        self.order.refresh_from_db()
        self.assertEqual(self.order.status, 'processing')
        self.assertEqual(self.order.payment_status, 'paid')

    def test_expire_requires_auth(self):
        """Unauthenticated request should redirect (302)."""
        resp = self.client.post(
            '/vietqr/expire/',
            data=json.dumps({'order_id': self.order.id, 'reason': 'expired'}),
            content_type='application/json',
        )
        self.assertEqual(resp.status_code, 302)

    def test_expire_wrong_user(self):
        """Different user cannot expire another user's order."""
        other_user = CustomUser.objects.create_user(
            email='other@example.com',
            password='otherpass123',
        )
        self.client.login(email='other@example.com', password='otherpass123')
        resp = self.client.post(
            '/vietqr/expire/',
            data=json.dumps({'order_id': self.order.id, 'reason': 'expired'}),
            content_type='application/json',
        )
        self.assertEqual(resp.status_code, 404)

    def test_expire_already_delivered_no_change(self):
        """Delivered order should not be changed by expire call."""
        self.order.status = 'delivered'
        self.order.payment_status = 'paid'
        self.order.save()
        self.client.login(email='test@example.com', password='testpass123')
        resp = self.client.post(
            '/vietqr/expire/',
            data=json.dumps({'order_id': self.order.id, 'reason': 'expired'}),
            content_type='application/json',
        )
        self.assertEqual(resp.status_code, 200)
        self.order.refresh_from_db()
        self.assertEqual(self.order.status, 'delivered')
        self.assertEqual(self.order.payment_status, 'paid')
