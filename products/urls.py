from django.urls import path
from .views import product_list, product_detail, index

urlpatterns = [
    path('', index, name='index'),
    path('shop/', product_list, name='product_list'),
    path('<int:pk>/', product_detail, name='product_detail'),
]
