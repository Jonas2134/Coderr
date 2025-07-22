from rest_framework import serializers

from offers_app.models import Offer, OfferDetail


class OfferFilterdSerializer(serializers.ModelSerializer):
    pass


class NestedDetailSerializer(serializers.ModelSerializer):
    offer_type = serializers.ChoiceField(choices=OfferDetail.OFFER_TYPE_CHOICES, required=True)

    class Meta:
        model = OfferDetail
        fields = ('id', 'title', 'revisions', 'delivery_time_in_days', 'price', 'features', 'offer_type')
        read_only_fields = ('id')


class OfferSerializer(serializers.ModelSerializer):
    details = NestedDetailSerializer(many=True)

    class Meta:
        model = Offer
        fields = ('id', 'title', 'image', 'description', 'details')
        read_only_fields = ('id')
