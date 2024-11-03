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
     path('orders/<int:pk>/change_received', views.order_change_received,
          name='order_change_received'),
     path('orders/<int:pk>/reset_received_date', views.order_reset_received_date,
          name='order_reset_received_date'),
     path('orders/<int:pk>/accept_all', views.order_accept_all,
          name='order_accept_all'),
     path('orders/<int:pk>/received_date', views.order_received_date,
           name='order_received_date'),
     path('orders/<int:pk>/begin_scan', views.order_begin_scan,
           name='order_begin_scan'),
     path('orders/<int:pk>/end_scan', views.order_end_scan,
           name='order_end_scan'),
           
     # Товары, Остатки
     path('goods/', views.goods_list,
          name='goods_list'),
     path('goods/stock', views.stock_list,
          name='stock_list'),
     path('sales/selected_good/<int:pk>/', views.selected_good,
          name='selected_good'),
     path('goods/edit/<int:pk>', views.good_detail_edit,
          name='good_detail_edit'),
     path('goods/defect', views.defect_goods,
          name='defect_goods'),
     path('goods/problem', views.problem_goods,
          name='problem_goods'),

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
     path('sales/<int:pk>/edit_detail/', views.sale_detail_edit,
          name='sale_detail_edit'),
     path('sales/<int:pk>/change_cash/', views.sale_change_cash,
          name='sale_change_cash'),
     path('sales/begin_scan', views.sale_begin_scan,
          name='sale_begin_scan'),
     path('sales/end_scan', views.sale_end_scan,
          name='sale_end_scan'),
     path('sales/select_good/', views.select_good,
          name='select_good'),
     path('sales/selected_good_stock/<int:pk>/', views.selected_good_stock,
          name='selected_good_stock'),
     path('sales/<int:pk>/change_sold', views.sale_change_sold,
          name='sale_change_sold'),
     path('sales/busket', views.sale_busket,
          name='sale_busket'),

     # Пользовательские настройки
     path('settings_edit/',
          views.settings_edit, name='settings_edit'),
     path('import/orders/', views.import_orders_data, name='import_orders_data'),
     path('import/sales/', views.import_sales_data, name='import_sales_data'),
     path('import/catalog/', views.import_catalog_data, name='import_catalog_data'),

     # Дашборд
     path('dashboard/', views.dashboard, name='dashboard'),

     # API для сканирования s/n номеров
     # curl -X POST http://127.0.0.1:8000/app/scan/ -H "Content-Type: application/json" -d '{"code": 111}'
     # curl -X POST http://djirobots.pythonanywhere.com/app/scan/ -H "Content-Type: application/json" -d '{"code": 111}'
     path('scan/', views.ScanAPIView.as_view(), name='scan')
]
