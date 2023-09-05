from django.urls import path

from app import views

app_name = 'app'

urlpatterns = [
     path('', views.index, name='index'),
     # Закупки
     path('order_add/', views.order_add,
          name='order_add'),
     path('order_detail_add/', views.order_detail_add,
          name='order_detail_add'),
     path('orders/', views.orders_list,
          name='orders_list'),
     path('orders/<int:pk>/', views.order_detail,
          name='order_detail'),
     path('orders/<int:pk>/delete/', views.order_delete,
          name='order_delete'),
     path('orders/<int:pk>/edit/', views.order_edit,
          name='order_edit'),
     path('orders/<int:order_number>/edit/<int:pk>', views.order_detail_edit,
          name='order_detail_edit'),
     path('orders/<int:pk>/received/', views.order_received,
          name='order_received'),
     # Товары, Остатки
     path('goods/', views.goods_list,
          name='goods_list'),
     path('goods/stock', views.stock_list,
          name='stock_list'),
     # Каталог
     path('goods/catalog/', views.catalog,
          name='catalog'),
     path('goods/catalog/<int:pk>/', views.catalog_detail,
          name='catalog_detail'),
     path('goods/catalog/add/', views.catalog_add,
          name='catalog_add'),     
     path('goods/catalog/<int:pk>/edit/', views.catalog_edit,
          name='catalog_edit'),
     path('goods/catalog/<int:pk>/delete/', views.catalog_delete,
          name='catalog_delete'),
     # Продажи
     path('sale_add/', views.sale_add,
          name='sale_add'),
     path('sale_detail_add/', views.sale_detail_add,
          name='sale_detail_add'),
     path('sales/', views.sales_list,
          name='sales_list'),
     path('sales/<int:pk>/', views.sale_detail,
          name='sale_detail'),
     path('sales/<int:pk>/delete/', views.sale_delete,
          name='sale_delete'),
     path('sales/<int:pk>/edit/', views.sale_edit,
          name='sale_edit'),
     path('sales/<int:sale_number>/edit/<int:pk>', views.sale_detail_edit,
          name='sale_detail_edit'),
     # Пользовательские настройки
     path('settings_edit/',
          views.settings_edit, name='settings_edit'),
     path('import/orders/', views.import_orders_data, name='import_orders_data'),
     path('import/sales/', views.import_sales_data, name='import_sales_data'),
     path('import/catalog/', views.import_catalog_data, name='import_catalog_data'),
     # Дашборд
     path('dashboard/', views.dashboard, name='dashboard'),
]
