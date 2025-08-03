from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import generics, status, mixins, filters
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.exceptions import NotFound

from .serializers import ReviewSerializer, ReviewCreateSerializer, ReviewUpdateSerializer
from .permissions import OneReviewPerBusinessUserPermission, IsUserReviewerPermission
from reviews_app.models import Review
from core.permissions import IsCustomerUser
from core.decorators import handle_exceptions


class ReviewsGetPostView(generics.ListCreateAPIView):
    """
    View for listing and creating reviews.

    GET:
        - Returns a paginated list of reviews.
        - Supports filtering by `business_user_id` and `reviewer_id`.
        - Supports ordering by `created_at` and `rating`.

    POST:
        - Allows authenticated users with type 'customer' to create a review.
        - Only one review per business user is allowed per reviewer.
        - Automatically sets the `reviewer` to the currently authenticated user.

    Permissions:
        - GET: Requires authentication.
        - POST: Requires authentication, customer role, and no existing review for the same business user.

    Filters:
        - filterset_fields: ['business_user_id', 'reviewer_id']
        - ordering_fields: ['created_at', 'rating']
    """
    queryset = Review.objects.all()
    serializer_class = ReviewSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['business_user_id', 'reviewer_id']
    ordering_fields = ['created_at', 'rating']

    def get_permissions(self):
        """
        Returns a list of permission instances that the current request must satisfy.

        - For POST requests: Ensures the user is authenticated, has the role of a customer,
          and has not already submitted a review for the specified business user.
        - For GET requests: Only authentication is required.

        This dynamic handling ensures stricter access control for creating reviews.
        """
        if self.request.method == 'POST':
            return [IsAuthenticated(), IsCustomerUser(), OneReviewPerBusinessUserPermission()]
        return super().get_permissions()

    @handle_exceptions(action='listing reviews')
    def get(self, request, *args, **kwargs):
        """
        Returns a filtered and/or ordered list of reviews.
        """
        return super().get(request, *args, **kwargs)

    @handle_exceptions(action='creating review')
    def create(self, request, *args, **kwargs):
        """
        Validates and creates a new review. Automatically sets the reviewer
        to the authenticated user and uses `ReviewCreateSerializer` for input
        validation.
        """
        serializer = ReviewCreateSerializer(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        review = serializer.save()
        output_serializer = self.get_serializer(review)
        return Response(output_serializer.data, status=status.HTTP_201_CREATED)


class ReviewsPatchDeleteView(
    mixins.UpdateModelMixin,
    mixins.DestroyModelMixin,
    generics.GenericAPIView
):
    """
    View for updating (PATCH) and deleting (DELETE) individual reviews.

    PATCH:
        - Partially updates a review.
        - Only the reviewer who created the review can perform this action.
        - Uses `ReviewUpdateSerializer` for input validation.
        - Returns updated data using the default output serializer.

    DELETE:
        - Deletes a review.
        - Only the original reviewer can delete it.

    Permissions:
        - Requires authentication and the user must be the original reviewer.

    Methods:
        - get_object(): Fetches the review by ID and raises a 404 if not found.
    """
    queryset = Review.objects.all()
    serializer_class = ReviewSerializer
    permission_classes = [IsAuthenticated, IsUserReviewerPermission]

    def get_object(self):
        """
        Retrieves the review object by primary key from URL kwargs.
        Raises a 404 if not found.
        """
        review_id = self.kwargs.get('pk')
        try:
            review = Review.objects.get(pk=review_id)
        except Review.DoesNotExist:
            raise NotFound('Review not found')
        return review

    @handle_exceptions(action='updating review')
    def patch(self, request, *args, **kwargs):
        """
        Entry point for PATCH request. Delegates to `partial_update`.
        """
        return super().partial_update(request, *args, **kwargs)

    @handle_exceptions(action='updating review')
    def partial_update(self, request, *args, **kwargs):
        """
        Partially updates the review with validated fields.
        Uses `ReviewUpdateSerializer` for input and default output serializer for response.
        """
        review = self.get_object()
        serializer = ReviewUpdateSerializer(review, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        output_serializer = self.get_serializer(review, context={'request': request})
        return Response(output_serializer.data, status=status.HTTP_200_OK)

    @handle_exceptions(action='deleting review')
    def delete(self, request, *args, **kwargs):
        """
        Deletes the review instance. Only allowed for the original reviewer.
        """
        return super().destroy(request, *args, **kwargs)
