from django.db import models
from django.contrib.auth import get_user_model

from django.db import models
from django.db.models import Max

User = get_user_model()


class BaseModel(models.Model):
    created_at = models.DateTimeField('Создано', auto_now_add=True)
    created_by = models.ForeignKey(
        User, on_delete=models.CASCADE,
        verbose_name='Автор записи')
    is_published = models.BooleanField(default=True)

    class Meta:
        abstract = True

class Catalog(BaseModel):
    title = models.CharField('Название', max_length=256)

    class Meta:
        verbose_name = 'Каталог товаров'
        verbose_name_plural = 'Каталог товаров'

    def __str__(self):
        return self.title


class Orders(BaseModel):
    number = models.IntegerField('Номер закупки',  default=0)
    comment = models.CharField('Комментарий', max_length=256)
    order_date = models.DateTimeField('Дата закупки', null=True, blank=True)
    quantity = models.IntegerField('Количество единиц товаров',  default=1)
    cost_price_RUB = models.DecimalField(
        'Себестоимость в руб. (Например, 25123.13)', max_digits=9, decimal_places=2,
        null=True, blank=True)
    product = models.ForeignKey(
        Catalog,
        on_delete=models.CASCADE,
        related_name='orders',
        verbose_name='Продукт')

    class Meta:
        verbose_name = 'Заказ'
        verbose_name_plural = 'Заказы'

    def __str__(self):
        return self.title

"""
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


class Goods(BaseModel):
    date_of_order = models.DateTimeField('Дата заказа', auto_now_add=True)
    date_of_receiving = models.DateTimeField('Дата получения', null=True,
                                             blank=True)
    date_of_sell = models.DateTimeField('Дата продажи', null=True, blank=True)
    product = models.ForeignKey(
        Catalog,
        on_delete=models.CASCADE,
        related_name='goods',
        verbose_name='Товар')
    ordering_price_RMB = models.DecimalField(
        'Цена закупки в юанях', max_digits=8, decimal_places=2,
        null=True, blank=True)
    cost_price_RUB = models.DecimalField(
        'Себестоимость в руб.', max_digits=9, decimal_places=2,
        null=True, blank=True)
    selling_price_RUB = models.DecimalField(
        'Цена продажи в руб.', max_digits=9, decimal_places=2,
        null=True, blank=True)
    payment_type = models.ForeignKey(
        Payment_type,
        on_delete=models.CASCADE,
        related_name='goods',
        verbose_name='Способ оплаты')
    client_type = models.ForeignKey(
        Client_type,
        on_delete=models.CASCADE,
        related_name='goods',
        verbose_name='Тип покупателя')
    receiving_type = models.ForeignKey(
        Receiving_type,
        on_delete=models.CASCADE,
        related_name='goods',
        verbose_name='Тип получения')

    class Meta:
        verbose_name = 'Товар'
        verbose_name_plural = 'Товары'
        ordering = ('date_of_order', 'product')

    def __str__(self):
        return self.product




User = get_user_model()


class BaseModel(models.Model):
    is_published = models.BooleanField(
        'Опубликовано',
        default=True,
        help_text='Снимите галочку, чтобы скрыть публикацию.'
    )
    created_at = models.DateTimeField('Добавлено', auto_now_add=True)

    class Meta:
        abstract = True


class Location(BaseModel):
    name = models.CharField('Название места', max_length=256)

    class Meta:
        verbose_name = 'местоположение'
        verbose_name_plural = 'Местоположения'

    def __str__(self):
        return self.name


class Category(BaseModel):
    title = models.CharField('Заголовок', max_length=256)
    description = models.TextField('Описание')
    slug = models.SlugField(
        'Идентификатор',
        unique=True,
        help_text='Идентификатор страницы для URL; разрешены символы '
        'латиницы, цифры, дефис и подчёркивание.')

    class Meta:
        verbose_name = 'категория'
        verbose_name_plural = 'Категории'

    def __str__(self):
        return self.title


class Post(BaseModel):
    title = models.CharField('Заголовок', max_length=256)
    text = models.TextField('Текст')
    pub_date = models.DateTimeField(
        'Дата и время публикации',
        help_text='Если установить дату и время в будущем — '
        'можно делать отложенные публикации.')
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='post',
        verbose_name='Автор публикации'
    )
    location = models.ForeignKey(
        Location,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='post',
        verbose_name='Местоположение'
    )
    category = models.ForeignKey(
        Category,
        on_delete=models.SET_NULL,
        null=True,
        related_name='post',
        verbose_name='Категория'
    )
    image = models.ImageField('Фото', upload_to='post_images', blank=True)

    class Meta:
        verbose_name = 'публикация'
        verbose_name_plural = 'Публикации'
        ordering = ('-pub_date',)

    def __str__(self):
        return self.title


class Comment(models.Model):
    text = models.TextField('Комментарий')
    post = models.ForeignKey(
        Post, on_delete=models.CASCADE,
        related_name='comments',
        verbose_name='Публикация')
    created_at = models.DateTimeField('Добавлено', auto_now_add=True)
    author = models.ForeignKey(
        User, on_delete=models.CASCADE,
        related_name='authors',
        verbose_name='Автор комментария')

    class Meta:
        ordering = ('-created_at',)
        verbose_name = 'комментарий'
        verbose_name_plural = 'Комментарии'

"""