from django.urls import path
from .views import cart_detail, cart_add, cart_remove, checkout, order_success, update_cart, cart_summary

urlpatterns = [
    path('', cart_detail, name='cart_detail'),
    path('add/<int:product_id>/', cart_add, name='cart_add'),
    path('summary/', cart_summary, name='cart_summary'),  # ✅ Add summary URL
    path('remove/<int:product_id>/', cart_remove, name='cart_remove'),
    path('checkout/', checkout, name='checkout'),
    path('update/<int:product_id>/<str:action>/', update_cart, name='update_cart'),
    path('order-success/', order_success, name='order_success'),
]