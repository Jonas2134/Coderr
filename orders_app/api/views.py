from rest_framework import generics, status, filters
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response


class OrdersGetPostView(generics.ListCreateAPIView):
    pass
