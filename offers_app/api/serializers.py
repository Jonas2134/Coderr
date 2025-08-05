from decimal import Decimal

from django.contrib.auth import get_user_model
from rest_framework import serializers

from offers_app.models import Offer, OfferDetail


class NestedUserDetailsSerializer(serializers.ModelSerializer):
    """
    Serializer for embedding basic creator information in nested representations.

    Fields:
        first_name (str): The user’s first name (read-only).
        last_name (str): The user’s last name (read-only).
        username (str): The user’s username (read-only).
    """
    class Meta:
        model = get_user_model()
        fields = ('first_name', 'last_name', 'username')
        read_only_fields = fields


class NestedDetailHyperlinkedSerializer(serializers.ModelSerializer):
    """
    Serializer for embedding hyperlinked OfferDetail references.

    Provides an `id` and a URL to the detail endpoint.

    Fields:
        id (int): Primary key of the OfferDetail instance.
        url (str): Hyperlink to the OfferDetail detail view.
    """
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
    """
    Serializer for nested read-only representation of an Offer.

    Includes foreign-key reference to the creator, a list of hyperlinked details,
    and computed fields for minimum price and delivery time.

    Fields:
        id (int): Offer primary key.
        user (int): ID of the creator user.
        title (str): Offer title.
        image (URL): URL to the offer image.
        description (str): Offer description text.
        created_at (datetime): Creation timestamp.
        updated_at (datetime): Last update timestamp.
        details (list): List of hyperlinked OfferDetail resources.
        min_price (float): Lowest price among associated details.
        min_delivery_time (int): Shortest delivery time among associated details.
    """
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
        """
        Compute the minimum price among the offer’s detail variants.

        Args:
            obj (Offer): The Offer instance.

        Returns:
            float or None: The lowest detail.price, or None if no details.
        """
        request = self.context.get('request')
        param = request.query_params.get('min_price')
        if param is None:
            prices = [detail.price for detail in obj.details.all()]
            return min(prices) if prices else None
        try:
            threshold = Decimal(param)
        except (TypeError, ValueError):
            prices = [detail.price for detail in obj.details.all()]
            return min(prices) if prices else None
        matching = [detail.price for detail in obj.details.all() if detail.price >= threshold]
        return min(matching) if matching else None

    def get_min_delivery_time(self, obj):
        """
        Compute the minimum delivery time among the offer’s detail variants.

        Args:
            obj (Offer): The Offer instance.

        Returns:
            int or None: The shortest detail.delivery_time_in_days, or None if no details.
        """
        request = self.context.get('request')
        param = request.query_params.get('max_delivery_time')
        if param is None:
            times = [detail.delivery_time_in_days for detail in obj.details.all()]
            return min(times) if times else None
        try:
            threshold = int(param)
        except (TypeError, ValueError):
            times = [detail.delivery_time_in_days for detail in obj.details.all()]
            return min(times) if times else None
        matching = [detail.delivery_time_in_days for detail in obj.details.all() if detail.delivery_time_in_days <= threshold]
        return max(matching) if matching else None


class NestedDetailSerializer(serializers.ModelSerializer):
    """
    Serializer for nested create/update of OfferDetail variants.

    Fields:
        id (int): Detail primary key (read-only).
        title (str): Title of this detail variant.
        revisions (int): Number of revisions included.
        delivery_time_in_days (int): Delivery time in days.
        price (decimal): Price for this variant.
        features (list): List of feature descriptions.
        offer_type (str): One of the OFFER_TYPE_CHOICES values.
    """
    offer_type = serializers.ChoiceField(choices=OfferDetail.OFFER_TYPE_CHOICES, required=True)

    class Meta:
        model = OfferDetail
        fields = ('id', 'title', 'revisions', 'delivery_time_in_days', 'price', 'features', 'offer_type')
        read_only_fields = ('id',)


class OfferResultSerializer(NestedOfferResultSerializer):
    """
    Extended read-only serializer for an Offer including nested user details.

    Inherits all fields from NestedOfferResultSerializer and adds:
        user_details (object): Embedded NestedUserDetailsSerializer of creator.
    """
    user_details = NestedUserDetailsSerializer(source='creator', read_only=True)

    class Meta(NestedOfferResultSerializer.Meta):
        fields = NestedOfferResultSerializer.Meta.fields + ('user_details',)
        read_only_fields = NestedOfferResultSerializer.Meta.read_only_fields + ('user_details',)


class OfferSerializer(serializers.ModelSerializer):
    """
    Serializer for creating and updating Offer instances with nested details.

    Fields:
        id (int): Offer primary key (read-only).
        title (str): Title of the offer.
        image (URL): Image URL for the offer.
        description (str): Description text.
        details (list): List of nested detail objects (Basic, Standard, Premium).
    """
    details = NestedDetailSerializer(many=True)

    class Meta:
        model = Offer
        fields = ('id', 'title', 'image', 'description', 'details')
        read_only_fields = ('id',)

    def validate_details(self, value):
        """
        Ensure exactly one detail of each required offer_type is provided on create.

        Args:
            value (list): List of detail data dicts.

        Raises:
            serializers.ValidationError: If missing or duplicate types.
        """
        if getattr(self, 'partial', False):
            return value
        types = {d.get('offer_type') for d in value}
        required = {OfferDetail.BASIC, OfferDetail.STANDARD, OfferDetail.PREMIUM}
        if types != required:
            raise serializers.ValidationError('An Offer must have exactly one basic, one standard, and one premium detail.')
        return value

    def update(self, instance, validated_data):
        """
        Update Offer fields and nested details.

        Args:
            instance (Offer): The Offer to update.
            validated_data (dict): Validated data including optional 'details'.

        Returns:
            Offer: The updated Offer instance.

        Raises:
            serializers.ValidationError: If detail variant not found.
        """
        details_data = validated_data.pop('details', None)
        for attr, val in validated_data.items():
            setattr(instance, attr, val)
        instance.save()
        if details_data is not None:
            for detail in details_data:
                try:
                    offer_type = detail['offer_type']
                    obj = instance.details.get(offer_type=offer_type)
                except KeyError:
                    raise serializers.ValidationError({'details': 'No detail found with offer_type.'})
                except OfferDetail.DoesNotExist:
                    raise serializers.ValidationError({'details': 'No detail found with offer_type.'})
                for key, val in detail.items():
                    setattr(obj, key, val)
                obj.save()
        return instance
