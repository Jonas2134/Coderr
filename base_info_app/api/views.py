from django.contrib.auth import get_user_model
from django.db.models import Avg, Count
from rest_framework.generics import GenericAPIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny

from .serializers import BaseInfoSerializer
from reviews_app.models import Review
from offers_app.models import Offer


class GetBaseInfoView(GenericAPIView):
    """
    API endpoint to retrieve aggregated base statistics for the application.

    Provides counts of reviews, average review rating, number of business profiles,
    and total offers. Accessible without authentication.

    Attributes:
        serializer_class (Serializer): BaseInfoSerializer for output formatting.
        permission_classes (list): [AllowAny] to allow unrestricted access.
    """
    serializer_class = BaseInfoSerializer
    permission_classes = [AllowAny]

    def get(self, request, *args, **kwargs):
        """
        Handle GET requests to fetch base statistics.

        1. Aggregate review count and average rating from Review model.
        2. Count business users via CustomUser model's `type='business'`.
        3. Count total Offer instances.
        4. Round average rating to one decimal place (default to 0 if no reviews).
        5. Serialize and return the aggregated data.

        Returns:
            rest_framework.response.Response: A Response containing:
                - review_count (int): Total number of reviews.
                - average_rating (float): Average rating rounded to one decimal.
                - business_profile_count (int): Number of business users.
                - offer_count (int): Total number of offers.
        """
        review_stats = Review.objects.aggregate(review_count=Count('pk'), average_rating=Avg('rating'))
        business_count = get_user_model().objects.filter(type='business').count()
        offer_count = Offer.objects.count()
        avg = review_stats.get('average_rating') or 0
        rounded_avg = round(float(avg), 1)
        payload = {
            'review_count': review_stats.get('review_count') or 0,
            'average_rating': rounded_avg,
            'business_profile_count': business_count,
            'offer_count': offer_count,
        }
        serializer = self.get_serializer(payload)
        return Response(serializer.data)
