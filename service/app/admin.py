from django.contrib import admin

from .models import (Orders, Catalog, Payment_type,
                     Receiving_type, Client_type, Goods, Sales, OrderDetail, SaleDetail)


class SalesAdmin(admin.ModelAdmin):
    list_display = ('cash', 'sale_number', 'sale_date',
                    'product_list', 'total_price',)
    list_editable = ('cash',)
    list_display_links = ('product_list',)


admin.site.register(Catalog)
admin.site.register(Payment_type)
admin.site.register(Receiving_type)
admin.site.register(Client_type)
admin.site.register(Goods)
admin.site.register(Orders)
admin.site.register(Sales, SalesAdmin)
admin.site.register(OrderDetail)
admin.site.register(SaleDetail)
