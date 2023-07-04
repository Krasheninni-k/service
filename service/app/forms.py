from django import forms
from datetime import date
from django.core.exceptions import ValidationError
from django.utils import timezone

from .models import Orders, Goods, Payment_type, OrderDetail
from .utils import max_value


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
        fields = ('product', 'cost_price_RUB', 'quantity', 'ordering_price_RMB')
        widgets = {
            'cost_price_RUB': forms.Textarea(attrs={'cols': '40', 'rows': '1'}),
            'ordering_price_RMB': forms.Textarea(attrs={'cols': '40', 'rows': '1'})}


class ReceivedForm(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        super(ReceivedForm, self).__init__(*args, **kwargs)
        initial = date.today().strftime("%d.%m.%Y")
        self.fields['received_date'].initial = initial
        self.fields['received_date'].help_text = f'Сегодня - { initial }'

    def clean_received_date(self):
        received_date = self.cleaned_data.get('received_date')
        current_date = timezone.now().date()
        if received_date.date() > current_date:
            raise ValidationError("Нельзя указывать дату в будущем.")
        return received_date

    class Meta:
        model = Orders
        fields = ('received_date',)
        widgets = {
            'received_date': forms.DateInput(attrs={'format': '%d.%m.%Y'})}


class EditDeleteOrderForm(forms.ModelForm):

    def clean(self):
        super().clean()

    def clean_received_date(self):
        received_date = self.cleaned_data['received_date']
        current_date = timezone.now().date()
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
