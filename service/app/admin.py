from django.contrib import admin

from .models import Orders, Catalog, Payment_type, Receiving_type, Client_type, Goods


admin.site.register(Catalog)
admin.site.register(Payment_type)
admin.site.register(Receiving_type)
admin.site.register(Client_type)
admin.site.register(Goods)
admin.site.register(Orders)