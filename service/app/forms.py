from django import forms
from datetime import date
import datetime

from .models import Orders, Goods, Payment_type, Catalog
from .utils import max_value


class OrderForm(forms.Form):
    number = forms.IntegerField(
        label="Номер закупки",
        initial=max_value() + 1,
        help_text=f'Номер последней закупки - {max_value}'
        )
    order_date = forms.DateField(
        label='Дата закупки',
        initial=date.today(),
        help_text=f'Сегодня - {date.today().strftime("%d %m")}'
        )
    quantity = forms.IntegerField(
        label='Количество наименований товара',
        )


class OrderDetailForm(forms.Form):
    product = forms.ModelChoiceField(
        queryset=Catalog.objects.all(),
        label="Продукт",
        help_text='Выберете продукт'
        )
    quantity = forms.IntegerField(
        label='Количество единиц товаров',
        help_text='Укажите количество товаров'
        )
    cost_price_RUB = forms.DecimalField(
        label='Себестоимость в руб. (Например, 25123.13)',
        help_text='Укажите себестоимость товара в рублях',
        max_digits=9, decimal_places=2)


class SaleForm(forms.Form):
    number = forms.IntegerField(
        label="Номер продажи",
        help_text='Укажите номер продажи'
        )
    sale_date = forms.DateField(
        label='Дата продажи',
        help_text='Укажите дату продажи'
        )
    quantity = forms.IntegerField(
        label='Количество', 
        help_text='Укажите количество наименований товара'
        )
    payment_type = forms.ModelChoiceField(
        queryset=Payment_type.objects.all(),
        label='Способ оплаты',
        help_text='Выберите способ оплаты'
        )
    

class SaleDetailForm(forms.ModelForm):

    class Meta:
        model = Goods
        fields = ('product', 'selling_price_RUB',)
        widgets = {
            'selling_price_RUB': forms.Textarea(attrs={'cols': '40', 'rows': '1'})}


class ReceivedForm(forms.ModelForm):

    class Meta:
        model = Orders
        fields = ('received_date',)
        widgets = {
            'received_date': forms.DateInput(attrs={'type': 'date'})}
        

class DeleteOrderForm(forms.ModelForm):

    class Meta:
        model = Orders
        fields = ('order_number', 'order_date',)
        widgets = {
            'order_date': forms.DateInput(attrs={'format': '%d.%m.%Y'})}

"""

class ReceivedForm(forms.Form):
    received_date = forms.DateField(
        label='Дата получения закупки',
        initial=date.today(),
        help_text=f'Сегодня - {date.today().strftime("%d %m")}'
        )
"""