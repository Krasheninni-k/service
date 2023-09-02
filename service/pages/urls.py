from django.urls import path
from django.views.generic import TemplateView

app_name = 'pages'

urlpatterns = [
     path('about/', TemplateView.as_view(template_name='pages/about.html'),
         name='about'),
     path('faq/', TemplateView.as_view(template_name='pages/faq.html'),
         name='faq'),
]
