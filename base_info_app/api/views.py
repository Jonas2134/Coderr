from django.contrib.auth import get_user_model
from django.db.models import Avg, Count
from rest_framework.generics import GenericAPIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny

from .serializers import BaseInfoSerializer
from reviews_app.models import Review
from offers_app.models import Offer


class GetBaseInfoView(GenericAPIView):
    serializer_class = BaseInfoSerializer
    permission_classes = [AllowAny]

    def get(self, request, *args, **kwargs):
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
