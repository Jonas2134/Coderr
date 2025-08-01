from django.contrib.auth import get_user_model
from django.db.models import Avg, Count
from rest_framework.generics import GenericAPIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated


class GetBaseInfoView(GenericAPIView):
    pass
