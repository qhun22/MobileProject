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
