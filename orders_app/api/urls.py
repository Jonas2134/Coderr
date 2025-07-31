from django.urls import path

from .views import OrdersGetPostView, OrderPatchDeleteView, OrderCountView, CompletedOrderCountView

urlpatterns = [
    path('orders/', OrdersGetPostView.as_view(), name='orders-list-create'),
    path('orders/<int:pk>/', OrderPatchDeleteView.as_view(), name='orders-update-delete'),
    path('order-count/<int:pk>/', OrderCountView.as_view(), name='orders-count'),
    path('completed-order-count/<int:pk>/', CompletedOrderCountView.as_view(), name='completed-orders-count'),
]
