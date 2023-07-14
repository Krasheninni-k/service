from django.urls import path

from app import views

app_name = 'app'

urlpatterns = [
     path('', views.index,
          name='index'),
     # Закупки
     path('app/add_order/', views.add_order,
          name='add_order'),
     path('app/add_order_detail/', views.add_order_detail,
          name='add_order_detail'),
     path('app/orders/', views.orders_list,
          name='orders_list'),
     path('app/orders/<int:pk>/', views.order_detail,
          name='order_detail'),
     path('app/orders/<int:pk>/delete/', views.delete_order,
          name='delete_order'),
     path('app/orders/<int:pk>/edit/', views.edit_order,
          name='edit_order'),
     path('app/orders/<int:order_number>/edit/<int:pk>', views.edit_order_detail,
          name='edit_order_detail'),
     path('app/orders/<int:pk>/received/', views.received_order,
          name='order_received'),
     # Товары, Остатки
     path('app/goods/', views.goods_list,
          name='goods_list'),
     path('app/goods/stock', views.stock_list,
          name='stock_list'),
     # Каталог
     path('app/goods/catalog/', views.catalog,
          name='catalog'),
     path('app/goods/catalog/<int:pk>/', views.catalog_detail,
          name='catalog_detail'),
     path('app/goods/catalog/add/', views.catalog_add,
          name='catalog_add'),     
     path('app/goods/catalog/<int:pk>/edit/', views.catalog_edit,
          name='catalog_edit'),
     path('app/goods/catalog/<int:pk>/delete/', views.catalog_delete,
          name='catalog_delete'),
     # Продажи
     path('app/sale_add/', views.sale_add,
          name='sale_add'),
     path('app/sale_detail_add/', views.sale_detail_add,
          name='sale_detail_add'),
     path('app/sales/', views.sales_list,
          name='sales_list'),
     path('app/sales/<int:pk>/', views.sale_detail,
          name='sale_detail'),
     path('app/sales/<int:pk>/delete/', views.sale_delete,
          name='sale_delete'),
     path('app/sales/<int:pk>/edit/', views.sale_edit,
          name='sale_edit'),
     path('app/sales/<int:sale_number>/edit/<int:pk>', views.sale_detail_edit,
          name='sale_detail_edit'),
     # Пользователи
     path('profile/<slug:username>/', views.UserDetailView.as_view(),
          name='profile'),
     path('profile/<slug:username>/edit_profile/',
         views.UserUpdateView.as_view(), name='edit_profile'),
     # Пользовательские настройки
     path('app/settings_edit/',
          views.settings_edit, name='settings_edit'),
     path('app/import/orders/', views.import_orders_data, name='import_orders_data'),
     path('app/import/sales/', views.import_sales_data, name='import_sales_data'),
]
