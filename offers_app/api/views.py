from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework.exceptions import NotFound, PermissionDenied, ValidationError
from rest_framework.pagination import PageNumberPagination

from .serilaizers import OfferSerializer, OfferFilterdSerializer
from .permissions import IsBusinessUser
from offers_app.models import Offer
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
        return super().create(request, *args, **kwargs)
