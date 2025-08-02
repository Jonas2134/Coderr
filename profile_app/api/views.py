from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.exceptions import NotFound, PermissionDenied, ValidationError

from .serializers import ProfileDetailSerializer, ProfileDetailPatchSerializer, BusinessProfileSerializer, CustomerProfileSerializer
from profile_app.models import UserProfile
from core.decorators import handle_exceptions


class ProfileDetailPatchView(generics.RetrieveUpdateAPIView):
    permission_classes = [IsAuthenticated]

    def get_object(self):
        pk = self.kwargs.get('pk')
        try:
            profile = UserProfile.objects.get(pk=pk)
        except UserProfile.DoesNotExist:
            raise NotFound(detail="Profile not found.")
        return profile

    def get_serializer_class(self):
        if self.request.method == 'PATCH':
            return ProfileDetailPatchSerializer
        return ProfileDetailSerializer

    @handle_exceptions(action='retrieving profile')
    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @handle_exceptions(action='patching profile')
    def patch(self, request, *args, **kwargs):
        instance = self.get_object()
        if instance.user != request.user:
            raise PermissionDenied(detail="You do not have permission to edit this profile.")
        serializer = self.get_serializer(instance, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        output_serializer = ProfileDetailSerializer(instance, context={'request': request})
        return Response(output_serializer.data, status=status.HTTP_200_OK)


class ProfileRoleListView(generics.ListAPIView):
    permission_classes = [IsAuthenticated]
    role: str

    def get_queryset(self):
        if self.role == 'business':
            return UserProfile.objects.filter(user__type='business')
        if self.role == 'customer':
            return UserProfile.objects.filter(user__type='customer')
        raise ValidationError(detail="Invalid role specified.")

    def get_serializer_class(self):
        if self.role == 'business':
            return BusinessProfileSerializer
        elif self.role == 'customer':
            return CustomerProfileSerializer
        raise ValidationError(detail="Invalid role specified.")

    @handle_exceptions(action='listing profiles')
    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class BusinessProfileListView(ProfileRoleListView):
    role = 'business'


class CustomerProfileListView(ProfileRoleListView):
    role = 'customer'
