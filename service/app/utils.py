from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
from django.db.models import Max, Sum, F, Count

from app.models import Goods, Orders, OrderDetail, Catalog, Sales, SaleDetail, CustomSettings

User = get_user_model()

def get_markup():
    markup_obj = CustomSettings.objects.last()
    if markup_obj is not None:
        markup_dict = {
            (0, 2000): markup_obj.markup_0,
            (2000, 4000): markup_obj.markup_2,
            (4000, 8000): markup_obj.markup_4,
            (8000, 16000): markup_obj.markup_8,
            (16000, 32000): markup_obj.markup_16,
            (32000, 64000): markup_obj.markup_32,
            (64000, 128000): markup_obj.markup_64,
            (128000, float('inf')): markup_obj.markup_128,
        }
        return markup_obj, markup_dict
    else:
        default_markup_obj = None
        default_markup_dict = {(0, float('inf')): 40,}
        return default_markup_obj, default_markup_dict

# При создании заказа создает объеты Goods на каждый товар заказа.
def create_goods(order, order_detail, quantity):
    for i in range(quantity):
        good = Goods.objects.create(
            order_number=order,
            order_date=order,
            created_by=order.created_by,
            product=order_detail,
            price_RUB=order_detail.product,
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
            sale_date__isnull=True,
            received_date__received_date__isnull=False,
            product__in=order_list).order_by(
            'order_date').select_related('received_date').last()
        good.sale_date = sale_detail.sale_date
        good.sale_price_RUB = sale_detail
        good.days_in_stock = (good.sale_date.sale_date.date() - good.received_date.received_date.date()).days
        good.margin = (float(sale_detail.sale_price_RUB) - float(good.cost_price_RUB.cost_price_RUB))
        good.markup = (float(sale_detail.sale_price_RUB)/float(good.cost_price_RUB.cost_price_RUB) - 1)*100
        good.save()

# При каждой закупке изменяет Catalog: цену товара в юанях и расчетные цены от закупки и от текущего курса.
def update_catalog(order_detail):
    if order_detail == OrderDetail.objects.last():
        cost_price = float(order_detail.cost_price_RUB)
        RMB_price = float(order_detail.ordering_price_RMB)
        product = get_object_or_404(Catalog, title=order_detail.product)
        product.order_price_RMB = RMB_price
        markup_obj, markup_dict = get_markup()
        markup = None
        for i, j in markup_dict.items():
            min_price, max_price = i
            if min_price <= cost_price < max_price:
                markup = j
        product.target_last_order_price_RUB = cost_price * (1 + markup / 100)
        product.target_current_RMB_price_RUB = (
            RMB_price * (1 + float(markup_obj.delivery_cost)/100) * float(markup_obj.exchange_rate) * (1 + markup / 100))
        product.save()

# Обновление расчетной цены товара от курса при изменении курса валюты
def update_exchange_rate(rmb):
    catalog_list = Catalog.objects.all()
    markup_obj, markup_dict = get_markup()
    for catalog in catalog_list:
        RMB_price = catalog.order_price_RMB
        cost_price = float(RMB_price) * (1 + float(markup_obj.delivery_cost)/100) * float(rmb)
        markup = None
        for i, j in markup_dict.items():
            min_price, max_price = i
            if min_price <= cost_price < max_price:
                markup = j
                break
        if markup is not None:
            catalog.target_current_RMB_price_RUB = cost_price * (1 + markup / 100)
            catalog.save()

# Для подсказки в форме добавления закупки
def max_value():
    result = Orders.objects.aggregate(max_value=Max('order_number'))['max_value']
    return result if result is not None else 0

# Для подсказки в форме добавления продажи
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

def product_list_for_import(sale, sale_detail):
    sale_detail_list = SaleDetail.objects.filter(
        sale_number=sale_detail.sale_number).order_by('id')
    product_list = []
    for i in sale_detail_list:
        product_list.append(f'{i.product} - {i.quantity} ед.')
    sale.product_list = ', '.join(str(item) for item in product_list)
    sale.save()

def get_month_list(start_date, end_date):
    month_list = Sales.objects.select_related(
        'created_by', 'payment_type', 'receiving_type', 'client_type').filter(
        is_published=True, sale_date__gte=start_date, sale_date__lte=end_date)
    return(month_list)

def get_month_goods_list(start_date, end_date):
    month_goods_list = Goods.objects.filter(
        sale_date__sale_date__gte=start_date, sale_date__sale_date__lte=end_date).aggregate(
        count_goods=Count('id'),
        sum_sale=Sum('sale_price_RUB__sale_price_RUB'),
        sum_margin=Sum('margin')
        )
    return(month_goods_list)
