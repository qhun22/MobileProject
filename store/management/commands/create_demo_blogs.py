from django.core.management.base import BaseCommand
from store.models import BlogPost


class Command(BaseCommand):
    help = 'Tạo 2 bài blog demo cho SEO'

    def handle(self, *args, **options):
        posts = [
            {
                'title': 'iPhone 16 Pro Max vs Samsung Galaxy S25 Ultra: Đâu là lựa chọn tốt nhất 2025?',
                'summary': 'So sánh toàn diện iPhone 16 Pro Max và Samsung Galaxy S25 Ultra về hiệu năng, camera, pin và giá cả. Giúp bạn đưa ra lựa chọn thông minh.',
                'content': (
                    'iPhone 16 Pro Max và Samsung Galaxy S25 Ultra là hai flagship đỉnh cao nhất năm 2025. '
                    'Cả hai đều hướng đến những người dùng khó tính nhất với giá bán trên 30 triệu đồng.\n\n'
                    'Hiệu năng\n'
                    'iPhone 16 Pro Max trang bị chip Apple A18 Pro — bộ xử lý di động mạnh nhất trên thị trường, '
                    'xử lý các tác vụ AI tại chỗ (on-device) cực kỳ nhanh. '
                    'Samsung Galaxy S25 Ultra sử dụng Snapdragon 8 Elite for Galaxy được tối ưu riêng, '
                    'hiệu năng đa nhiệm vượt trội với RAM 12 GB.\n\n'
                    'Camera\n'
                    'Cả hai đều có hệ thống camera chuyên nghiệp 4 ống kính. '
                    'iPhone 16 Pro Max nổi bật với khả năng quay video 4K/120fps ProRes và chip Neural Engine thế hệ mới. '
                    'Galaxy S25 Ultra gây ấn tượng với camera chính 200 MP, zoom quang học 5x và tính năng AI generative editing.\n\n'
                    'Pin & Sạc\n'
                    'iPhone 16 Pro Max có pin 4685 mAh, sạc nhanh 27W và sạc không dây MagSafe 25W. '
                    'Galaxy S25 Ultra vượt trội hơn với pin 5000 mAh và sạc có dây 45W.\n\n'
                    'Kết luận\n'
                    'Nếu bạn trong hệ sinh thái Apple, iPhone 16 Pro Max là lựa chọn hoàn hảo. '
                    'Nếu bạn yêu thích Android và cần linh hoạt hơn, Galaxy S25 Ultra xứng đáng đồng tiền. '
                    'Hãy đến QHUN22 Mobile để được tư vấn và trải nghiệm thực tế cả hai dòng máy!'
                ),
                'is_active': True,
            },
            {
                'title': 'Top 5 Điện Thoại Chính Hãng Giá Dưới 10 Triệu Đáng Mua Nhất 2025',
                'summary': 'Tổng hợp 5 mẫu điện thoại chính hãng giá dưới 10 triệu đồng có hiệu năng tốt, camera chất lượng cao, pin trâu bảo hành tại QHUN22 Mobile.',
                'content': (
                    'Thị trường điện thoại tầm trung ngày càng cạnh tranh gay gắt, '
                    'mang lại nhiều lựa chọn xuất sắc cho người dùng có ngân sách dưới 10 triệu đồng.\n\n'
                    '1. Xiaomi Redmi Note 14 Pro\n'
                    'Chip Snapdragon 7s Gen 3, RAM 8 GB, camera chính 200 MP, pin 5110 mAh sạc nhanh 45W. '
                    'Màn hình AMOLED 120Hz, thiết kế có kính mặt lưng sang trọng. Giá từ 7,5 triệu đồng.\n\n'
                    '2. Samsung Galaxy A56\n'
                    'Chip Exynos 1580 tiết kiệm điện, màn AMOLED 120Hz, pin 5000 mAh sạc 45W, '
                    'camera 50 MP OIS. Chống nước IP67, bảo hành 4 năm Android update. Giá từ 9 triệu đồng.\n\n'
                    '3. OPPO Reno 13\n'
                    'Chip Dimensity 8350, RAM 12 GB, sạc nhanh SUPERVOOC 80W đầy pin chỉ 40 phút. '
                    'Thiết kế Haze Glass cao cấp, camera dải động rộng AI. Giá từ 9,5 triệu đồng.\n\n'
                    '4. Vivo V40\n'
                    'Chip Snapdragon 7 Gen 3, hợp tác với Zeiss cho camera chân dung xuất sắc, '
                    'pin 5500 mAh sạc 80W, màn 3D curved AMOLED 120Hz. Giá từ 9 triệu đồng.\n\n'
                    '5. Realme GT 6T\n'
                    'Chip Snapdragon 7+ Gen 3 — hiệu năng gaming cực mạnh trong tầm giá, '
                    'pin 5500 mAh sạc siêu nhanh 120W (đầy pin chỉ 19 phút). Giá từ 8,5 triệu đồng.\n\n'
                    'Lời khuyên\n'
                    'Tất cả 5 mẫu trên đều có mặt tại QHUN22 Mobile với giá chính hãng, '
                    'bảo hành 12 tháng và hỗ trợ trả góp 0% lãi suất. '
                    'Ghé cửa hàng hoặc nhắn tin để được tư vấn miễn phí!'
                ),
                'is_active': True,
            },
        ]

        for data in posts:
            obj, created = BlogPost.objects.get_or_create(
                title=data['title'],
                defaults={k: v for k, v in data.items() if k != 'title'},
            )
            status = 'Tạo mới' if created else 'Đã tồn tại'
            self.stdout.write(f'{status}: {obj.title}')

        self.stdout.write(self.style.SUCCESS('Hoàn tất!'))
