"""
Sitemap configuration cho QHUN22 Mobile
Đăng ký tại: /sitemap.xml
"""
from django.contrib.sitemaps import Sitemap
from django.urls import reverse
from .models import Product, Brand, BlogPost


class StaticViewSitemap(Sitemap):
    """Các trang tĩnh quan trọng"""
    priority = 1.0
    changefreq = 'daily'
    protocol = 'https'

    def items(self):
        return ['store:home', 'store:blog_page_list']

    def location(self, item):
        return reverse(item)


class ProductSitemap(Sitemap):
    """Tất cả sản phẩm đang active"""
    changefreq = 'weekly'
    priority = 0.9
    protocol = 'https'

    def items(self):
        return Product.objects.filter(is_active=True).order_by('-updated_at')

    def lastmod(self, obj):
        return obj.updated_at

    def location(self, obj):
        return reverse('store:product_detail', kwargs={'slug': obj.slug})


class BrandSitemap(Sitemap):
    """Trang filter theo hãng"""
    changefreq = 'weekly'
    priority = 0.7
    protocol = 'https'

    def items(self):
        return Brand.objects.filter(is_active=True)

    def lastmod(self, obj):
        return obj.updated_at

    def location(self, obj):
        return reverse('store:product_search') + f'?brand={obj.slug}'


class BlogSitemap(Sitemap):
    """Bài viết blog"""
    changefreq = 'monthly'
    priority = 0.6
    protocol = 'https'

    def items(self):
        return BlogPost.objects.filter(is_active=True).order_by('-updated_at')

    def lastmod(self, obj):
        return obj.updated_at

    def location(self, obj):
        return reverse('store:blog_page_detail', kwargs={'post_id': obj.id})
