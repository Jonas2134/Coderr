from django.db import transaction
from django.db.models import Min
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import generics, status, filters
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework.exceptions import NotFound, PermissionDenied, ValidationError
from rest_framework.pagination import PageNumberPagination

from .serilaizers import OfferSerializer, OfferResultSerializer, NestedOfferResultSerializer
from .permissions import IsBusinessUser
from .filters import OfferFilterSet
from offers_app.models import Offer, OfferDetail
from core.decorators import handle_exceptions


class OfferPagination(PageNumberPagination):
    page_size = 1
    page_size_query_param = "page_size"


class OffersGetPostView(generics.ListCreateAPIView):
    queryset = Offer.objects.all().distinct()
    permission_classes = [AllowAny]
    pagination_class = OfferPagination
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter, filters.SearchFilter]
    filterset_class = OfferFilterSet
    ordering_fields = ['updated_at', 'min_price']
    search_fields = ['title', 'description']

    def get_permissions(self):
        if self.request.method in ['POST']:
            return [IsAuthenticated(), IsBusinessUser()]
        return super().get_permissions()

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return OfferSerializer
        return OfferResultSerializer

    @handle_exceptions(action='retrieving offers')
    def get(self, request, *args, **kwargs):
        qs = self.filter_queryset(self.get_queryset())
        page = self.paginate_queryset(qs)
        serializer = self.get_serializer(page, many=True, context={'request': request})
        return self.get_paginated_response(serializer.data)

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


class OffersRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Offer.objects.all()
    permission_classes = [IsAuthenticated]

    def get_object(self):
        offer_id = self.kwargs.get('pk')
        try:
            offer = Offer.objects.get(pk=offer_id)
        except Offer.DoesNotExist:
            raise NotFound(detail="Offer not found.")
        return offer
    
    def get_serializer_class(self):
        if self.request.method == 'GET':
            return NestedOfferResultSerializer
        return OfferSerializer
    
    @handle_exceptions(action='retrieving offer')
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)


class DetailsRetrieveView(generics.RetrieveAPIView):
    pass
