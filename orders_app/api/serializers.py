from rest_framework import serializers
from rest_framework.exceptions import NotFound
from rest_framework.fields import empty

from orders_app.models import Order
from offers_app.models import OfferDetail


class OfferDetailRelatedField(serializers.PrimaryKeyRelatedField):
    default_error_messages = {
        'required': 'This field is required.',
        'does_not_exist': 'The offer detail does not exist.',
        'incorrect_type': 'Invalid type. An integer is expected.'
    }

    def run_validation(self, data=empty):
        if data is empty:
            self.fail('required')
        try:
            return super().run_validation(data)
        except serializers.ValidationError as e:
            codes = e.get_codes()

            def has_dne(c):
                if isinstance(c, (list, tuple)):
                    return any(has_dne(x) for x in c)
                if isinstance(c, dict):
                    return any(has_dne(v) for v in c.values())
                return c == 'does_not_exist'

            if has_dne(codes):
                raise NotFound(self.error_messages['does_not_exist'])
            raise


class OrderCreateSerializer(serializers.Serializer):
    offer_detail_id = OfferDetailRelatedField(
        queryset=OfferDetail.objects.all(),
        source='offer_detail'
    )

    def create(self, validated_data):
        offer_detail = validated_data['offer_detail']
        customer = self.context['request'].user
        business = offer_detail.offer.creator
        return Order.objects.create(
            offer_detail=offer_detail,
            customer_user=customer,
            business_user=business
        )


class OrderPatchSerializer(serializers.Serializer):
    status = serializers.ChoiceField(
        choices=Order.ORDER_STATUS_CHOICES,
        required=True
    )


class OrderSerializer(serializers.ModelSerializer):
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
    order_count = serializers.IntegerField(read_only=True)


class CompletedOrderCountSerializer(serializers.Serializer):
    completed_order_count = serializers.IntegerField(read_only=True)
