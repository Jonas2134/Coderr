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
    queryset = Review.objects.all()
    serializer_class = ReviewSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['business_user_id', 'reviewer_id']
    ordering_fields = ['created_at', 'rating']

    def get_permissions(self):
        if self.request.method == 'POST':
            return [IsAuthenticated(), IsCustomerUser(), OneReviewPerBusinessUserPermission()]
        return super().get_permissions()

    @handle_exceptions(action='listing reviews')
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

    @handle_exceptions(action='creating review')
    def create(self, request, *args, **kwargs):
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
    queryset = Review.objects.all()
    serializer_class = ReviewSerializer
    permission_classes = [IsAuthenticated, IsUserReviewerPermission]

    def get_object(self):
        review_id = self.kwargs.get('pk')
        try:
            review = Review.objects.get(pk=review_id)
        except Review.DoesNotExist:
            raise NotFound('Review not found')
        return review

    @handle_exceptions(action='updating review')
    def patch(self, request, *args, **kwargs):
        return super().partial_update(request, *args, **kwargs)

    @handle_exceptions(action='updating review')
    def partial_update(self, request, *args, **kwargs):
        review = self.get_object()
        serializer = ReviewUpdateSerializer(review, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        output_serializer = self.get_serializer(review, context={'request': request})
        return Response(output_serializer.data, status=status.HTTP_200_OK)

    @handle_exceptions(action='deleting review')
    def delete(self, request, *args, **kwargs):
        return super().destroy(request, *args, **kwargs)
