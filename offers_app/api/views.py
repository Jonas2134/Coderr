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
    
    def get_serializer(self, *args, **kwargs):
        if self.request.method == 'POST':
            return OfferSerializer
        return OfferFilterdSerializer
    
    @handle_exceptions(action='retrieving offers')
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

    @handle_exceptions(action='creating offer')
    def create(self, request, *args, **kwargs):
        try:
            print("[DEBUG] Enter OffersGetPostView.create with data:", request.data)
            serializer = self.get_serializer(data=request.data)
            print("[DEBUG] Serializer instance created successfully")
        except Exception as e:
            print("[ERROR] Failed to instantiate serializer:", e)
            raise

        try:
            serializer.is_valid(raise_exception=True)
            print("[DEBUG] Serializer validation passed. Validated data:", serializer.validated_data)
        except ValidationError as e:
            print("[ERROR] Serializer validation failed:", e)
            raise

        print("[DEBUG] Validated data:", serializer.validated_data)
        # serializer.is_valid(raise_exception=True)
        details_data = serializer.validated_data.pop('details')
        print("[DEBUG] Details to create:", details_data)
        data = serializer.validated_data

        with transaction.atomic():
            offer = Offer.objects.create(creator=request.user, **data)
            for detail in details_data:
                OfferDetail.objects.create(offer=offer, **detail)
            offer.full_clean()

        output_serializer = self.get_serializer(offer)
        return Response(output_serializer.data, status=status.HTTP_201_CREATED)
