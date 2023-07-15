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
from django.db.models import F, Sum, Q
import csv
import pandas as pd

from app.models import (Orders, Goods, Catalog, OrderDetail, Sales, SaleDetail,
                         Payment_type, Client_type, Receiving_type, CustomSettings)

from app.forms import (OrderForm, OrderDetailForm, SaleForm, SaleDetailForm,
                        ReceivedForm, EditDeleteOrderForm, EditOrderDetailForm,
                        CatalogForm, SaleEditDeleteForm, SaleEditDetailForm,
                        CustomSettingsForm, FilterProductForm)

from app.utils import (create_goods, update_goods, update_catalog, update_exchange_rate,
                       change_order_detail_fields, change_sale_detail_fields,
                       change_order_days_in_stock, change_sale_days_in_stock,
                       product_list_for_import)

current_time = timezone.now()
User = get_user_model()


def index(request):
    template = 'app/index.html'
    return render(request, template)


# Закупки
@login_required
def add_order_detail(request):
    number = int(request.GET.get('order_number'))
    quantity_name = int(request.GET.get('quantity'))
    order_date = request.GET.get('order_date')
    template = 'app/add_order_detail.html'
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
def add_order(request):
    template = 'app/add_order.html'
    form = OrderForm(request.POST or None)
    context = {'form': form}
    if form.is_valid():
        quantity = form.cleaned_data['quantity']
        order_date = form.cleaned_data['order_date'].date()
        order_number = form.cleaned_data['order_number']
        redirect_url = reverse(
            'app:add_order_detail') + f'?quantity={quantity}&order_date={order_date}&order_number={order_number}'
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
        order_number_id__order_number=pk).select_related('product').values(
        'order_number_id__order_number',
        'received_date_id__received_date',
          'order_date_id__order_date',
          'quantity',
          'id',
            'product__title',
              'cost_price_RUB',
              'ordering_price_RMB')
    context = {'order_info': order_info}
    return render(request, template, context)


@login_required
def delete_order(request, pk):
    template = 'app/edit_delete_order.html'
    instance = get_object_or_404(Orders, order_number=pk)
    form = EditDeleteOrderForm(instance=instance)
    context = {'form': form}
    if request.method == 'POST':
        instance.delete()
        return redirect('app:orders_list')
    return render(request, template, context)


@login_required
def edit_order(request, pk):
    template = 'app/edit_delete_order.html'
    instance = get_object_or_404(Orders, order_number=pk)
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
def edit_order_detail(request, **kwargs):
    template = 'app/edit_order_detail.html'
    instance = get_object_or_404(OrderDetail, pk=kwargs['pk'])
    order_number = instance.order_number.order_number
    form = EditOrderDetailForm(instance=instance)
    context = {'form': form}
    if request.method == 'POST':
        form = EditOrderDetailForm(request.POST, instance=instance)
        if form.is_valid():
            form.save()
            change_order_detail_fields(instance)
            update_catalog(instance)
            return redirect('app:order_detail', pk=order_number)
    return render(request, template, context)


@login_required
def received_order(request, pk):
    template = 'app/received_order.html'
    order = get_object_or_404(Orders, order_number=pk)
    form = ReceivedForm(request.POST or None)
    context = {'form': form}
    if request.method == 'POST':
        form = ReceivedForm(request.POST, instance=order)
        if form.is_valid():
            form.save()
            redirect_url = reverse('app:orders_list')
            return HttpResponseRedirect(redirect_url)
    return render(request, template, context)


# Каталог
@login_required
def catalog(request):
    template = 'app/catalog.html'
    catalog = Catalog.objects.select_related('created_by').filter(
        is_published=True).annotate(
        count_stock=Count('order_detail__goods',
                      filter=(Q(order_detail__goods__received_date__received_date__isnull=False) &
                             Q(order_detail__goods__sale_date__sale_date__isnull=True))),
        count_wait=Count('order_detail__goods',
                      filter=Q(order_detail__goods__received_date__received_date__isnull=True))).order_by('title')[:100]
    paginator = Paginator(catalog, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    context = {'page_obj': page_obj}
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
    template = 'app/catalog_detail.html'
    product = get_object_or_404(Catalog, pk=pk)
    product_count_stock = Goods.objects.filter(
        Q(received_date__received_date__isnull=False),
          Q(sale_date__sale_date__isnull=True),
            product__product=pk).values('id').count()
    product_count_wait = Goods.objects.filter(
        Q(received_date__received_date__isnull=True), product__product=pk).values('id').count()
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
        'received_date__received_date',
        'sale_price_RUB__sale_price_RUB',
        'cost_price_RUB__cost_price_RUB',
        'sale_date__sale_date').order_by('sale_date')
    paginator = Paginator(sale_list, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    context = {'product': product, 'page_obj': page_obj, 'order_list': order_list,
               'product_count_stock': product_count_stock,
               'product_count_wait': product_count_wait}
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
                      filter=(Q(order_detail__goods__received_date__received_date__isnull=False) &
                            Q(order_detail__goods__sale_date__sale_date__isnull=True))),
    count_wait=Count('order_detail__goods',
                      filter=Q(order_detail__goods__received_date__received_date__isnull=True)),
    cost_stock=Sum('order_detail__goods__cost_price_RUB__cost_price_RUB',
                 filter=(Q(order_detail__goods__received_date__received_date__isnull=False) &
                            Q(order_detail__goods__sale_date__sale_date__isnull=True))),
    cost_wait=Sum('order_detail__goods__cost_price_RUB__cost_price_RUB',
                 filter=Q(order_detail__goods__received_date__received_date__isnull=True))).order_by('-count_stock')
    total_count_stock = Goods.objects.filter(
        Q(received_date__received_date__isnull=False) &
        Q(sale_date__sale_date__isnull=True)).values('id').count()
    total_count_wait = Goods.objects.filter(
        Q(received_date__received_date__isnull=True)).values('id').count()
    total_list = Goods.objects.filter(
        is_published=True).annotate(
        cost_stock=Sum('cost_price_RUB__cost_price_RUB', filter=(
            Q(received_date__received_date__isnull=False) &
            Q(sale_date__sale_date__isnull=True))),
        cost_wait=Sum('cost_price_RUB__cost_price_RUB', filter=(
            Q(received_date__received_date__isnull=True))))
    total_cost_stock = total_list.aggregate(
        total_cost_stock=Sum('cost_stock'))['total_cost_stock']
    total_cost_wait = total_list.aggregate(
        total_cost_wait=Sum('cost_wait'))['total_cost_wait']
    context = {'stock_list': stock_list,
               'total_count_stock': total_count_stock,
               'total_cost_stock': total_cost_stock,
               'total_count_wait': total_count_wait,
               'total_cost_wait': total_cost_wait}
    return render(request, template, context)


#  Продажи
@login_required
def sale_detail_add(request):
    sale_number = request.GET.get('sale_number')
    sale_date = request.GET.get('sale_date')
    client_name = request.GET.get('client_name')
    quantity_name = int(request.GET.get('quantity'))
    payment_type = Payment_type.objects.get(
        id=int(request.GET.get('payment_type')))
    client_type = Client_type.objects.get(
        id=int(request.GET.get('client_type')))
    receiving_type = Receiving_type.objects.get(
        id=int(request.GET.get('receiving_type')))
    template = 'app/sale_detail_add.html'
    forms = []
    product_list = []

    if request.method == 'POST':
        for i in range(quantity_name):
            form = SaleDetailForm(request.POST, prefix=f'form_{i+1}')
            forms.append(form)
        if all(form.is_valid() for form in forms):
            sale = Sales.objects.create(
                sale_number=sale_number,
                created_by=request.user,
                sale_date=datetime.strptime(sale_date, "%Y-%m-%d"),
                quantity=quantity_name,
                payment_type=payment_type,
                client_type=client_type,
                receiving_type=receiving_type,
                client_name=client_name
            )
            for i in range(quantity_name):
                quantity = int(request.POST.get(
                    'form_' + str(i+1) + '-quantity'))
                product = Catalog.objects.get(
                    id=int(request.POST.get('form_' + str(i+1) + '-product')))
                sale_detail = SaleDetail.objects.create(
                    sale_number=Sales.objects.get(id=sale.id),
                    sale_date=Sales.objects.get(id=sale.id),
                    created_by=request.user,
                    product=product,
                    quantity=quantity,
                    sale_price_RUB=request.POST.get(
                        'form_' + str(i+1) + '-sale_price_RUB')
                )
                sale_detail.save()
                product_list.append(f'{product} - {quantity} ед.')
                sale.product_list = ', '.join(
                    str(item) for item in product_list)
                sale.save()
                update_goods(sale_detail, quantity)
            total_price = SaleDetail.objects.filter(
                sale_number=sale.id).aggregate(
                total_price=Sum(
                    F('quantity') * F('sale_price_RUB')))['total_price']
            sale.total_price = total_price
            sale.save()
            return redirect('app:sales_list')
    else:
        for i in range(quantity_name):
            form = SaleDetailForm(prefix=f'form_{i+1}')
            forms.append(form)

    context = {'forms': forms}
    return render(request, template, context)


@login_required
def sale_add(request):
    template = 'app/sale_add.html'
    form = SaleForm(request.POST or None)
    context = {'form': form}
    if form.is_valid():
        sale_number = form.cleaned_data['sale_number']
        sale_date = form.cleaned_data['sale_date'].date()
        quantity = form.cleaned_data['quantity']
        payment_type = form.cleaned_data['payment_type'].id
        client_type = form.cleaned_data['client_type'].id
        receiving_type = form.cleaned_data['receiving_type'].id
        client_name = form.cleaned_data['client_name']
        redirect_url = (
            reverse('app:sale_detail_add') +
            f'?sale_number={sale_number}&sale_date={sale_date}'
            f'&quantity={quantity}&payment_type={payment_type}'
            f'&client_type={client_type}&receiving_type={receiving_type}'
            f'&client_name={client_name}')
        return HttpResponseRedirect(redirect_url)
    return render(request, template, context)


@login_required
def sales_list(request):
    template = 'app/sales_list.html'
    sales_list = Sales.objects.select_related(
        'created_by', 'payment_type', 'receiving_type', 'client_type').filter(
        is_published=True)
    paginator = Paginator(sales_list, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    context = {'page_obj': page_obj}
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
        'product__title',
        'sale_price_RUB')
    sale_info = get_object_or_404(Sales, sale_number=pk)
    context = {'sale_info': sale_info, 'sale_info_detail': sale_info_detail}
    return render(request, template, context)


@login_required
def sale_delete(request, pk):
    template = 'app/sale_edit_delete.html'
    instance = get_object_or_404(Sales, sale_number=pk)
    form = SaleEditDeleteForm(instance=instance)
    context = {'form': form}
    if request.method == 'POST':
        instance.delete()
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
def sale_detail_edit(request, **kwargs):
    template = 'app/sale_edit_detail.html'
    instance = get_object_or_404(SaleDetail, pk=kwargs['pk'])
    sale_number = instance.sale_number.sale_number
    form = SaleEditDetailForm(instance=instance)
    context = {'form': form}
    if request.method == 'POST':
        form = SaleEditDetailForm(request.POST, instance=instance)
        if form.is_valid():
            form.save()
            change_sale_detail_fields(instance)
            return redirect('app:sale_detail', pk=sale_number)
    return render(request, template, context)


@login_required
def goods_list(request):
    template = 'app/goods_list.html'
    form_product = FilterProductForm(request.POST or None)
    goods_list = Goods.objects.select_related(
        'order_number', 'order_date', 'received_date',
        'product', 'product__product',
        'ordering_price_RMB', 'cost_price_RUB', 'created_by').filter(
        is_published=True).values(
        'order_number__order_number', 'order_date__order_date',
        'received_date__received_date', 'cost_price_RUB__cost_price_RUB',
        'product__product__title', 'sale_date__sale_date',
        'sale_price_RUB__sale_price_RUB').order_by('order_number')
    if request.method == 'POST':
        form_product = FilterProductForm(request.POST)
        if form_product.is_valid():
            product = form_product.cleaned_data['product']
            goods_list = goods_list.filter(product__product=product)
    paginator = Paginator(goods_list, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    context = {'page_obj': page_obj, 'form_product': form_product}
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
        return reverse('app:profile',
                       kwargs={'username': self.request.user.username})
    

@login_required
def settings_edit(request):
    template = 'app/settings_edit.html'
    settings = CustomSettings.objects.get_or_create(pk=1)[0]
    form = CustomSettingsForm(request.POST or None, instance=settings)
    if request.method == 'POST':
        if form.is_valid():
            form.save()
            update_exchange_rate(settings.exchange_rate)
            return redirect('app:profile', username=request.user.username)
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
            received_date = row['received_date'].to_pydatetime()
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
                cost_price_RUB=int(row[2])
                ordering_price_RMB=int(row[3])
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
            last_sale = Sales.objects.order_by('id').last()
            sale_number = last_sale.sale_number + 1
            sale_date = row['sale_date'].to_pydatetime()
            created_by = request.user
            payment_type = Payment_type.objects.get(title=row['payment_type'])
            client_type = Client_type.objects.get(title=row['client_type'])
            receiving_type = Receiving_type.objects.get(title=row['receiving_type'])
            client_name = row['client_name']
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
                    client_name=client_name
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
            instance = Catalog(
                title=title,
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



"""
def import_sales_data(request):
    template = 'app/import_sales_data.html'
    count = 0
    if request.method == 'POST':
        excel_file = request.FILES['file']
        decoded_file = excel_file.read()

        df1 = pd.read_excel(decoded_file, sheet_name=0)
        for _, row in df1.iterrows():
            product_list = []
            sale_number = int(row['sale_number'])
            sale_date = row['sale_date'].to_pydatetime()
            quantity_name = int(row['quantity'])
            created_by = request.user
            payment_type = Payment_type.objects.get(title=row['payment_type'])
            client_type = Client_type.objects.get(title=row['client_type'])
            receiving_type = Receiving_type.objects.get(title=row['receiving_type'])
            client_name = row['client_name']
            sale = Sales(
                sale_number=sale_number,
                sale_date=sale_date,
                quantity=quantity_name,
                created_by=created_by,
                payment_type=payment_type,
                client_type=client_type,
                receiving_type=receiving_type,
                client_name=client_name,
                is_published=True)
            sale.save()

            df2 = pd.read_excel(decoded_file, sheet_name=1)
            for _, row in df2.iloc[count:count+quantity_name].iterrows():
                created_by=User.objects.get(username=request.user.username)
                quantity=int(row[0])
                product = Catalog.objects.get(title=row[1])
                sale_price_RUB=int(row[2])
                sale_detail = SaleDetail(
                    sale_number=sale,
                    sale_date=sale,
                    created_by=created_by,
                    product=product,
                    quantity=quantity,
                    sale_price_RUB=sale_price_RUB
                    )
                sale_detail.save()
                product_list.append(f'{product} - {quantity} ед.')
                sale.product_list = ', '.join(str(item) for item in product_list)
                sale.save()
                update_goods(sale_detail, quantity)
            count = count + quantity_name
            total_price = SaleDetail.objects.filter(
                sale_number=sale.id).aggregate(
                total_price=Sum(
                    F('quantity') * F('sale_price_RUB')))['total_price']
            sale.total_price = total_price
            sale.save()
        return render(request, 'app/import_success.html')

    return render(request, template)
"""