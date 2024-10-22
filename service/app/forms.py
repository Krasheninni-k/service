from django import forms
from datetime import date
from django.core.exceptions import ValidationError
from django.utils import timezone
from datetime import datetime
from dateutil.relativedelta import relativedelta
from django.forms import modelformset_factory

from .models import (Orders, OrderDetail, Catalog, Sales, SaleDetail, Goods,
                      Client_type, Payment_type, Receiving_type, CustomSettings)
from .utils import max_value, max_value_sale

# Закупки
class OrderForm(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        super(OrderForm, self).__init__(*args, **kwargs)
        max_order_number = max_value()
        initial = date.today().strftime("%d.%m.%Y")
        self.fields['order_number'].initial = max_order_number + 1
        self.fields['order_number'].help_text = f'Номер последней закупки - { max_order_number }'
        self.fields['order_date'].initial = initial
        self.fields['order_date'].help_text = f'Сегодня - { initial }'

    def clean(self):
        super().clean()

    def clean_order_date(self):
        order_date = self.cleaned_data.get('order_date')
        current_date = timezone.now().date()
        if order_date.date() > current_date:
            raise ValidationError("Нельзя указывать дату в будущем.")
        return order_date

    class Meta:
        model = Orders
        fields = ('order_number', 'order_date', 'quantity')


class OrderDetailForm(forms.ModelForm):

    class Meta:
        model = OrderDetail
        fields = (
            'product', 'cost_price_RUB', 'quantity', 'ordering_price_RMB')
        widgets = {
            'cost_price_RUB': forms.Textarea(attrs={'cols': '40', 'rows': '1'}),
            'ordering_price_RMB': forms.Textarea(attrs={'cols': '40', 'rows': '1'})}


class EditDeleteOrderForm(forms.ModelForm):

    def clean(self):
        super().clean()

    def clean_received_date(self):
        received_date = self.cleaned_data['received_date']
        current_date = timezone.now().date()
        if received_date is not None:
            if received_date.date() > current_date:
                raise ValidationError("Нельзя указывать дату в будущем.")
        return received_date

    def clean_order_date(self):
        order_date = self.cleaned_data['order_date']
        current_date = timezone.now().date()
        if order_date.date() > current_date:
            raise ValidationError("Нельзя указывать дату в будущем.")
        return order_date

    class Meta:
        model = Orders
        fields = ('order_number', 'order_date', 'received_date')
        widgets = {
            'order_date': forms.DateInput(attrs={'format': '%d.%m.%Y'}),
            'received_date': forms.DateInput(attrs={'format': '%d.%m.%Y'})}


class EditOrderDetailForm(forms.ModelForm):

    class Meta:
        model = OrderDetail
        fields = ('product', 'cost_price_RUB', 'ordering_price_RMB')
        widgets = {
            'cost_price_RUB': forms.Textarea(attrs={'cols': '40', 'rows': '1'}),
            'ordering_price_RMB': forms.Textarea(attrs={'cols': '40', 'rows': '1'})}


# Каталог
class CatalogForm(forms.ModelForm):

    class Meta:
        model = Catalog
        exclude = ('created_at', 'created_by', 'target_last_order_price_RUB',
                   'target_current_RMB_price_RUB', 'is_published')
        widgets = {
            'description': forms.Textarea(attrs={'cols': '40', 'rows': '3'})}

# Продажи
class SaleForm(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        super(SaleForm, self).__init__(*args, **kwargs)
        max_sale_number = max_value_sale()
        initial = date.today().strftime("%d.%m.%Y")
        self.fields['sale_number'].initial = max_sale_number + 1
        self.fields['sale_number'].help_text = f'Номер последней продажи - { max_sale_number }'
        self.fields['sale_date'].initial = initial
        self.fields['sale_date'].help_text = f'Сегодня - { initial }'
        self.fields['client_type'].initial = Client_type.objects.first()
        self.fields['payment_type'].initial = Payment_type.objects.first()
        self.fields['receiving_type'].initial = Receiving_type.objects.first()

    def clean(self):
        super().clean()

    def clean_order_date(self):
        sale_date = self.cleaned_data.get('sale_date')
        current_date = timezone.now().date()
        if sale_date.date() > current_date:
            raise ValidationError("Нельзя указывать дату в будущем.")
        return sale_date

    class Meta:
        model = Sales
        exclude = ('created_at', 'created_by', 'product_list', 'is_published', 'total_price', 'cash', 'quantity')
        widgets = {
            'comment': forms.Textarea(attrs={'cols': '40', 'rows': '3'})}

# Форма для внесения цены единицы товара
class SalePriceForm(forms.ModelForm):

    class Meta:
        model = Goods
        fields = ('sale_price',)
        widgets = {
            'sale_price': forms.TextInput(attrs={'class': 'form-control', 'style': 'width: 100px;'}),
        }

    # def __init__(self, *args, **kwargs):
        # good = kwargs.get('instance', None)
        # super(SalePriceForm, self).__init__(*args, **kwargs)
        # if good and getattr(good, 'product', None) and getattr(good.product, 'product', None):
        #    self.fields['sale_price'].initial = getattr(good.product.product, 'price_RUB', 0)

class SaleEditDeleteForm(forms.ModelForm):

    def clean(self):
        super().clean()

    def clean_order_date(self):
        sale_date = self.cleaned_data['sale_date']
        current_date = timezone.now().date()
        if sale_date.date() > current_date:
            raise ValidationError("Нельзя указывать дату в будущем.")
        return sale_date

    class Meta:
        model = Sales
        exclude = ('created_at', 'created_by', 'product_list', 'is_published', 'total_price', 'quantity', 'comment')
        widgets = {
            'sale_date': forms.DateInput(attrs={'format': '%d.%m.%Y'})}


class SaleEditDetailForm(forms.ModelForm):

    class Meta:
        model = SaleDetail
        fields = ('product', 'sale_price_RUB')
        widgets = {
            'sale_price_RUB': forms.Textarea(attrs={'cols': '40', 'rows': '1'})}
        

class CustomSettingsForm(forms.ModelForm):
   
   class Meta:
        model = CustomSettings
        fields = '__all__'


class FilterProductForm(forms.Form):
    product = forms.ModelChoiceField(
        queryset=Catalog.objects.all(),
        label="Товар",
        required=False
        )


class StartEndDateForm(forms.Form):
    start_date = forms.DateField(
        label="Начало",
        required=False,
        widget=forms.DateInput(attrs={'type':'date', 'class': 'form-control'})
        )
    end_date = forms.DateField(
        label="Конец",
        required=False,
        widget=forms.DateInput(attrs={'type':'date', 'class': 'form-control'})
        )

# Форма для редактирования товара
class EditGoodDetailForm(forms.ModelForm):

    class Meta:
        model = Goods
        fields = ('sn_number', 'defect', 'comment', 'received_date', 'received')
        widgets = {
            'sn_number': forms.Textarea(attrs={'cols': '40', 'rows': '1'}),
            'comment': forms.Textarea(attrs={'cols': '40', 'rows': '1'})}

# Форма для выбора отчетного месяца.
class MonthForm(forms.Form):
    start_date = Sales.objects.last().sale_date
    end_date = Sales.objects.first().sale_date
    months_between_dates = []
    current_date = end_date
    while current_date >= start_date:
        months_between_dates.append((current_date, current_date.strftime('%B %Y')))
        current_date -= relativedelta(months=1)

    month = forms.ChoiceField(
        choices=months_between_dates,
        label='Выберите месяц'
    )
