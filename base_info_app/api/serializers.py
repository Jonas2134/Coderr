from rest_framework import serializers

class BaseInfoSerializer(serializers.Serializer):
    """
    Serializer for the application’s base statistics endpoint.

    Outputs aggregated counts and averages for reviews, business profiles, and offers.

    Fields:
        review_count (int): Total number of reviews in the system.
        average_rating (float): Average review rating, rounded to one decimal.
        business_profile_count (int): Total number of users with `type='business'`.
        offer_count (int): Total number of offers available.
    """
    review_count = serializers.IntegerField(read_only=True)
    average_rating = serializers.FloatField(read_only=True)
    business_profile_count = serializers.IntegerField(read_only=True)
    offer_count = serializers.IntegerField(read_only=True)
