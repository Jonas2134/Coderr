from rest_framework import serializers

from offers_app.models import Offer, OfferDetail
from django.contrib.auth import get_user_model


class NestedUserDetailsSerializer(serializers.ModelSerializer):
    class Meta:
        model = get_user_model()
        fields = ('first_name', 'last_name', 'username')
        read_only_fields = fields


class NestedDetailHyperlinkedSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField()
    url = serializers.HyperlinkedIdentityField(
        view_name='offerdetails-detail',
        lookup_field='pk',
        lookup_url_kwarg='pk'
    )

    class Meta:
        model = OfferDetail
        fields = ('id', 'url')
        read_only_fields = ('id', 'url')


class NestedOfferResultSerializer(serializers.ModelSerializer):
    user = serializers.IntegerField(source='creator.id', read_only=True)
    details = NestedDetailHyperlinkedSerializer(many=True, read_only=True)
    min_price = serializers.SerializerMethodField()
    min_delivery_time = serializers.SerializerMethodField()

    class Meta:
        model = Offer
        fields = (
            'id', 'user', 'title', 'image', 'description', 'created_at', 'updated_at',
            'details', 'min_price', 'min_delivery_time'
        )
        read_only_fields = fields
    
    def get_min_price(self, obj):
        prices = [detail.price for detail in obj.details.all()]
        return min(prices) if prices else None

    def get_min_delivery_time(self, obj):
        times = [detail.delivery_time_in_days for detail in obj.details.all()]
        return min(times) if times else None


class NestedDetailSerializer(serializers.ModelSerializer):
    offer_type = serializers.ChoiceField(choices=OfferDetail.OFFER_TYPE_CHOICES, required=True)

    class Meta:
        model = OfferDetail
        fields = ('id', 'title', 'revisions', 'delivery_time_in_days', 'price', 'features', 'offer_type')
        read_only_fields = ('id',)


class OfferResultSerializer(NestedOfferResultSerializer):
    user_details = NestedUserDetailsSerializer(source='creator', read_only=True)

    class Meta(NestedOfferResultSerializer.Meta):
        fields = NestedOfferResultSerializer.Meta.fields + ('user_details',)
        read_only_fields = NestedOfferResultSerializer.Meta.read_only_fields + ('user_details',)


class OfferSerializer(serializers.ModelSerializer):
    details = NestedDetailSerializer(many=True)

    class Meta:
        model = Offer
        fields = ('id', 'title', 'image', 'description', 'details')
        read_only_fields = ('id',)
    
    def validate_details(self, value):
        types = {d.get('offer_type') for d in value}
        required = {OfferDetail.BASIC, OfferDetail.STANDARD, OfferDetail.PREMIUM}
        if types != required:
            raise serializers.ValidationError('An Offer must have exactly one basic, one standard, and one premium detail.')
        return value
