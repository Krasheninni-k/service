from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse, reverse_lazy
from django.utils import timezone
from django.db.models import Count
from django.views.generic import DetailView, UpdateView
from django.contrib.auth import get_user_model
from django.core.paginator import Paginator
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect
from datetime import datetime
from django.db.models import F, Sum, Q, Count, Avg, fields, Max
import pandas as pd
import calendar
from django.db.models.functions import Now, Cast, Round

from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status

from app.models import (Orders, Goods, Catalog, OrderDetail, Sales, SaleDetail, ScanSnNumber,
                         Payment_type, Client_type, Receiving_type, CustomSettings)

from app.forms import (OrderForm, OrderDetailForm, SaleForm,
                        EditDeleteOrderForm, EditOrderDetailForm,
                        CatalogForm, SaleEditDeleteForm, EditGoodDetailForm,
                        CustomSettingsForm, OrderReceivedDateForm,
                        StartEndDateForm, MonthForm, SalePriceForm)

from app.utils import (create_goods, update_goods, update_catalog, update_exchange_rate,
                       change_order_detail_fields,
                       change_order_days_in_stock, change_sale_days_in_stock,
                       product_list_for_import, get_month_list, get_month_goods_list,
                       get_count_postamat)

from app.currency import change_prices

current_time = timezone.now()
User = get_user_model()


def index(request):
    template = 'app/index.html'
    return render(request, template)


# Закупки
@login_required
def order_detail_add(request):
    number = int(request.GET.get('order_number'))
    quantity_name = int(request.GET.get('quantity'))
    order_date = request.GET.get('order_date')
    template = 'app/order_detail_add.html'
    forms = []
    product_list = []

    if request.method == 'POST':
        for i in range(quantity_name):
            form = OrderDetailForm(request.POST, prefix=f'form_{i+1}')
            forms.append(form)
        if all(form.is_valid() for form in forms):
            order = Orders.objects.create(
                order_number=number,
                created_by=request.user,
                order_date=datetime.strptime(order_date, "%Y-%m-%d"),
                quantity=quantity_name
            )
            for i in range(quantity_name):
                quantity = int(request.POST.get('form_' + str(i+1) + '-quantity'))
                product = Catalog.objects.get(
                    id=int(request.POST.get('form_' + str(i+1) + '-product')))
                order_detail = OrderDetail.objects.create(
                    order_number=Orders.objects.get(id=order.id),
                    order_date=Orders.objects.get(id=order.id),
                    received_date=Orders.objects.get(id=order.id),
                    created_by=request.user,
                    product=product,
                    quantity=quantity,
                    cost_price_RUB=request.POST.get('form_' + str(i+1) + '-cost_price_RUB'),
                    ordering_price_RMB=request.POST.get('form_' + str(i+1) + '-ordering_price_RMB')
                )
                order_detail.save()
                product_list.append(f'{product} - {quantity} ед.')
                order.product_list = ', '.join(str(item) for item in product_list)
                order.save()
                create_goods(
                    order, order_detail, quantity)
                update_catalog(order_detail)
            total_cost = OrderDetail.objects.filter(
                order_number=order.id).aggregate(
                total_cost=Sum(F('quantity') * F('cost_price_RUB')))['total_cost']
            order.total_cost = total_cost
            order.save()
            return redirect('app:orders_list')
    else:
        for i in range(quantity_name):
            form = OrderDetailForm(prefix=f'form_{i+1}')
            forms.append(form)

    context = {'forms': forms}
    return render(request, template, context)


@login_required
def order_add(request):
    template = 'app/order_add.html'
    form = OrderForm(request.POST or None)
    context = {'form': form}
    if form.is_valid():
        quantity = form.cleaned_data['quantity']
        order_date = form.cleaned_data['order_date'].date()
        order_number = form.cleaned_data['order_number']
        redirect_url = reverse(
            'app:order_detail_add') + f'?quantity={quantity}&order_date={order_date}&order_number={order_number}'
        return redirect(redirect_url)
    return render(request, template, context)


@login_required
def orders_list(request):
    template = 'app/orders_list.html'
    order_list = Orders.objects.select_related('created_by').filter(
        is_published=True)[:100]
    paginator = Paginator(order_list, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    context = {'page_obj': page_obj}
    return render(request, template, context)


@login_required
def order_detail(request, pk):
    template = 'app/order_detail.html'
    order_info = OrderDetail.objects.filter(
        is_published=True,
        order_number_id=pk).select_related('product').values(
        'order_number_id__order_number',
        'order_number_id__id',
        'received_date_id__received_date',
          'order_date_id__order_date',
          'quantity',
          'id',
          'product__id',
            'product__title',
              'cost_price_RUB',
              'ordering_price_RMB')
    context = {'order_info': order_info}
    return render(request, template, context)


@login_required
def order_delete(request, pk):
    template = 'app/order_edit_delete.html'
    instance = get_object_or_404(Orders, id=pk)
    form = EditDeleteOrderForm(instance=instance)
    context = {'form': form}
    if request.method == 'POST':
        instance.delete()
        return redirect('app:orders_list')
    return render(request, template, context)


@login_required
def order_edit(request, pk):
    template = 'app/order_edit_delete.html'
    instance = get_object_or_404(Orders, id=pk)
    if request.method == 'POST':
        form = EditDeleteOrderForm(request.POST, instance=instance)
        if form.is_valid():
            form.save()
            change_order_days_in_stock(instance)
            return redirect('app:orders_list')
    else:
        form = EditDeleteOrderForm(instance=instance)

    context = {'form': form}
    return render(request, template, context)


@login_required
def order_detail_edit(request, **kwargs):
    template = 'app/order_detail_edit.html'
    instance = get_object_or_404(OrderDetail, pk=kwargs['pk'])
    id = instance.order_number.id
    form = EditOrderDetailForm(instance=instance)
    context = {'form': form}
    if request.method == 'POST':
        form = EditOrderDetailForm(request.POST, instance=instance)
        if form.is_valid():
            form.save()
            change_order_detail_fields(instance)
            update_catalog(instance)
            return redirect('app:order_detail', pk=id)
    return render(request, template, context)


@login_required
def order_received(request, pk):
    template = 'app/order_received.html'
    goods_info = Goods.objects.select_related(
        'order_number', 'product__product','cost_price_RUB').filter(
        is_published=True, order_number__id=pk).values(
        'order_number__order_number', 'order_number__order_date',
        'product__product__title','cost_price_RUB__cost_price_RUB',
        'received_date', 'id','received', 'sn_number')
    context = {'goods_info': goods_info, 'pk': pk, 'begin': True}
    return render(request, template, context)

# Кнопка для изменения статуса конкретного товара received в блоке Приемки товара
@login_required
def order_change_received(request, pk):
    good = get_object_or_404(Goods, pk=pk)
    good.received = not good.received
    good.save()
    url = reverse('app:order_received', args=[good.order_number.id])
    return redirect(f"{url}#good-{good.id}")

# Кнопка для сброса даты приемки товара в блоке Приемки товара
@login_required
def order_reset_received_date(request, pk):
    order = get_object_or_404(Orders, pk=pk)
    goods_list = Goods.objects.filter(order_number=order)
    for good in goods_list:
        good.received_date = None
        good.save()
    return redirect(reverse('app:order_received', args=[good.order_number.id]))

# Кнопка для приемки всех товаров заказа "Принять все"
@login_required
def order_accept_all(request, pk):
    order = get_object_or_404(Orders, pk=pk)
    has_unreceived_goods = Goods.objects.filter(order_number=order, received=False).exists()
    new_status = True if has_unreceived_goods else False
    Goods.objects.filter(order_number=order).update(received=new_status)
    return redirect('app:order_received', pk=order.id)

# Ввод даты приемки товара (по-умолчанию сегодня)
@login_required
def order_received_date(request, pk):
    template = 'app/order_received_date.html'
    order = get_object_or_404(Orders, id=pk)
    form = OrderReceivedDateForm(request.POST or None)
    context = {'form': form, 'order': order}
    if form.is_valid():
        received_date = form.cleaned_data['received_date'].date()
        request.session['order_info'] = {'received_date': str(received_date)}
        return redirect(reverse('app:order_begin_scan', kwargs={'pk': pk}))
    return render(request, template, context)

# Кнопка начать сканирование для внесения заказа
@login_required
def order_begin_scan(request, pk):
    template = 'app/order_received.html'
    ScanSnNumber.objects.all().delete()
    unreceived_goods = Goods.objects.select_related(
        'order_number', 'product__product','cost_price_RUB').filter(
            order_number__id=pk, received=True, received_date__isnull=True).values(
        'order_number__order_number', 'order_number__order_date',
        'product__product__title','cost_price_RUB__cost_price_RUB',
        'received_date', 'id','received', 'sn_number')
    context = {'goods_info':  unreceived_goods, 'pk': pk, 'approve': True}
    return render(request, template, context)

@login_required
def order_end_scan(request, pk):
    order_info = request.session.get('order_info', {})
    if 'received_date' not in order_info:
        return render(request, template, {'error': 'Дата получения не найдена в сессии.'})
    received_date = datetime.strptime(order_info['received_date'], '%Y-%m-%d').date()
    print(received_date)
    template = 'app/order_received.html'
    sn_numbers = ScanSnNumber.objects.all()
    unreceived_goods = Goods.objects.filter(
            order_number__id=pk, received=True, received_date__isnull=True)
    
    for scan, good in zip(sn_numbers, unreceived_goods):
        print(scan, good)
        good.sn_number = scan.sn_number
        good.received_date = received_date
        good.save()
    ScanSnNumber.objects.all().delete()
    has_unreceived_goods = Goods.objects.filter(order_number__id=pk, received_date__isnull=True).exists()
    if not has_unreceived_goods:
        order = get_object_or_404(Orders, pk=pk)
        order.received_date = received_date
        order.save()
    goods_info = Goods.objects.select_related(
        'order_number', 'product__product', 'cost_price_RUB').filter(
        is_published=True, order_number__id=pk).values(
        'order_number__order_number', 'order_number__order_date',
        'product__product__title','cost_price_RUB__cost_price_RUB',
        'received_date', 'id','received', 'sn_number')
    context = {'goods_info': goods_info, 'pk': pk, 'finished': True}
    return render(request, template, context)

# Каталог
@login_required
def catalog(request):
    change_prices()
    exchange_rate = CustomSettings.objects.last().exchange_rate
    template = 'app/catalog.html'
    catalog = Catalog.objects.select_related('created_by').filter(
        is_published=True).annotate(
        count_stock=Count('order_detail__goods',
                      filter=(Q(order_detail__goods__received_date__isnull=False) &
                             Q(order_detail__goods__sale_date__sale_date__isnull=True))),
        count_wait=Count('order_detail__goods',
                      filter=Q(order_detail__goods__received_date__isnull=True))).order_by('title')[:100]
    paginator = Paginator(catalog, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    count_product = Catalog.objects.select_related('created_by').filter(
        is_published=True).count
    context = {'page_obj': page_obj, 'count_product': count_product, 'exchange_rate': exchange_rate}

    if request.method == 'GET':
        query = request.GET.get('q', '')
        print(query)
        if query:
            results = Catalog.objects.filter(title__icontains=query).annotate(
        count_stock=Count('order_detail__goods',
                      filter=(Q(order_detail__goods__received_date__isnull=False) &
                             Q(order_detail__goods__sale_date__sale_date__isnull=True))),
        count_wait=Count('order_detail__goods',
                      filter=Q(order_detail__goods__received_date__isnull=True))).order_by('title')
            context['results'] = results
            context['query'] = query
        return render(request, template, context)
    return render(request, template, context)


@login_required
def catalog_add(request):
    template = 'app/catalog_add.html'
    form = CatalogForm(request.POST or None,
                       files=request.FILES or None)
    context = {'form': form}
    if form.is_valid():
        product = form.save(commit=False)
        product.created_by = request.user
        product.save()
        return redirect('app:catalog')
    return render(request, template, context)


@login_required
def catalog_detail(request, pk):
    change_prices()
    exchange_rate = CustomSettings.objects.last().exchange_rate
    template = 'app/catalog_detail.html'
    product = get_object_or_404(Catalog, pk=pk)
    product_count_stock = Goods.objects.filter(
        Q(received_date__isnull=False),
          Q(sale_date__sale_date__isnull=True),
            product__product=pk).values('id').count()
    product_count_wait = Goods.objects.filter(
        Q(received_date__isnull=True), product__product=pk).values('id').count()
    order_list = OrderDetail.objects.filter(
        product=pk).values('order_number__order_number',
                           'order_date__order_date',
                           'received_date__received_date',
                           'quantity', 'cost_price_RUB', 'ordering_price_RMB').order_by('order_number')[:20]
    sale_list = Goods.objects.filter(
        product__product=pk, sale_date__sale_date__isnull=False).values(
        'margin',
        'markup',
        'days_in_stock',
        'received_date',
        'sale_price',
        'cost_price_RUB__cost_price_RUB',
        'sale_date__sale_date').order_by('sale_date')
    paginator = Paginator(sale_list, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    context = {'product': product, 'page_obj': page_obj, 'order_list': order_list,
               'product_count_stock': product_count_stock,
               'product_count_wait': product_count_wait,
               'exchange_rate': exchange_rate}
    return render(request, template, context)


@login_required
def catalog_edit(request, pk):
    template = 'app/catalog_edit_delete.html'
    instance = get_object_or_404(Catalog, pk=pk)
    if request.method == 'POST':
        form = CatalogForm(request.POST, instance=instance, files=request.FILES or None)
        if form.is_valid():
            form.save()
            return redirect('app:catalog')
    else:
        form = CatalogForm(instance=instance)
    context = {'form': form}
    return render(request, template, context)

@login_required
def catalog_delete(request, pk):
    template = 'app/catalog_edit_delete.html'
    instance = get_object_or_404(Catalog, pk=pk)
    context = {'instance': instance}
    if request.method == 'POST':
        instance.delete()
        return redirect('app:catalog')
    return render(request, template, context)

# Остатки
@login_required
def stock_list(request):
    template = 'app/stock_list.html'
    stock_list = Catalog.objects.filter(
    order_detail__goods__isnull=False).annotate(
    count_stock=Count('order_detail__goods',
                      filter=(Q(order_detail__goods__received_date__isnull=False) &
                            Q(order_detail__goods__sale_date__sale_date__isnull=True))),
    count_wait=Count('order_detail__goods',
                      filter=Q(order_detail__goods__received_date__isnull=True)),
    cost_stock=Sum('order_detail__goods__cost_price_RUB__cost_price_RUB',
                 filter=(Q(order_detail__goods__received_date__isnull=False) &
                            Q(order_detail__goods__sale_date__sale_date__isnull=True))),
    cost_wait=Sum('order_detail__goods__cost_price_RUB__cost_price_RUB',
                 filter=Q(order_detail__goods__received_date__isnull=True)),
    price_stock=Sum('price_RUB',
                 filter=(Q(order_detail__goods__received_date__isnull=False) &
                            Q(order_detail__goods__sale_date__sale_date__isnull=True))),
    price_wait=Sum('price_RUB',
                 filter=Q(order_detail__goods__received_date__isnull=True))).order_by('title')
    total_count_stock = Goods.objects.filter(
        Q(received_date__isnull=False) &
        Q(sale_date__sale_date__isnull=True)).values('id').count()
    total_count_wait = Goods.objects.filter(
        Q(received_date__isnull=True)).values('id').count()
    total_list = Goods.objects.filter(
        is_published=True).annotate(
        cost_stock=Sum('cost_price_RUB__cost_price_RUB', filter=(
            Q(received_date__isnull=False) &
            Q(sale_date__sale_date__isnull=True))),
        cost_wait=Sum('cost_price_RUB__cost_price_RUB', filter=(
            Q(received_date__isnull=True))),
        price_stock=Sum('price_RUB__price_RUB', filter=(
            Q(received_date__isnull=False) &
            Q(sale_date__sale_date__isnull=True))),
        price_wait=Sum('price_RUB__price_RUB', filter=(
            Q(received_date__isnull=True)))
        )
    total_cost_stock = sum(item.cost_stock if item.cost_stock is not None else 0 for item in total_list)
    total_cost_wait = sum(item.cost_wait if item.cost_wait is not None else 0 for item in total_list)
    total_price_stock = sum(item.price_stock if item.price_stock is not None else 0 for item in total_list)
    total_price_wait = sum(item.price_wait if item.price_wait is not None else 0 for item in total_list)
    context = {'stock_list': stock_list,
               'total_count_stock': total_count_stock,
               'total_cost_stock': total_cost_stock,
               'total_price_stock': total_price_stock,
               'total_count_wait': total_count_wait,
               'total_cost_wait': total_cost_wait,
               'total_price_wait': total_price_wait}
    return render(request, template, context)


#  Продажи
@login_required
def sale_detail_add(request):
    template = 'app/sale_detail_add.html'
    goods_list = Goods.objects.filter(
        is_published=True, sold=True, sale_date__sale_date__isnull=True)
    # Сбросим лишние True, по которым нет даты продажи (кроме перехода с корзины)
    add_more = request.GET.get('add_more', 'False')
    if add_more != 'True':
        goods_list.update(sold=False)
    context = {'begin': True}
    return render(request, template, context)


@login_required
def sale_add(request):
    template = 'app/sale_add.html'
    form = SaleForm(request.POST or None)
    context = {'form': form}
    if form.is_valid():
        sale_number = form.cleaned_data['sale_number']
        sale_date = form.cleaned_data['sale_date'].strftime('%Y-%m-%d')
        payment_type = form.cleaned_data['payment_type'].id
        client_type = form.cleaned_data['client_type'].id
        receiving_type = form.cleaned_data['receiving_type'].id
        client_name = form.cleaned_data['client_name']
        client_contact = form.cleaned_data['client_contact']
        comment = form.cleaned_data['comment']
        regular_client = form.cleaned_data['regular_client']
        sale_info = {
            'sale_number': sale_number,
            'sale_date': sale_date,
            'payment_type': payment_type,
            'client_type': client_type,
            'receiving_type': receiving_type,
            'client_name': client_name,
            'client_contact': client_contact,
            'comment': comment,
            'regular_client': regular_client}
        request.session['sale_info'] = sale_info
        return HttpResponseRedirect(reverse('app:sale_detail_add'))
    return render(request, template, context)


@login_required
def sales_list(request):
    template = 'app/sales_list.html'
    sales_list = Sales.objects.select_related(
        'created_by', 'payment_type', 'receiving_type', 'client_type').filter(
        is_published=True)
    paginator = Paginator(sales_list, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    current_date = datetime.now()
    month = current_date.month
    year = current_date.year
    _, last_day = calendar.monthrange(year, month)
    start_date = datetime(year, month, 1).date()
    end_date = datetime(year, month, last_day).date()

    sum_cash = sales_list.filter(cash=False).aggregate(sum_cash=Sum('total_price'))

    month_list = sales_list.filter(
       sale_date__gte=start_date, sale_date__lte=end_date)
    count_sales = month_list.values('id').count()
    count_postamat = get_count_postamat(month_list)
    goods_list = get_month_goods_list(start_date, end_date)
    start_end_date_form = StartEndDateForm(request.POST or None)
    context = {'page_obj': page_obj,
               'goods_list': goods_list,
               'sum_cash': sum_cash,
               'current_date': current_date,
               'count_sales': count_sales,
               'count_postamat': count_postamat,
               'start_end_date_form': start_end_date_form
               }
    if request.method == 'POST':
        if start_end_date_form.is_valid():
            start_date = start_end_date_form.cleaned_data['start_date']
            end_date = start_end_date_form.cleaned_data['end_date']
            month_list = get_month_list(start_date, end_date)
            count_postamat = get_count_postamat(month_list)
            goods_list = get_month_goods_list(start_date, end_date)
            context['month_list'] = month_list
            context['goods_list'] = goods_list
            context['count_postamat'] = count_postamat
    if goods_list['count_goods'] > 0:
        total_margin = goods_list['sum_margin'] / goods_list['sum_sale']*100
        total_markup = (goods_list['sum_sale'] / (goods_list['sum_sale'] - goods_list['sum_margin']) - 1) *100
        context['total_margin'] = total_margin
        context['total_markup'] = total_markup
    return render(request, template, context)

@login_required
def sale_detail(request, pk):
    template = 'app/sale_detail.html'
    sale_info_detail = SaleDetail.objects.filter(
        is_published=True,
        sale_number_id__sale_number=pk).select_related('product').values(
        'sale_number_id__sale_number',
        'sale_date_id__sale_date',
        'quantity',
        'id',
        'product',
        'product__title',
        'sale_price_RUB')
    sale_info = get_object_or_404(Sales, sale_number=pk)
    context = {'sale_info': sale_info, 'sale_info_detail': sale_info_detail}
    return render(request, template, context)


@login_required
def sale_delete(request, pk):
    template = 'app/sale_edit_delete.html'
    sale = get_object_or_404(Sales, sale_number=pk)
    form = SaleEditDeleteForm(instance=sale)
    context = {'form': form}
    if request.method == 'POST':
        good_list = Goods.objects.filter(sale_date=sale)
        good_list.update(sold=False, sale_price=None)
        sale.delete()
        return redirect('app:sales_list')
    return render(request, template, context)


@login_required
def sale_edit(request, pk):
    template = 'app/sale_edit_delete.html'
    instance = get_object_or_404(Sales, sale_number=pk)
    if request.method == 'POST':
        form = SaleEditDeleteForm(request.POST, instance=instance)
        if form.is_valid():
            form.save()
            change_sale_days_in_stock(instance)
            return redirect('app:sales_list')
    else:
        form = SaleEditDeleteForm(instance=instance)

    context = {'form': form}
    return render(request, template, context)

@login_required
def sale_detail_edit(request, pk):
    template = 'app/sale_busket.html'

    goods_list = Goods.objects.select_related(
        'order_number',
        'product', 'sale_date').filter(is_published=True, sale_date__sale_number=pk)
    print(goods_list)
    context = {'goods_list': goods_list}

    forms = []
    product_list = []

    if request.method == 'POST':
        for i, good in enumerate(goods_list):
            form = SalePriceForm(request.POST, prefix=f'form_{i+1}', instance=good)
            forms.append(form)
        if all(form.is_valid() for form in forms):
            for form in forms:
                form.save()
            # Получаем объект sale и редактируем его поля
            sale = get_object_or_404(Sales, sale_number=pk)

            product_summary = goods_list.values('product__product__id').annotate(
                quantity=Count('id'),
                average_price=Avg('sale_price'))

            for product in product_summary:
                sale_price_RUB = product['average_price']
                quantity = product['quantity']
                product = Catalog.objects.get(id=int(product['product__product__id']))
                # Получаем объект sale_detail и редактируем все его поля 
                sale_detail = get_object_or_404(SaleDetail, product=product, sale_number=sale)
                print(sale_detail.sale_date)
                sale_detail.product = product
                sale_detail.quantity = quantity
                sale_detail.sale_price_RUB = sale_price_RUB
                sale_detail.save()
                product_list.append(f'{product} - {quantity} ед.')
                sale.product_list = ', '.join(
                    str(item) for item in product_list)
                sale.save()
                update_goods(goods_list, sale)
            total_price = SaleDetail.objects.filter(
                sale_number=sale.id).aggregate(
                total_price=Sum(
                    F('quantity') * F('sale_price_RUB')))['total_price']
            sale.total_price = total_price
            sale.save()
            return redirect('app:sales_list')
    else:
        for i, good in enumerate(goods_list):
            form = SalePriceForm(instance=good, prefix=f'form_{i+1}')
            forms.append((good, form))

    context = {'forms': forms}
    return render(request, template, context)

@login_required
def sale_change_cash(request, pk):
    sale = get_object_or_404(Sales, pk=pk)
    sale.cash = not sale.cash
    sale.save()
    return redirect('app:sales_list')


# Кнопка начать сканирование для внесения продажи
@login_required
def sale_begin_scan(request):
    template = 'app/sale_detail_add.html'
    ScanSnNumber.objects.all().delete()
    context = {'approve': True}
    return render(request, template, context)


# Кнопка завершения сканирование для внесения продажи
@login_required
def sale_end_scan(request):
    template = 'app/sale_detail_add.html'
    sn_numbers = ScanSnNumber.objects.all()
    sn_number_values = list(sn_numbers.values_list('sn_number', flat=True))
    sale_info = Goods.objects.select_related(
        'order_number', 'product__product', 'cost_price_RUB').filter(sn_number__in=sn_number_values)
    sale_info.update(sold=True)
    sale_info = sale_info.values(
        'order_number__order_number', 'order_number__order_date',
        'product__product__title', 'cost_price_RUB__cost_price_RUB',
        'received_date', 'id', 'received', 'sn_number', 'sold', 'sale_date__sale_date')
    ScanSnNumber.objects.all().delete()
    context = {'sale_info': sale_info, 'finished': True}
    return render(request, template, context)

# Ручной выбор товара по поисковой строке
@login_required
def select_good(request):
    template = 'app/sale_detail_add.html'
    if request.method == 'GET':
        query = request.GET.get('q', '')
        if query:
            results = Catalog.objects.filter(title__icontains=query)
            context = {'results': results, 'query': query}
        return render(request, template, context)
    return render(request, template, context)

# Переход к списку товаров в наличии при ручном выборе товара
@login_required
def selected_good_stock(request, pk):
    template = 'app/sale_detail_add.html'
    goods_list = Goods.objects.select_related(
        'order_number',
        'product', 'sale_date').filter(
        is_published=True, received_date__isnull=False, product__product__id=pk, sale_date__sale_date__isnull=True).values(
        'order_number__order_number', 'order_number__order_date',
        'received_date', 'cost_price_RUB__cost_price_RUB',
        'product__product__title', 'sn_number', 'sale_date__sale_date',
        'id', 'sold')
    context = {'goods_list': goods_list, 'selected': True}
    return render(request, template, context)

# Кнопка для изменения статуса конкретного товара sold в блоке Продажи товара
@login_required
def sale_change_sold(request, pk):
    good = get_object_or_404(Goods, pk=pk)
    good.sold = not good.sold
    good.save()
    url = reverse('app:selected_good_stock', args=[good.product.product.id])
    return redirect(url)


# Переход к списку товаров в наличии при ручном выборе товара
@login_required
def sale_busket(request):
    template = 'app/sale_busket.html'
    goods_list = Goods.objects.select_related(
        'order_number',
        'product', 'sale_date'
    ).filter(is_published=True, sold=True, sale_date__sale_date__isnull=True)
    quantity_name = goods_list.values('product').distinct().count()

    forms = []
    product_list = []

    if request.method == 'POST':
        for i, good in enumerate(goods_list):
            form = SalePriceForm(request.POST, prefix=f'form_{i+1}', instance=good)
            forms.append(form)
        if all(form.is_valid() for form in forms):
            for form in forms:
                form.save()
            sale_info = request.session.get('sale_info', {})
            # Создаем объект sale и заполнем все его поля
            sale = Sales.objects.create(
                sale_number=sale_info.get('sale_number'),
                created_by=request.user,
                sale_date=datetime.strptime(sale_info.get('sale_date'), '%Y-%m-%d'),
                quantity=quantity_name,
                payment_type=Payment_type.objects.get(
                    id=int(sale_info.get('payment_type'))),
                client_type=Client_type.objects.get(
                    id=int(sale_info.get('client_type'))),
                receiving_type=Receiving_type.objects.get(
                    id=int(sale_info.get('receiving_type'))),
                client_name=sale_info.get('client_name'),
                client_contact=sale_info.get('client_contact'),
                regular_client=sale_info.get('regular_client')
            )
            comment = sale_info.get('comment') 
            if comment != "None":
                sale.comment = comment
            if (sale.payment_type == Payment_type.objects.get(title='Наличные') or
                sale.payment_type == Payment_type.objects.get(title='Перевод')):
                sale.cash = False

            product_summary = goods_list.values('product__product__id').annotate(
                quantity=Count('id'),
                average_price=Avg('sale_price'))

            for product in product_summary:
                sale_price_RUB = product['average_price']
                quantity = product['quantity']
                product = Catalog.objects.get(id=int(product['product__product__id']))
                # Создаем объект sale_detail и заполнем все его поля  
                sale_detail = SaleDetail.objects.create(
                    sale_number=Sales.objects.get(id=sale.id),
                    sale_date=Sales.objects.get(id=sale.id),
                    created_by=request.user,
                    product=product,
                    quantity=quantity,
                    sale_price_RUB=sale_price_RUB)
                product_list.append(f'{product} - {quantity} ед.')
                sale.product_list = ', '.join(
                    str(item) for item in product_list)
                sale.save()
            total_price = SaleDetail.objects.filter(
                sale_number=sale.id).aggregate(
                total_price=Sum(
                    F('quantity') * F('sale_price_RUB')))['total_price']
            sale.total_price = total_price
            sale.save()
            update_goods(goods_list, sale)
            return redirect('app:sales_list')
    else:
        for i, good in enumerate(goods_list):
            form = SalePriceForm(prefix=f'form_{i+1}', instance=good)
            forms.append((good, form))

    context = {'forms': forms, 'busket': True}
    return render(request, template, context)

# Список товаров.
@login_required
def goods_list(request):
    template = 'app/goods_list.html'
    context = {}
    if request.method == 'GET':
        query = request.GET.get('q', '')
        if query:
            results = Catalog.objects.filter(title__icontains=query)
            context = {'results': results, 'query': query}
        return render(request, template, context)
    return render(request, template, context)

# Переход к списку товаров при выборе товара на вкладке Товары (ВСЕ)
@login_required
def selected_good(request, pk):
    in_stock = request.GET.get('in_stock')

    template = 'app/goods_list.html'
    goods_list = Goods.objects.select_related(
        'order_number',
        'product', 'sale_date').filter(
        is_published=True, product__product__id=pk).values(
        'order_number__order_number', 'order_number__order_date',
        'received_date', 'cost_price_RUB__cost_price_RUB',
        'product__product__title', 'sn_number', 'sale_date__sale_date',
        'id', 'sold', 'product__product')
    if in_stock == 'stock':
        goods_list = goods_list.filter(sale_date__isnull=True, received_date__isnull=False)
    if in_stock == 'wait':
        goods_list = goods_list.filter(sale_date__isnull=True, received_date__isnull=True)    
    context = {'goods_list': goods_list, 'selected': True, 'pk': pk}
    return render(request, template, context)


# Список бракованных товаров
@login_required
def defect_goods(request):
    template = 'app/goods_problems.html'
    goods_list = Goods.objects.select_related(
        'order_number',
        'product', 'sale_date').filter(
        defect=True).values(
        'order_number__order_number', 'order_number__order_date',
        'received_date', 'cost_price_RUB__cost_price_RUB', 'product__product',
        'product__product__title', 'sn_number', 'sale_date__sale_date',
        'id', 'sold', 'defect', 'comment', 'days_in_stock')
    context = {'goods_list': goods_list, 'defect': True}
    return render(request, template, context)


# Список проблемных товаров (долгоо не продаются)
@login_required
def problem_goods(request):
    template = 'app/goods_problems.html'
    in_stock = request.GET.get('in_stock')
    goods_list = Goods.objects.filter(sale_date__isnull=True, received_date__isnull=False)
    goods_list.update(
        days_in_stock=Cast(
            Round(
                (Now() - F('received_date')) / (60 * 60 * 24 * 10**6), 
                0 
            ),
            output_field=fields.IntegerField()
        )
    )
    goods_list = goods_list.order_by('-days_in_stock').values(
        'order_number__order_number', 'order_number__order_date',
        'received_date', 'cost_price_RUB__cost_price_RUB', 'product__product',
        'product__product__title', 'sn_number', 'sale_date__sale_date',
        'product__product__price_RUB', 'id', 'defect', 'comment', 'days_in_stock')

    # Рассчитаем количество проблемных товаров по 4 категориям:
    over_365 = goods_list.filter(days_in_stock__gt=365)
    between_180_and_365 = goods_list.filter(days_in_stock__gt=180, days_in_stock__lte=365)
    between_60_and_180 = goods_list.filter(days_in_stock__gt=60, days_in_stock__lte=180)
    under_60 = goods_list.filter(days_in_stock__lte=60)

    all_stats = goods_list.aggregate(
        count=Count('id'),
        total_cost=Sum('cost_price_RUB__cost_price_RUB')
    )
    over_365_stats = over_365.aggregate(
        count=Count('id'),
        total_cost=Sum('cost_price_RUB__cost_price_RUB')
    )
    between_180_and_365_stats = between_180_and_365.aggregate(
        count=Count('id'),
        total_cost=Sum('cost_price_RUB__cost_price_RUB')
    )
    between_60_and_180_stats = between_60_and_180.aggregate(
        count=Count('id'),
        total_cost=Sum('cost_price_RUB__cost_price_RUB')
    )
    under_60_stats = under_60.aggregate(
        count=Count('id'),
        total_cost=Sum('cost_price_RUB__cost_price_RUB')
    )
    if all_stats['total_cost'] > 0:
        over_365_percent = round((over_365_stats['total_cost'] / all_stats['total_cost'] * 100), 1)
        between_180_and_365_percent = round((between_180_and_365_stats['total_cost'] / all_stats['total_cost'] * 100), 1)
        between_60_and_180_percent = round((between_60_and_180_stats['total_cost'] / all_stats['total_cost'] * 100), 1)
        under_60_percent = round((under_60_stats['total_cost'] / all_stats['total_cost'] * 100), 1)
    result = {
        'all': {
            'count': all_stats['count'],
            'total_cost': round(all_stats['total_cost'], 0) or 0
        },
        'over_365': {
            'count': over_365_stats['count'],
            'total_cost': round(over_365_stats['total_cost'], 0) or 0,
            'percent': over_365_percent
        },
        'between_180_and_365': {
            'count': between_180_and_365_stats['count'],
            'total_cost': round(between_180_and_365_stats['total_cost'], 0) or 0,
            'percent': between_180_and_365_percent
        },
        'between_60_and_180': {
            'count': between_60_and_180_stats['count'],
            'total_cost': round(between_60_and_180_stats['total_cost'], 0) or 0,
            'percent': between_60_and_180_percent
        },
        'under_60': {
            'count': under_60_stats['count'],
            'total_cost': round(under_60_stats['total_cost'], 0) or 0,
            'percent': under_60_percent
        }
    }
    context = {'goods_list': goods_list, 'result': result}

    # Добавляем 4 новых выборки при нажатии 4 кнопок: 365/180/60/0
    if in_stock == '365':
        detail = over_365.values('product__product__title', 'product__product__id').annotate(
            product_count=Count('id'),
            max_days_in_stock=Max('days_in_stock'),
            total_cost=Sum('cost_price_RUB__cost_price_RUB')
            ).order_by('-total_cost')
        context['detail'] = detail
    elif in_stock == '180':
        detail = between_180_and_365.values('product__product__title', 'product__product__id').annotate(
            product_count=Count('id'),
            max_days_in_stock=Max('days_in_stock'),
            total_cost=Sum('cost_price_RUB__cost_price_RUB')
            ).order_by('-total_cost')
        context['detail'] = detail
    elif in_stock == '60':
        detail = between_60_and_180.values('product__product__title', 'product__product__id').annotate(
            product_count=Count('id'),
            max_days_in_stock=Max('days_in_stock'),
            total_cost=Sum('cost_price_RUB__cost_price_RUB')
            ).order_by('-total_cost')
        context['detail'] = detail
    elif in_stock == '0':
        detail = under_60.values('product__product__title', 'product__product__id').annotate(
            product_count=Count('id'),
            max_days_in_stock=Max('days_in_stock'),
            total_cost=Sum('cost_price_RUB__cost_price_RUB')
            ).order_by('-total_cost')
        context['detail'] = detail
    return render(request, template, context)

# Редакировать товар (sn номер, брак, комментарий)
@login_required
def good_detail_edit(request, pk):
    template = 'app/good_detail_edit.html'
    instance = get_object_or_404(Goods, pk=pk)
    form = EditGoodDetailForm(instance=instance)
    context = {'form': form}
    if request.method == 'POST':
        form = EditGoodDetailForm(request.POST, instance=instance)
        if form.is_valid():
            form.save()
            return redirect('app:selected_good', pk=instance.product.product.id)
    return render(request, template, context)

# Профили
class UserDetailView(DetailView):
    model = get_user_model()
    template_name = 'app/profile.html'
    slug_field = 'username'
    slug_url_kwarg = 'username'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['profile'] = self.get_object()
        context['username'] = self.request.user.username
        settings = CustomSettings.objects.first()
        context['settings'] = settings
        return context


class UserUpdateView(UpdateView):
    model = get_user_model()
    fields = 'first_name', 'last_name', 'email'
    success_url = reverse_lazy('app:index')
    slug_field = 'username'
    slug_url_kwarg = 'username'
    template_name = 'app/user.html'

    def dispatch(self, request, *args, **kwargs):
        instance = get_object_or_404(get_user_model(), username=request.user)
        if instance.username != request.user.username:
            return redirect('login')
        return super().dispatch(request, *args, **kwargs)

    def get_success_url(self):
        return reverse('profile',
                       kwargs={'username': self.request.user.username})

# Вносит изменения настроек: курс валюты, издержки доставки, нормы наценки
@login_required
def settings_edit(request):
    template = 'app/settings_edit.html'
    settings = CustomSettings.objects.get_or_create(pk=1)[0]
    form = CustomSettingsForm(request.POST or None, instance=settings)
    if request.method == 'POST':
        if form.is_valid():
            form.save()
            update_exchange_rate(settings.exchange_rate)
            return redirect('profile', username=request.user.username)
    context = {'form': form}
    return render(request, template, context)

# Импорт закупок
def import_orders_data(request):
    template = 'app/import_orders_data.html'
    count = 0
    if request.method == 'POST':
        excel_file = request.FILES['file']
        decoded_file = excel_file.read()

        df1 = pd.read_excel(decoded_file, sheet_name=0)
        for _, row in df1.iterrows():
            product_list = []
            order_number = int(row['order_number'])
            order_date = row['order_date'].to_pydatetime()
            quantity_name = int(row['quantity'])
            received_date = row['received_date']
            if not pd.isna(row['received_date']):
                received_date = row['received_date'].to_pydatetime()
            else:
                received_date = None
            created_by = request.user
            order = Orders(
                order_number=order_number,
                order_date=order_date,
                quantity=quantity_name,
                received_date=received_date,
                created_by=created_by,
                is_published=True)
            order.save()

            df2 = pd.read_excel(decoded_file, sheet_name=1)
            for _, row in df2.iloc[count:count+quantity_name].iterrows():
                created_by=User.objects.get(username=request.user.username)
                quantity=int(row[0])
                product = Catalog.objects.get(title=row[1])
                cost_price_RUB=float(row[2])
                ordering_price_RMB=float(row[3])
                order_detail = OrderDetail(
                    order_number=order,
                    order_date=order,
                    received_date=order,
                    created_by=created_by,
                    product=product,
                    quantity=quantity,
                    cost_price_RUB=cost_price_RUB,
                    ordering_price_RMB=ordering_price_RMB
                    )
                order_detail.save()
                product_list.append(f'{product} - {quantity} ед.')
                order.product_list = ', '.join(str(item) for item in product_list)
                order.save()
                create_goods(
                    order, order_detail, quantity)
                update_catalog(order_detail)
            count = count + quantity_name
            total_cost = OrderDetail.objects.filter(
                order_number=order.id).aggregate(
                total_cost=Sum(F('quantity') * F('cost_price_RUB')))['total_cost']
            order.total_cost = total_cost
            order.save()
        return render(request, 'app/import_success.html')

    return render(request, template)

# Импорт продаж
def import_sales_data(request):
    template = 'app/import_sales_data.html'
    previous_client_name = None
    previous_product = None
    if request.method == 'POST':
        excel_file = request.FILES['file']
        decoded_file = excel_file.read()

        df1 = pd.read_excel(decoded_file, sheet_name=0)
        for _, row in df1.iterrows():
            last_sale = Sales.objects.select_related(
                'created_by',
                'payment_type',
                'client_type',
                'receiving_type').order_by('id').last()
            if last_sale is None:
                sale_number = 1
            else:
                sale_number = last_sale.sale_number + 1
            sale_date = row['sale_date'].to_pydatetime()
            created_by = request.user
            payment_type = Payment_type.objects.get(title=row['payment_type'])
            client_type = Client_type.objects.get(title=row['client_type'])
            receiving_type = Receiving_type.objects.get(title=row['receiving_type'])
            client_name = row['client_name']
            client_contact = row['client_contact']
            product = Catalog.objects.get(title=row['product'])
            sale_price_RUB = int(row['sale_price_RUB'])
            if client_name == previous_client_name:
                if product == previous_product:
                    previous_sale = Sales.objects.order_by('id').last()
                    previous_sale_detail = SaleDetail.objects.order_by('id').last()
                    previous_sale_detail.quantity += 1
                    previous_sale_detail.save()
                    previous_sale.total_price += previous_sale_detail.sale_price_RUB
                    product_list_for_import(previous_sale, previous_sale_detail)
                    update_goods(previous_sale_detail, 1)
                    previous_client_name = client_name
                    previous_product = product
                else:
                    previous_sale = Sales.objects.order_by('id').last()
                    previous_sale.quantity += 1
                    sale_detail = SaleDetail(
                        sale_number=previous_sale,
                        sale_date=previous_sale,
                        created_by=created_by,
                        product=product,
                        sale_price_RUB=sale_price_RUB
                        )
                    sale_detail.save()
                    previous_sale.total_price += sale_detail.sale_price_RUB
                    product_list_for_import(previous_sale, sale_detail)
                    update_goods(sale_detail, 1)
                    previous_client_name = client_name
                    previous_product = product
            else:
                sale = Sales(
                    sale_number=sale_number,
                    sale_date=sale_date,
                    quantity=1,
                    created_by=created_by,
                    payment_type=payment_type,
                    client_type=client_type,
                    receiving_type=receiving_type,
                    client_name=client_name,
                    client_contact=client_contact
                    )
                sale.save()
                sale_detail = SaleDetail(
                    sale_number=sale,
                    sale_date=sale,
                    created_by=created_by,
                    product=product,
                    sale_price_RUB=sale_price_RUB
                    )
                sale_detail.save()
                sale.total_price = sale_detail.sale_price_RUB
                product_list_for_import(sale, sale_detail)
                update_goods(sale_detail, 1)
                previous_client_name = client_name
                previous_product = product

        return render(request, 'app/import_success.html')

    return render(request, template)

# Импорт каталога
def import_catalog_data(request):
    template = 'app/import_catalog_data.html'
    created_by = request.user
    if request.method == 'POST':
        excel_file = request.FILES['file']
        decoded_file = excel_file.read()
        df1 = pd.read_excel(decoded_file, sheet_name=0)
        for _, row in df1.iterrows():
            title = row['title']
            price_RUB = row['price_RUB']
            instance = Catalog(
                title=title,
                price_RUB=price_RUB,
                created_by=created_by)
            instance.save()
        df2 = pd.read_excel(decoded_file, sheet_name=1)
        for _, row in df2.iterrows():
            title = row['title']
            instance = Client_type(
                title=title,
                created_by=created_by)
            instance.save()
        df3 = pd.read_excel(decoded_file, sheet_name=2)
        for _, row in df3.iterrows():
            title = row['title']
            instance = Payment_type(
                title=title,
                created_by=created_by)
            instance.save()
        df4 = pd.read_excel(decoded_file, sheet_name=3)
        for _, row in df4.iterrows():
            title = row['title']
            instance = Receiving_type(
                title=title,
                created_by=created_by)
            instance.save()

        return render(request, 'app/import_success.html')

    return render(request, template)

# Дашборд (в разработке)
@login_required
def dashboard(request):
    template = 'app/dashboard.html'
    month_form = MonthForm(request.POST or None)
    context = {'month_form': month_form}
    if request.method == 'POST':
        if month_form.is_valid():
            month = datetime.fromisoformat(month_form.cleaned_data['month'])
            #sales_list = Sales.objects.filter(sale_date__month=month)
            #context['sales_list'] = sales_list
            count_sales = Sales.objects.filter(
                sale_date__month=month.month, sale_date__year=month.year).count()
            context['count_sales'] = count_sales
    return render(request, template, context)

# Обработка api-запроса от сканера штрих-кодов
class ScanAPIView(APIView):
    def post(self, request, *args, **kwargs):
        code = request.data.get('code')
        if not code:
            return Response({'error': 'No code provided'}, status=status.HTTP_400_BAD_REQUEST)
        sn_number = ScanSnNumber.objects.create(sn_number=code)
        return Response({'message': 'done', 'sn_number': sn_number.sn_number}, status=status.HTTP_200_OK)