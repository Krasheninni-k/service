from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
from django.db.models import Max, Sum, F

from app.models import Goods, Orders, OrderDetail, Catalog, Sales, SaleDetail

User = get_user_model()

# При создании заказа создает объеты Goods на каждый товар заказа.
def create_goods(order, order_detail, quantity):
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

# При каждой продаже изменяет Goods: дату продажи, цену продажи, маржу, наценку, кол-во дней на складе.
def update_goods(sale_detail, quantity):
    for i in range(quantity):
        order_list = OrderDetail.objects.filter(
            product=sale_detail.product)
        good = Goods.objects.filter(
            sale_date__isnull=True, product__in=order_list).order_by(
            'order_date').select_related('received_date').last()
        good.sale_date = sale_detail.sale_date
        good.sale_price_RUB = sale_detail
        good.days_in_stock = (sale_detail.sale_date.sale_date.date() - good.received_date.received_date.date()).days
        good.margin = (float(sale_detail.sale_price_RUB) - float(good.cost_price_RUB.cost_price_RUB))
        good.markup = (float(sale_detail.sale_price_RUB)/float(good.cost_price_RUB.cost_price_RUB) - 1)*100
        good.save()


def max_value():
    result = Orders.objects.aggregate(max_value=Max('order_number'))['max_value']
    return result if result is not None else 0

def max_value_sale():
    result = Sales.objects.aggregate(max_value=Max('sale_number'))['max_value']
    return result if result is not None else 0

# При редактировании даты заказа пересчитываем поле days_in_stock в каждом товаре заказа модели Goods.
def change_order_days_in_stock(instance):
    order_detail_list = OrderDetail.objects.filter(order_number=instance)
    for i in range(len(order_detail_list)):
        goods_list = Goods.objects.filter(
            order_number=instance,
            sale_date__sale_date__isnull=False).select_related('received_date')
        for j in range(len(goods_list)):
            good = goods_list[j]
            good.days_in_stock = (good.sale_date.sale_date.date() - good.received_date.received_date.date()).days
            good.save()

# При редактировании даты покупки пересчитываем поле days_in_stock в каждом товаре покупки модели Goods.
def change_sale_days_in_stock(instance):
    sale_detail_list = SaleDetail.objects.filter(sale_date=instance)
    for i in range(len(sale_detail_list)):
        goods_list = Goods.objects.filter(
            sale_date=instance).select_related('received_date')
        for j in range(len(goods_list)):
            good = goods_list[j]
            good.days_in_stock = (good.sale_date.sale_date.date() - good.received_date.received_date.date()).days
            good.save()

# При редактировании деталей заказа меняет поле product_list в Orders, total_cost_RUB в OrderDetail.
# и поля good.margin и good.markup в Goods.
def change_order_detail_fields(instance):
    order = get_object_or_404(Orders, pk=instance.order_number.id)
    order_detail_list = OrderDetail.objects.filter(order_number=order.id)
    product_list = []
    for i in range(len(order_detail_list)):
        order_detail = order_detail_list[i]
        product = Catalog.objects.get(id=order_detail.product_id)
        product_list.append(f'{product} - {order_detail.quantity} ед.')
        order.product_list = ', '.join(str(item) for item in product_list)
        order.save()
        goods_list = Goods.objects.filter(
            order_number=order,
            sale_date__sale_date__isnull=False).select_related('received_date')
        for j in range(len(goods_list)):
            good = goods_list[j]
            good.margin = (float(good.sale_price_RUB.sale_price_RUB) - float(good.cost_price_RUB.cost_price_RUB))
            good.markup = (float(good.sale_price_RUB.sale_price_RUB)/float(good.cost_price_RUB.cost_price_RUB) - 1)*100
            good.save()
    total_cost = OrderDetail.objects.filter(
         order_number=order.id).aggregate(
         total_cost=Sum(F('quantity') * F('cost_price_RUB')))['total_cost']
    order.total_cost = total_cost
    order.save()

# При редактировании продажи меняет поля product_list в Sales и total_price в SaleDetail.
# и поля good.margin и good.markup в Goods.
def change_sale_detail_fields(instance):
    sale = get_object_or_404(Sales, pk=instance.sale_number.id)
    sale_detail_list = SaleDetail.objects.filter(sale_number=sale.id)
    product_list = []
    for i in range(len(sale_detail_list)):
        sale_detail = sale_detail_list[i]
        product = Catalog.objects.get(id=sale_detail.product_id)
        product_list.append(f'{product} - {sale_detail.quantity} ед.')
        sale.product_list = ', '.join(str(item) for item in product_list)
        sale.save()
        goods_list = Goods.objects.filter(
            sale_date=sale).select_related('received_date')
        for j in range(len(goods_list)):
            good = goods_list[j]
            good.margin = (float(good.sale_price_RUB.sale_price_RUB) - float(good.cost_price_RUB.cost_price_RUB))
            good.markup = (float(good.sale_price_RUB.sale_price_RUB)/float(good.cost_price_RUB.cost_price_RUB) - 1)*100
            good.save()
    total_price = SaleDetail.objects.filter(
         sale_number=sale.id).aggregate(
         total_price=Sum(F('quantity') * F('sale_price_RUB')))['total_price']
    sale.total_price = total_price
    sale.save()
