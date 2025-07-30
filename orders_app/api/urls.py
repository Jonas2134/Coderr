from django.urls import path

from .views import OrdersGetPostView

urlpatterns = [
    path('orders/', OrdersGetPostView.as_view(), name='orders-list-create'),
]
