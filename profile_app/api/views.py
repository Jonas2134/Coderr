from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated


class ProfileDetailPatchView(generics.RetrieveUpdateAPIView):
    pass


class ProfileRoleListView(generics.ListAPIView):
    pass


class BusinessProfileListView(ProfileRoleListView):
    pass


class CustomerProfileListView(ProfileRoleListView):
    pass
