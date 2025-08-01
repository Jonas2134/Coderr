from rest_framework import generics, status, mixins
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.response import Response
from rest_framework.exceptions import NotFound


class ReviewsGetPostView(generics.ListCreateAPIView):
    pass


class ReviewsPatchDeleteView(
    mixins.UpdateModelMixin,
    mixins.DestroyModelMixin,
    generics.GenericAPIView
):
    pass
