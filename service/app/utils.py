from django.contrib.auth import get_user_model
from django.db.models import Max

from app.models import Goods, Orders

User = get_user_model()


def create_goods(
        order, product, cost_price_RUB, quantity):
    for i in range(quantity):
        good = Goods.objects.create(
            order_number=order,
            order_date=order,
            created_by=order.created_by,
            product=product,
            cost_price_RUB=cost_price_RUB,
            received_date=order
            )
        good.save()


def max_value():
    result = Orders.objects.aggregate(max_value=Max('order_number'))['max_value']
    return result if result is not None else 0
