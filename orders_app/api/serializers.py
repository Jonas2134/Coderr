from rest_framework import serializers
from rest_framework.exceptions import NotFound
from rest_framework.fields import empty

from orders_app.models import Order
from offers_app.models import OfferDetail


class OfferDetailRelatedField(serializers.PrimaryKeyRelatedField):
    """
    Custom related-field that maps a primary-key value to an OfferDetail instance,
    with tailored error messages for required, non-existent, or invalid IDs.

    Inherits:
        serializers.PrimaryKeyRelatedField

    Overrides:
        run_validation(data) -> OfferDetail:
            - Raises NotFound if the PK doesn’t correspond to an existing OfferDetail.
    """
    default_error_messages = {
        'required': 'This field is required.',
        'does_not_exist': 'The offer detail does not exist.',
        'incorrect_type': 'Invalid type. An integer is expected.'
    }

    def run_validation(self, data=empty):
        """
        Validate the incoming PK and return the corresponding OfferDetail.

        Args:
            data: The raw input value from the client.

        Returns:
            OfferDetail: The matching model instance.

        Raises:
            NotFound: If no OfferDetail matches the provided ID.
            serializers.ValidationError: For other validation issues.
        """
        if data is empty:
            self.fail('required')
        try:
            return super().run_validation(data)
        except serializers.ValidationError as e:
            codes = e.get_codes()
            if self._has_dne(codes):
                raise NotFound(self.error_messages['does_not_exist'])
            raise

    def _has_dne(self, c):
        """Recursively search validation codes for 'does_not_exist'."""
        if isinstance(c, (list, tuple)):
            return any(self._has_dne(x) for x in c)
        if isinstance(c, dict):
            return any(self._has_dne(v) for v in c.values())
        return c == 'does_not_exist'


class OrderCreateSerializer(serializers.Serializer):
    """
    Serializer for creating new Order instances.

    Fields:
        offer_detail_id (int): Primary key of the OfferDetail to order; 
            mapped to `offer_detail` in `create()`.
    """
    offer_detail_id = OfferDetailRelatedField(
        queryset=OfferDetail.objects.all(),
        source='offer_detail'
    )

    def create(self, validated_data):
        """
        Create an Order linking customer and business users.

        Uses:
            - `offer_detail` from validated_data
            - `request.user` as `customer_user`
            - `offer_detail.offer.creator` as `business_user`

        Returns:
            Order: The newly created order instance.
        """
        offer_detail = validated_data['offer_detail']
        customer = self.context['request'].user
        business = offer_detail.offer.creator
        return Order.objects.create(
            offer_detail=offer_detail,
            customer_user=customer,
            business_user=business
        )


class OrderPatchSerializer(serializers.Serializer):
    """
    Serializer for patch-updating Order status.

    Fields:
        status (str): New status for the order; must be one of Order.ORDER_STATUS_CHOICES.
    """
    status = serializers.ChoiceField(
        choices=Order.ORDER_STATUS_CHOICES,
        required=True
    )


class OrderSerializer(serializers.ModelSerializer):
    """
    Full read/write serializer for Order instances, embedding related OfferDetail fields.

    Read-only fields sourced from the related OfferDetail:
        - title
        - revisions
        - delivery_time_in_days
        - price
        - features
        - offer_type

    Writable fields:
        - status
    """
    title = serializers.ReadOnlyField(source='offer_detail.title')
    revisions = serializers.ReadOnlyField(source='offer_detail.revisions')
    delivery_time_in_days = serializers.ReadOnlyField(source='offer_detail.delivery_time_in_days')
    price = serializers.ReadOnlyField(source='offer_detail.price')
    features = serializers.JSONField(source='offer_detail.features', read_only=True)
    offer_type = serializers.ReadOnlyField(source='offer_detail.offer_type')

    class Meta:
        model = Order
        fields = (
            'id',
            'customer_user',
            'business_user',
            'title',
            'revisions',
            'delivery_time_in_days',
            'price',
            'features',
            'offer_type',
            'status',
            'created_at',
            'updated_at'
        )
        read_only_fields = ('id', 'customer_user', 'business_user', 'created_at', 'updated_at')


class OrderCountSerializer(serializers.Serializer):
    """
    Serializer for representing total order count in aggregate endpoints.

    Fields:
        order_count (int): Total number of orders.
    """
    order_count = serializers.IntegerField(read_only=True)


class CompletedOrderCountSerializer(serializers.Serializer):
    """
    Serializer for representing total completed order count in aggregate endpoints.

    Fields:
        completed_order_count (int): Number of orders with status 'completed'.
    """
    completed_order_count = serializers.IntegerField(read_only=True)
