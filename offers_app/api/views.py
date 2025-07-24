from django.db import transaction
from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework.exceptions import NotFound, PermissionDenied, ValidationError
from rest_framework.pagination import PageNumberPagination

from .serilaizers import OfferSerializer, OfferFilterdSerializer
from .permissions import IsBusinessUser
from offers_app.models import Offer, OfferDetail
from core.decorators import handle_exceptions


class OffersGetPostView(generics.ListCreateAPIView):
    queryset = Offer.objects.all()
    pagination_class = PageNumberPagination
    permission_classes = [AllowAny]

    def get_permissions(self):
        if self.request.method in ['POST']:
            return [IsAuthenticated(), IsBusinessUser()]
        return super().get_permissions()
    
    def get_serializer_class(self):
        if self.request.method == 'POST':
            return OfferSerializer
        return OfferFilterdSerializer
    
    @handle_exceptions(action='retrieving offers')
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

    @handle_exceptions(action='creating offer')
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        details_data = serializer.validated_data.pop('details')
        data = serializer.validated_data

        with transaction.atomic():
            offer = Offer.objects.create(creator=request.user, **data)
            for detail in details_data:
                OfferDetail.objects.create(offer=offer, **detail)
            offer.full_clean()

        offer.refresh_from_db()
        output_serializer = OfferSerializer(offer)
        return Response(output_serializer.data, status=status.HTTP_201_CREATED)
