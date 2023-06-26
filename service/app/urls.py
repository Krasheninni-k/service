from django.urls import path

from app import views

app_name = 'app'

urlpatterns = [
     path('', views.index,
         name='index'),
     path('app/add_order/', views.add_order,
         name='add_order'),      
     path('app/add_order/detail', views.add_order_detail,
         name='add_order_detail'),    
     path('app/orders/', views.order_list,
         name='order_list'),       
     path('profile/<slug:username>/', views.UserDetailView.as_view(),
         name='profile'),]
         

"""
    path('profile/<slug:username>/edit_profile',
         views.UserUpdateView.as_view(), name='edit_profile'),
    path('posts/create/', views.PostCreateView.as_view(),
         name='create_post'),
    path('posts/<int:pk>/', views.post_detail,
         name='post_detail'),
    path('posts/<int:pk>/edit/', views.PostUpdateView.as_view(),
         name='edit_post'),
    path('posts/<int:pk>/delete/', views.PostDeleteView.as_view(),
         name='delete_post'),
    path('posts/<int:pk>/comment/', views.add_comment,
         name='add_comment'),
    path('posts/<int:post_id>/edit_comment/<int:pk>/',
         views.CommentUpdateView.as_view(),
         name='edit_comment'),
    path('posts/<int:post_id>/delete_comment/<int:pk>/',
         views.CommentDeleteView.as_view(),
         name='delete_comment'),
    path('category/<slug:category_slug>/', views.category_posts,
         name='category_posts'),
]
"""