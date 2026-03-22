"""
Hot Sale Views - Quản lý sản phẩm trong tab HOTSALE trang chủ
"""
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.contrib.admin.views.decorators import staff_member_required
from django.db.models import Q


@staff_member_required
@require_http_methods(["GET"])
def hotsale_list(request):
    """Trả về danh sách tất cả HotSaleProduct"""
    from store.models import HotSaleProduct

    entries = HotSaleProduct.objects.select_related('product__brand').order_by('sort_order', 'created_at')

    data = []
    for entry in entries:
        product = entry.product
        data.append({
            'id': entry.id,
            'product_id': product.id,
            'name': product.name,
            'brand': product.brand.name if product.brand else '',
            'price': str(product.price) if product.price else '0',
            'image_url': product.image.url if product.image else '',
            'sort_order': entry.sort_order,
            'is_active': entry.is_active,
        })

    return JsonResponse({'success': True, 'entries': data})


@staff_member_required
@require_http_methods(["POST"])
def hotsale_add(request):
    """Thêm sản phẩm vào danh sách Hot Sale"""
    from store.models import HotSaleProduct, Product

    product_id = request.POST.get('product_id', '').strip()
    sort_order = request.POST.get('sort_order', '0').strip()
    is_active = request.POST.get('is_active', 'true').lower() == 'true'

    if not product_id:
        return JsonResponse({'success': False, 'message': 'Vui lòng chọn sản phẩm'})

    try:
        product = Product.objects.get(id=product_id)
    except Product.DoesNotExist:
        return JsonResponse({'success': False, 'message': 'Sản phẩm không tồn tại'})

    if HotSaleProduct.objects.filter(product=product).exists():
        return JsonResponse({'success': False, 'message': 'Sản phẩm này đã có trong danh sách Hot Sale'})

    try:
        sort_val = int(sort_order)
    except (ValueError, TypeError):
        sort_val = 0

    HotSaleProduct.objects.create(
        product=product,
        sort_order=sort_val,
        is_active=is_active,
    )

    return JsonResponse({'success': True, 'message': f'Đã thêm "{product.name}" vào Hot Sale'})


@staff_member_required
@require_http_methods(["POST"])
def hotsale_update(request):
    """Cập nhật sort_order hoặc is_active của một entry"""
    from store.models import HotSaleProduct

    entry_id = request.POST.get('entry_id', '').strip()
    sort_order = request.POST.get('sort_order', None)
    is_active = request.POST.get('is_active', None)

    if not entry_id:
        return JsonResponse({'success': False, 'message': 'Thiếu entry_id'})

    try:
        entry = HotSaleProduct.objects.get(id=entry_id)
    except HotSaleProduct.DoesNotExist:
        return JsonResponse({'success': False, 'message': 'Không tìm thấy mục này'})

    if sort_order is not None:
        try:
            entry.sort_order = int(sort_order)
        except (ValueError, TypeError):
            pass

    if is_active is not None:
        entry.is_active = is_active.lower() == 'true'

    entry.save()

    return JsonResponse({'success': True, 'message': 'Đã cập nhật'})


@staff_member_required
@require_http_methods(["POST"])
def hotsale_auto_top_discount(request):
    """Tự động thêm top sản phẩm có % giảm giá cao nhất vào Hot Sale"""
    from store.models import HotSaleProduct, Product, ProductVariant
    from django.db.models import Max

    limit = 10
    try:
        limit = int(request.POST.get('limit', 10))
        limit = max(1, min(limit, 50))
    except (ValueError, TypeError):
        pass

    # Lấy các product_id đã có trong hotsale
    existing_ids = set(HotSaleProduct.objects.values_list('product_id', flat=True))

    # Lấy max discount_percent từ ProductVariant theo từng Product
    top_products = (
        ProductVariant.objects
        .filter(discount_percent__gt=0, detail__product__is_active=True)
        .exclude(detail__product_id__in=existing_ids)
        .values('detail__product_id')
        .annotate(max_discount=Max('discount_percent'))
        .order_by('-max_discount')[:limit]
    )

    added = []
    for idx, row in enumerate(top_products):
        product_id = row['detail__product_id']
        max_discount = row['max_discount']
        try:
            product = Product.objects.get(id=product_id)
        except Product.DoesNotExist:
            continue
        entry = HotSaleProduct.objects.create(
            product=product,
            sort_order=idx,
            is_active=True,
        )
        added.append({'id': entry.id, 'name': product.name, 'discount_percent': max_discount})

    if not added:
        return JsonResponse({'success': False, 'message': 'Không có sản phẩm nào phù hợp (chưa trong Hot Sale và có % giảm giá > 0)'})

    return JsonResponse({
        'success': True,
        'message': f'Đã thêm {len(added)} sản phẩm vào Hot Sale!',
        'added': added,
    })


@staff_member_required
@require_http_methods(["POST"])
def hotsale_delete(request):
    """Xóa một entry khỏi danh sách Hot Sale (không xóa Product)"""
    from store.models import HotSaleProduct

    entry_id = request.POST.get('entry_id', '').strip()

    if not entry_id:
        return JsonResponse({'success': False, 'message': 'Thiếu entry_id'})

    try:
        entry = HotSaleProduct.objects.get(id=entry_id)
        name = entry.product.name
        entry.delete()
        return JsonResponse({'success': True, 'message': f'Đã xóa "{name}" khỏi Hot Sale'})
    except HotSaleProduct.DoesNotExist:
        return JsonResponse({'success': False, 'message': 'Không tìm thấy mục này'})
