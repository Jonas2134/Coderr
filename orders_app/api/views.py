from rest_framework import generics, status, filters, mixins
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response


class OrdersGetPostView(generics.ListCreateAPIView):
    pass


class OrderPatchDeleteView(
    mixins.UpdateModelMixin,
    mixins.DestroyModelMixin,
    generics.GenericAPIView
):
    pass


class OrderCountView(generics.RetrieveAPIView):
    pass


class CompletedOrderCountView(generics.RetrieveAPIView):
    pass
