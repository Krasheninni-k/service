from django.core.management.base import BaseCommand
from app.models import Goods

# python manage.py update_received_date
class Command(BaseCommand):
    help = 'Update received_date, sold, and sale_price in Goods from related Orders'

    def handle(self, *args, **kwargs):
        # Используем select_related для оптимизации запросов
        goods_list = Goods.objects.filter(order_number__isnull=False).select_related('order_number')
        updated_count = 0

        # Обновляем каждую запись
        for good in goods_list:
            # Обновляем поле received_date
            good.received_date = good.order_number.received_date
            
            # Если sale_date отсутствует, устанавливаем sold = True
            if good.sale_date is not None:
                good.sold = True
            else:
                good.sold = False

            # Если у товара есть поле sale_prce_RUB, обновляем sale_price
            if good.sale_price_RUB is not None:
                good.sale_price = good.sale_price_RUB.sale_price_RUB

            # Сохраняем изменения
            good.save()
            updated_count += 1

        # Выводим количество обновленных записей
        self.stdout.write(self.style.SUCCESS(f'{updated_count} records updated successfully.'))

