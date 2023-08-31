from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()


class BaseModel(models.Model):
    created_at = models.DateTimeField('Создано', auto_now_add=True)
    created_by = models.ForeignKey(
        User, on_delete=models.CASCADE,
        verbose_name='Автор записи')
    is_published = models.BooleanField('Опубликовано', default=True)

    class Meta:
        abstract = True


class Catalog(BaseModel):
    title = models.CharField('Название', max_length=256)
    description = models.TextField('Описание', blank=True)
    price_RUB = models.DecimalField(
        'Цена по прайсу, руб.', max_digits=9, decimal_places=2,
        null=True, blank=True, default=0)
    target_last_order_price_RUB = models.DecimalField(
        'Расчетная цена от последней закупки, руб.', max_digits=9, decimal_places=2,
        null=True, blank=True, default=0)
    target_current_RMB_price_RUB = models.DecimalField(
        'Расчетная цена от курса, руб.', max_digits=9, decimal_places=2,
        null=True, blank=True, default=0)
    market_price_RUB = models.DecimalField(
        'Рыночная цена, руб.', max_digits=9, decimal_places=2,
        null=True, blank=True, default=0)
    order_price_RMB = models.DecimalField(
        'Цена закупки в юанях.', max_digits=9, decimal_places=2,
        null=True, blank=True, default=0)
    image = models.ImageField('Фото', upload_to='app_images', blank=True)
    length = models.DecimalField(
        'Длина в см', max_digits=4, decimal_places=1,
        null=True, blank=True, default=0)
    width = models.DecimalField(
        'Ширина в см', max_digits=4, decimal_places=1,
        null=True, blank=True, default=0)
    height = models.DecimalField(
        'Высота в см', max_digits=4, decimal_places=1,
        null=True, blank=True, default=0)
    weight = models.DecimalField(
        'Вес в кг', max_digits=5, decimal_places=3,
        null=True, blank=True, default=0)

    class Meta:
        verbose_name = 'Каталог товаров'
        verbose_name_plural = 'Каталог товаров'

    def __str__(self):
        return self.title


class Payment_type(BaseModel):
    title = models.CharField('Способ оплаты', max_length=256)

    class Meta:
        verbose_name = 'Способ оплаты'
        verbose_name_plural = 'Способы оплаты'

    def __str__(self):
        return self.title


class Receiving_type(BaseModel):
    title = models.CharField('Способ получения', max_length=256)

    class Meta:
        verbose_name = 'Способ получения'
        verbose_name_plural = 'Способы получения'

    def __str__(self):
        return self.title


class Client_type(BaseModel):
    title = models.CharField('Тип покупателя', max_length=256, default='ФЛ')

    class Meta:
        verbose_name = 'Тип покупателя'
        verbose_name_plural = 'Типы покупателей'

    def __str__(self):
        return self.title


class Orders(BaseModel):
    order_number = models.IntegerField('Номер закупки',  default=0)
    order_date = models.DateTimeField('Дата закупки', blank=True)
    quantity = models.IntegerField('Количество единиц товаров',  default=1)
    product_list = models.TextField('Cостав закупки', blank=True)
    total_cost = models.DecimalField(
        'Себестоимость закупки', max_digits=8, decimal_places=2,
        null=True, blank=True, default=0)
    received_date = models.DateTimeField('Дата получения закупки',
                                         null=True, blank=True)
    comment = models.CharField('Комментарий', max_length=256)

    class Meta:
        verbose_name = 'Закупка'
        verbose_name_plural = 'Закупки'
        ordering = ['-order_number']
        constraints = (models.UniqueConstraint(
            fields=('order_number',), name='Unique order_number',),)

    def __str__(self):
        date = self.order_date.strftime('%Y-%m-%d')
        return f'{self.order_number} - {date} - {self.product_list}'


class OrderDetail(BaseModel):
    order_number = models.ForeignKey(
        Orders,
        on_delete=models.CASCADE,
        related_name='order_detail_order_number',
        verbose_name='Номер закупки',
        null=True, blank=True)
    order_date = models.ForeignKey(
        Orders,
        on_delete=models.CASCADE,
        related_name='order_detail_order_date',
        verbose_name='Дата закупки',
        null=True, blank=True)
    received_date = models.ForeignKey(
        Orders,
        on_delete=models.CASCADE,
        related_name='order_detail_received_date',
        verbose_name='Дата получения',
        null=True, blank=True)
    product = models.ForeignKey(
        Catalog,
        on_delete=models.CASCADE,
        related_name='order_detail',
        verbose_name='Товар')
    quantity = models.IntegerField('Количество единиц товаров',  default=1)
    ordering_price_RMB = models.DecimalField(
        'Цена закупки в юанях', max_digits=8, decimal_places=2,
        null=True, blank=True, default=0)
    cost_price_RUB = models.DecimalField(
        'Себестоимость в руб.', max_digits=9, decimal_places=2,
        null=True, blank=True, default=0)


class Sales(BaseModel):
    sale_number = models.IntegerField('Номер продажи',  default=0)
    sale_date = models.DateTimeField('Дата продажи')
    quantity = models.IntegerField('Количество наименований товаров',  default=1)
    product_list = models.TextField('Cостав продажи', blank=True)
    total_price = models.DecimalField(
        'Цена проджаи', max_digits=10, decimal_places=2,
        null=True, blank=True, default=0)
    payment_type = models.ForeignKey(
        Payment_type,
        on_delete=models.SET_NULL,
        related_name='goods',
        verbose_name='Способ оплаты',
        null=True)
    client_type = models.ForeignKey(
        Client_type,
        on_delete=models.SET_NULL,
        related_name='goods',
        verbose_name='Тип покупателя',
        null=True)
    receiving_type = models.ForeignKey(
        Receiving_type,
        on_delete=models.SET_NULL,
        related_name='goods',
        verbose_name='Тип получения',
        null=True)
    client_name = models.CharField('Имя покупателя', max_length=256, null=True)
    client_contact = models.CharField('Контакт', max_length=256, null=True)
    regular_client = models.BooleanField('Повторное обращение', default=False)
    comment = models.CharField('Комментарий', max_length=256, null=True, blank=True)

    class Meta:
        verbose_name = 'Продажа'
        verbose_name_plural = 'Продажи'
        ordering = ['-sale_number']
        constraints = (models.UniqueConstraint(
            fields=('sale_number',), name='Unique sale_number',),)

    def __str__(self):
        date = self.sale_date.strftime('%Y-%m-%d')
        return f'{self.sale_number} - {date} - {self.product_list}'
    

class SaleDetail(BaseModel):
    sale_number = models.ForeignKey(
        Sales,
        on_delete=models.CASCADE,
        related_name='sale_detail_sale_number',
        verbose_name='Номер продажи',
        null=True, blank=True)
    sale_date = models.ForeignKey(
        Sales,
        on_delete=models.CASCADE,
        related_name='sale_detail_sale_date',
        verbose_name='Дата продажи',
        null=True, blank=True)
    product = models.ForeignKey(
        Catalog,
        on_delete=models.CASCADE,
        related_name='sale_detail',
        verbose_name='Товар')
    quantity = models.IntegerField('Количество единиц товаров',  default=1)
    sale_price_RUB = models.DecimalField(
        'Цена продажи', max_digits=9, decimal_places=2,
        null=True, blank=True, default=0)
    
    class Meta:
        verbose_name = 'Детали продаж'
        verbose_name_plural = 'Детали продаж'
        ordering = ['-sale_number']

class Goods(BaseModel):
    order_number = models.ForeignKey(
        Orders,
        on_delete=models.CASCADE,
        related_name='goods_order_number',
        null=True, blank=True)
    order_date = models.ForeignKey(
        Orders,
        on_delete=models.CASCADE,
        related_name='goods_order_date',
        null=True, blank=True)
    received_date = models.ForeignKey(
        Orders,
        on_delete=models.CASCADE,
        related_name='goods_received_date',
        null=True, blank=True)
    product = models.ForeignKey(
        OrderDetail,
        on_delete=models.CASCADE,
        related_name='goods',
        verbose_name='Наименование товара')
    price_RUB = models.ForeignKey(
        Catalog,
        on_delete=models.SET_NULL,
        related_name='goods',
        verbose_name='Цена по прайсу',
        null=True, blank=True)
    ordering_price_RMB = models.ForeignKey(
        OrderDetail,
        on_delete=models.CASCADE,
        related_name='goods_ordering_price_RMB',
        verbose_name='Цена закупки в юанях',
        null=True, blank=True)
    cost_price_RUB = models.ForeignKey(
        OrderDetail,
        on_delete=models.CASCADE,
        related_name='goods_cost_price_RUB',
        verbose_name='Себестоимость в рублях',
        null=True, blank=True)
    sale_date = models.ForeignKey(
        Sales,
        on_delete=models.SET_NULL,
        related_name='goods_sale_date',
        verbose_name='Дата продажи',
        null=True, blank=True)
    sale_price_RUB = models.ForeignKey(
        SaleDetail,
        on_delete=models.SET_NULL,
        related_name='goods_sale_price_RUB',
        verbose_name='Цена продажи',
        null=True, blank=True)
    payment_type = models.ForeignKey(
        Sales,
        on_delete=models.SET_NULL,
        related_name='goods_payment_type',
        verbose_name='Способ оплаты',
        null=True, blank=True)
    client_type = models.ForeignKey(
        Sales,
        on_delete=models.SET_NULL,
        related_name='goods_client_type',
        verbose_name='Тип покупателя',
        null=True, blank=True)
    receiving_type = models.ForeignKey(
        Sales,
        on_delete=models.SET_NULL,
        related_name='goods_receiving_type',
        verbose_name='Тип получения',
        null=True, blank=True)
    margin = models.DecimalField(
        'Маржа, руб.', max_digits=9, decimal_places=2,
        null=True, blank=True, default=0)
    markup = models.DecimalField(
        'Наценка, %', max_digits=9, decimal_places=2,
        null=True, blank=True, default=0)
    days_in_stock = models.IntegerField('Дней на складе', null=True, blank=True, default=0)

    class Meta:
        verbose_name = 'Товар'
        verbose_name_plural = 'Товары'
        ordering = ('order_date', 'product')

    def __str__(self):
        return self.product


class CustomSettings(models.Model):
    exchange_rate = models.DecimalField(
        'Биржевой курс валюты (китайский юань)', max_digits=7, decimal_places=4, default=12.5000)
    delivery_cost = models.DecimalField(
        'Средние издержки на доставку, %', max_digits=5, decimal_places=2, default=10)
    markup_128 = models.IntegerField('Наценка для товаров с себестом более 128к, %', default=25)
    markup_64 = models.IntegerField('Наценка для товаров с себестом более 64к, %', default=30)
    markup_32 = models.IntegerField('Наценка для товаров с себестом более 32к, %', default=35)
    markup_16 = models.IntegerField('Наценка для товаров с себестом более 16к, %', default=40)
    markup_8 = models.IntegerField('Наценка для товаров с себестом более 8к, %', default=50)
    markup_4 = models.IntegerField('Наценка для товаров с себестом более 4к, %', default=70)
    markup_2 = models.IntegerField('Наценка для товаров с себестом более 2к, %', default=90)
    markup_0 = models.IntegerField('Наценка для товаров с себестом менее 2к, %', default=120)

    class Meta:
        verbose_name = 'Настройки'
        verbose_name_plural = 'Настройки'

    def __str__(self):
        return self.exchange_rate
