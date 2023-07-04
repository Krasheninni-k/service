from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
from django.db.models import Max, Sum, F

from app.models import Goods, Orders, OrderDetail, Catalog

User = get_user_model()


def create_goods(
        order, order_detail, quantity):
    for i in range(quantity):
        good = Goods.objects.create(
            order_number=order,
            order_date=order,
            created_by=order.created_by,
            product=order_detail,
            cost_price_RUB=order_detail,
            ordering_price_RMB=order_detail,
            received_date=order
            )
        good.save()


def max_value():
    result = Orders.objects.aggregate(max_value=Max('order_number'))['max_value']
    return result if result is not None else 0

def change_product_list(instance):
    order = get_object_or_404(Orders, pk=instance.order_number.id)
    order_detail_list = OrderDetail.objects.filter(order_number=order.id)
    product_list = []
    for i in range(len(order_detail_list)):
        order_detail = order_detail_list[i]
        product = Catalog.objects.get(id=order_detail.product_id)
        product_list.append(f'{product} - {order_detail.quantity} ед.')
        order.product_list = ', '.join(str(item) for item in product_list)
        order.save()
    total_cost = OrderDetail.objects.filter(
         order_number=order.id).aggregate(
         total_cost=Sum(F('quantity') * F('cost_price_RUB')))['total_cost']
    order.total_cost = total_cost
    order.save()
