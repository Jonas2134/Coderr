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
    """
    API endpoint to list all orders related to the current user and to create new orders.

    - GET: Returns all orders where the user is either the customer or the business.
    - POST: Allows authenticated customer users to create a new order.

    Attributes:
        permission_classes (list): Default [IsAuthenticated]; POST adds IsCustomerUser.
        serializer_class (Serializer): OrderSerializer for listing and response.
    """
    permission_classes = [IsAuthenticated]
    serializer_class = OrderSerializer

    def get_permissions(self):
        """
        Return additional permissions for POST.

        - POST: user must be authenticated and of type 'customer'.
        """
        if self.request.method == 'POST':
            return [IsAuthenticated(), IsCustomerUser()]
        return super().get_permissions()

    def get_queryset(self):
        """
        Retrieve orders where the current user is either customer or business.

        Returns:
            QuerySet: Filtered Order queryset.
        """
        user = self.request.user
        return Order.objects.filter(Q(customer_user=user) | Q(business_user=user))

    @handle_exceptions(action='retrieving orders')
    def get(self, request, *args, **kwargs):
        """
        Handle GET: Serialize and return all related orders.

        Returns:
            Response: HTTP 200 with list of orders.
        """
        qs = self.get_queryset()
        serializer = self.get_serializer(qs, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @handle_exceptions(action='creating order')
    def create(self, request, *args, **kwargs):
        """
        Handle POST: Validate and create a new order.

        Uses OrderCreateSerializer to enforce business logic, then responds
        with the full Order representation.
        """
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
    """
    API endpoint to update (PATCH) or delete an existing order.

    - PATCH: Allows the business owner of the order to change its status.
    - DELETE: Allows admin users to remove an order entirely.

    Attributes:
        queryset (QuerySet): Base Order queryset.
        serializer_class (Serializer): OrderSerializer for response.
    """
    queryset = Order.objects.all()
    serializer_class = OrderSerializer

    def get_permissions(self):
        """
        Return permissions based on HTTP method:

        - PATCH: Authenticated business user who owns the order.
        - DELETE: Admin users only.
        """
        if self.request.method == 'PATCH':
            return [IsAuthenticated(), IsBusinessUser(), IsUserBusinessOwner()]
        if self.request.method == 'DELETE':
            return [IsAdminUser()]
        return super().get_permissions()

    def get_object(self):
        """
        Retrieve the Order instance by pk or raise 404.

        Returns:
            Order: The requested order.
        """
        order_id = self.kwargs.get('pk')
        try:
            order = Order.objects.get(pk=order_id)
        except Order.DoesNotExist:
            raise NotFound('Order not found')
        return order

    @handle_exceptions(action='updating order')
    def patch(self, request, *args, **kwargs):
        """
        Handle PATCH: Delegate to partial_update.
        """
        return super().partial_update(request, *args, **kwargs)

    @handle_exceptions(action='updating order')
    def partial_update(self, request, *args, **kwargs):
        """
        Handle partial update of order status.

        Validates status field via OrderPatchSerializer, updates the order,
        and returns the updated representation.
        """
        order = self.get_object()
        serializer = OrderPatchSerializer(order, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        output_serializer = self.get_serializer(order, context={'request': request})
        return Response(output_serializer.data, status=status.HTTP_200_OK)

    @handle_exceptions(action='deleting order')
    def delete(self, request, *args, **kwargs):
        """
        Handle DELETE: Remove the order instance.
        """
        return super().destroy(request, *args, **kwargs)


class BaseOrderCountView(generics.RetrieveAPIView):
    """
    Base endpoint for retrieving count-based aggregates for a business user.

    Subclasses must define:
        serializer_class: Serializer to format the count field.
        order_filter_kwargs: Filters to apply on Order queryset.
        count_field_name: Key under which the count is returned.

    Attributes:
        permission_classes (list): [IsAuthenticated].
    """
    permission_classes = [IsAuthenticated]
    serializer_class = None
    order_filter_kwargs = {}
    count_field_name = ''

    def get_object(self):
        """
        Retrieve and validate the business user by pk.

        Raises 404 if user not found or not of type 'business'.
        """
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
        """
        Compute the filtered order count and return it serialized.

        Returns:
            Response: HTTP 200 with {count_field_name: count}.
        """
        user = self.get_object()
        count = Order.objects.filter(business_user=user, **self.order_filter_kwargs).count()
        serializer = self.get_serializer({self.count_field_name: count})
        return Response(serializer.data, status=status.HTTP_200_OK)


class OrderCountView(BaseOrderCountView):
    """
    Endpoint to retrieve the total order count for a business user.

    Inherits BaseOrderCountView with no additional filters.
    """
    serializer_class = OrderCountSerializer
    order_filter_kwargs = {}
    count_field_name = 'order_count'


class CompletedOrderCountView(BaseOrderCountView):
    """
    Endpoint to retrieve the count of completed orders for a business user.

    Inherits BaseOrderCountView with filter status='completed'.
    """
    serializer_class = CompletedOrderCountSerializer
    order_filter_kwargs = {'status': 'completed'}
    count_field_name = 'completed_order_count'
