from django.db.models import Q
from django.contrib.auth import get_user_model
from rest_framework import generics, status, mixins
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.response import Response
from rest_framework.exceptions import NotFound

from .serializers import OrderSerializer, OrderCreateSerializer, OrderPatchSerializer, OrderCountSerializer, CompletedOrderCountSerializer
from .permissions import IsUserBusinessOwner
from orders_app.models import Order
from core.permissions import IsBusinessUser, IsCustomerUser
from core.decorators import handle_exceptions


class OrdersGetPostView(generics.ListCreateAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = OrderSerializer

    def get_permissions(self):
        if self.request.method == 'POST':
            return [IsAuthenticated(), IsCustomerUser()]
        return super().get_permissions()

    def get_queryset(self):
        user = self.request.user
        return Order.objects.filter(Q(customer_user=user) | Q(business_user=user))

    @handle_exceptions(action='retrieving orders')
    def get(self, request, *args, **kwargs):
        qs = self.get_queryset()
        serializer = self.get_serializer(qs, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @handle_exceptions(action='creating order')
    def create(self, request, *args, **kwargs):
        serializer = OrderCreateSerializer(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        order = serializer.save()
        output_serializer = self.get_serializer(order)
        return Response(output_serializer.data, status=status.HTTP_201_CREATED)


class OrderPatchDeleteView(
    mixins.UpdateModelMixin,
    mixins.DestroyModelMixin,
    generics.GenericAPIView
):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer

    def get_permissions(self):
        if self.request.method == 'PATCH':
            return [IsAuthenticated(), IsBusinessUser(), IsUserBusinessOwner()]
        if self.request.method == 'DELETE':
            return [IsAdminUser()]
        return super().get_permissions()

    def get_object(self):
        order_id = self.kwargs.get('pk')
        try:
            order = Order.objects.get(pk=order_id)
        except Order.DoesNotExist:
            raise NotFound('Order not found')
        return order

    @handle_exceptions(action='updating order')
    def patch(self, request, *args, **kwargs):
        return super().partial_update(request, *args, **kwargs)

    @handle_exceptions(action='updating order')
    def partial_update(self, request, *args, **kwargs):
        order = self.get_object()
        serializer = OrderPatchSerializer(order, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        output_serializer = self.get_serializer(order, context={'request': request})
        return Response(output_serializer.data, status=status.HTTP_200_OK)
    
    @handle_exceptions(action='deleting order')
    def delete(self, request, *args, **kwargs):
        return super().destroy(request, *args, **kwargs)


class BaseOrderCountView(generics.RetrieveAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = None
    order_filter_kwargs = {}
    count_field_name = ''

    def get_object(self):
        business_user_id = self.kwargs.get('pk')
        try:
            user = get_user_model().objects.get(pk=business_user_id)
        except get_user_model().DoesNotExist:
            raise NotFound('Business user not found')
        if user.type != 'business':
            raise NotFound('User is not a business user')
        return user
    
    @handle_exceptions(action='retrieving order count')
    def retrieve(self, request, *args, **kwargs):
        user = self.get_object()
        count = Order.objects.filter(business_user=user, **self.order_filter_kwargs).count()
        serializer = self.get_serializer({self.count_field_name: count})
        return Response(serializer.data, status=status.HTTP_200_OK)


class OrderCountView(BaseOrderCountView):
    serializer_class = OrderCountSerializer
    order_filter_kwargs = {}
    count_field_name = 'order_count'
 

class CompletedOrderCountView(BaseOrderCountView):
    serializer_class = CompletedOrderCountSerializer
    order_filter_kwargs = {'status': 'completed'}
    count_field_name = 'completed_order_count'
