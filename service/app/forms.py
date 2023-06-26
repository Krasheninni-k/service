from django import forms

from .models import Orders

class OrderForm(forms.Form):
    number = forms.IntegerField(
        label="Номер закупки",
        help_text='Укажите номер закупки'
    )
    order_date = forms.DateField(
        label='Дата закупки',
        help_text='Укажите дату'
    )
    quantity = forms.IntegerField(
        label='Количество', 
        help_text='Укажите количество')

class OrderDetailForm(forms.ModelForm):

    class Meta:
        model = Orders
        fields = ('product', 'quantity', 'cost_price_RUB',)
        widgets = {
            'quantity': forms.Textarea(attrs={'cols': '40', 'rows': '1'}),
            'cost_price_RUB': forms.Textarea(attrs={'cols': '40', 'rows': '1'})
        }

"""
class OrderDetailForm(forms.Form):
    product_name = forms.CharField(
        label='Товар',
        max_length=100,
        help_text='Выберете товар'
        )
    quantity = forms.IntegerField(
        label='Количество', 
        help_text='Укажите количество')
    cost = forms.DecimalField(
        label='Себестоимость', 
        max_digits=10, decimal_places=2,
        help_text='Укажите себестоимость в руб.'
        )


        

class CommentForm(forms.ModelForm):

    class Meta:
        model = Comment
        fields = ('text',)

from django import forms
from .models import Orders


class SaleForm(forms.Form):
    title = forms.CharField(
        label='Товар',
        max_length=100,
        help_text='Выберете товар'
    )
    quantity = forms.IntegerField(
        label='Количество',
        min_value=1, max_value=100,
        help_text='Введите количество товаров'
    )
    price = forms.DecimalField(
        label='Цена продажи',
        max_digits=8,
        decimal_places=2,
        help_text='Введите цену продажи'
    )
    client_type = forms.CharField(
        label='Тип клиента',
        help_text='Выберете тип клиента'
    )
    payment_type = forms.CharField(
        label='Способ оплаты',
        help_text='Выберете способ оплаты'
    )
    receiving_type = forms.CharField(
        label='Способ получения',
        help_text='Выберете способ получения'
    )

"""