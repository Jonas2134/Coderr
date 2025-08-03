from django.db import transaction
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import generics, status, filters
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework.exceptions import NotFound

from .serializers import OfferSerializer, OfferResultSerializer, NestedOfferResultSerializer, NestedDetailSerializer
from .permissions import IsUserCreator
from .filters import OfferFilterSet
from .paginations import OfferPagination
from offers_app.models import Offer, OfferDetail
from core.decorators import handle_exceptions
from core.permissions import IsBusinessUser


class OffersGetPostView(generics.ListCreateAPIView):
    """
    API endpoint to list all offers and to create a new offer.

    - GET: Returns a paginated, filterable, searchable, and orderable list of offers.
    - POST: Allows authenticated business users to create a new offer with nested details.

    Attributes:
        queryset (QuerySet): Base queryset of Offers, with `.distinct()` to avoid duplicates.
        permission_classes (list): [AllowAny] for GET; overridden for POST.
        pagination_class (PageNumberPagination): Controls pagination behavior.
        filter_backends (list): Enables filtering (DjangoFilter), ordering, and search.
        filterset_class (FilterSet): Defines filters for creator, price, and delivery time.
        ordering_fields (list): Fields permitted for ordering in GET.
        search_fields (list): Fields permitted for full-text search in GET.
    """
    queryset = Offer.objects.all().distinct()
    permission_classes = [AllowAny]
    pagination_class = OfferPagination
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter, filters.SearchFilter]
    filterset_class = OfferFilterSet
    ordering_fields = ['updated_at', 'min_price']
    search_fields = ['title', 'description']

    def get_permissions(self):
        """
        Return permissions based on HTTP method.

        - POST requires authentication and business user status.
        - GET uses default AllowAny.
        """
        if self.request.method in ['POST']:
            return [IsAuthenticated(), IsBusinessUser()]
        return super().get_permissions()

    def get_serializer_class(self):
        """
        Choose serializer based on HTTP method.

        - POST uses OfferSerializer for input validation and creation.
        - GET uses OfferResultSerializer for nested read-only output.
        """
        if self.request.method == 'POST':
            return OfferSerializer
        return OfferResultSerializer

    @handle_exceptions(action='retrieving offers')
    def get(self, request, *args, **kwargs):
        """
        Handle GET requests: list offers.

        1. Apply filters, search, and ordering.
        2. Paginate the resulting queryset.
        3. Serialize with context (for Hyperlinked fields).
        4. Return paginated response.
        """
        qs = self.filter_queryset(self.get_queryset())
        page = self.paginate_queryset(qs)
        serializer = self.get_serializer(page, many=True, context={'request': request})
        return self.get_paginated_response(serializer.data)

    @handle_exceptions(action='creating offer')
    def create(self, request, *args, **kwargs):
        """
        Handle POST requests: create a new offer.

        1. Validate top-level offer data and nested details.
        2. Within a DB transaction:
           a. Create the Offer with `creator=request.user`.
           b. Create each nested OfferDetail.
           c. Run `full_clean()` for model validation.
        3. Refresh from DB to populate nested relations.
        4. Serialize with OfferResultSerializer and return 201 CREATED.
        """
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
        output_serializer = self.get_serializer(offer)
        return Response(output_serializer.data, status=status.HTTP_201_CREATED)


class OffersRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    """
    API endpoint to retrieve, update, or delete a specific offer.

    - GET: Retrieve nested offer data.
    - PUT/PATCH: Partially update an offer and nested details (creator only).
    - DELETE: Remove an offer (creator only).

    Attributes:
        queryset (QuerySet): Base queryset of Offers.
        permission_classes (list): [IsAuthenticated] for GET; overridden for unsafe.
    """
    queryset = Offer.objects.all()
    permission_classes = [IsAuthenticated]

    def get_permissions(self):
        """
        Return permissions based on HTTP method.

        - PUT/PATCH/DELETE requires authentication + creator ownership.
        - GET uses default IsAuthenticated.
        """
        if self.request.method in ['PUT', 'PATCH', 'DELETE']:
            return [IsAuthenticated(), IsUserCreator()]
        return super().get_permissions()

    def get_object(self):
        """
        Retrieve the Offer instance or raise 404.

        Uses `pk` URL kwarg. Raises NotFound if no matching Offer.
        """
        offer_id = self.kwargs.get('pk')
        try:
            offer = Offer.objects.get(pk=offer_id)
        except Offer.DoesNotExist:
            raise NotFound(detail="Offer not found.")
        return offer

    def get_serializer_class(self):
        """
        Choose serializer based on HTTP method.

        - GET: NestedOfferResultSerializer for read-only nested output.
        - PUT/PATCH: OfferSerializer for update with nested details.
        """
        if self.request.method == 'GET':
            return NestedOfferResultSerializer
        return OfferSerializer

    @handle_exceptions(action='retrieving offer')
    def retrieve(self, request, *args, **kwargs):
        """Delegate to DRF to retrieve the specified offer."""
        return super().retrieve(request, *args, **kwargs)

    @handle_exceptions(action='updating offer')
    def update(self, request, *args, **kwargs):
        """
        Handle PUT/PATCH: partial update.

        1. Fetch instance.
        2. Validate partial data with OfferSerializer.
        3. Save updates via `perform_update`.
        4. Refresh and return nested representation.
        """
        partial = True
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        instance.refresh_from_db()
        output_serializer = self.get_serializer(instance)
        return Response(output_serializer.data, status=status.HTTP_200_OK)

    @handle_exceptions(action='deleting offer')
    def destroy(self, request, *args, **kwargs):
        """Delegate to DRF to delete the specified offer."""
        return super().destroy(request, *args, **kwargs)


class DetailsRetrieveView(generics.RetrieveAPIView):
    """
    API endpoint to retrieve a single OfferDetail by primary key.

    - GET: Returns the detail fields only to authenticated users.

    Attributes:
        queryset (QuerySet): Base queryset of OfferDetail.
        serializer_class (Serializer): NestedDetailSerializer for output.
        permission_classes (list): [IsAuthenticated] to restrict access.
    """
    queryset = OfferDetail.objects.all()
    serializer_class = NestedDetailSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        """
        Retrieve the OfferDetail instance or raise 404.

        Uses `pk` URL kwarg. Raises NotFound if no matching detail.
        """
        detail_id = self.kwargs.get('pk')
        try:
            detail = OfferDetail.objects.get(pk=detail_id)
        except OfferDetail.DoesNotExist:
            raise NotFound(detail="Offer detail not found.")
        return detail

    @handle_exceptions(action='retrieving offer detail')
    def retrieve(self, request, *args, **kwargs):
        """Delegate to DRF to retrieve the specified OfferDetail."""
        return super().retrieve(request, *args, **kwargs)
