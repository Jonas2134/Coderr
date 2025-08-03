from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.exceptions import NotFound, PermissionDenied, ValidationError

from .serializers import ProfileDetailSerializer, ProfileDetailPatchSerializer, BusinessProfileSerializer, CustomerProfileSerializer
from profile_app.models import UserProfile
from core.decorators import handle_exceptions


class ProfileDetailPatchView(generics.RetrieveUpdateAPIView):
    """
    API endpoint to retrieve or patch a single user profile.

    - GET: Retrieve the full UserProfile (ProfileDetailSerializer).
    - PATCH: Update allowed profile fields (ProfileDetailPatchSerializer),
             only if the requesting user owns the profile.

    Attributes:
        permission_classes (list): [IsAuthenticated] — user must be logged in.
    """
    permission_classes = [IsAuthenticated]

    def get_object(self):
        """
        Fetch the UserProfile by primary key or raise 404.

        Returns:
            UserProfile: The requested profile instance.

        Raises:
            NotFound: If no UserProfile matches the given pk.
        """
        pk = self.kwargs.get('pk')
        try:
            profile = UserProfile.objects.get(pk=pk)
        except UserProfile.DoesNotExist:
            raise NotFound(detail="Profile not found.")
        return profile

    def get_serializer_class(self):
        """
        Select serializer based on HTTP method.

        - PATCH: uses ProfileDetailPatchSerializer for updates.
        - GET: uses ProfileDetailSerializer for read-only output.
        """
        if self.request.method == 'PATCH':
            return ProfileDetailPatchSerializer
        return ProfileDetailSerializer

    @handle_exceptions(action='retrieving profile')
    def retrieve(self, request, *args, **kwargs):
        """
        Handle GET: serialize and return the profile data.

        Returns:
            Response: HTTP 200 with profile details.
        """
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @handle_exceptions(action='patching profile')
    def patch(self, request, *args, **kwargs):
        """
        Handle PATCH: ensure ownership, apply partial updates, and return updated profile.

        Raises:
            PermissionDenied: If the authenticated user does not own the profile.

        Returns:
            Response: HTTP 200 with the refreshed ProfileDetailSerializer data.
        """
        instance = self.get_object()
        if instance.user != request.user:
            raise PermissionDenied(detail="You do not have permission to edit this profile.")
        serializer = self.get_serializer(instance, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        output_serializer = ProfileDetailSerializer(instance, context={'request': request})
        return Response(output_serializer.data, status=status.HTTP_200_OK)


class ProfileRoleListView(generics.ListAPIView):
    """
    Base endpoint for listing UserProfiles by user role.

    Subclasses must set `role` to either 'business' or 'customer' and
    will return the corresponding serializer.

    Attributes:
        permission_classes (list): [IsAuthenticated] — user must be logged in.
        role (str): Role to filter by ('business' or 'customer').
    """
    permission_classes = [IsAuthenticated]
    role: str

    def get_queryset(self):
        """
        Filter UserProfile queryset by the specified role.

        Returns:
            QuerySet: Profiles where user.type == self.role.

        Raises:
            ValidationError: If `self.role` is not 'business' or 'customer'.
        """
        if self.role == 'business':
            return UserProfile.objects.filter(user__type='business')
        if self.role == 'customer':
            return UserProfile.objects.filter(user__type='customer')
        raise ValidationError(detail="Invalid role specified.")

    def get_serializer_class(self):
        """
        Choose serializer based on role:

        - 'business': BusinessProfileSerializer
        - 'customer': CustomerProfileSerializer

        Raises:
            ValidationError: If `self.role` is not 'business' or 'customer'.
        """
        if self.role == 'business':
            return BusinessProfileSerializer
        elif self.role == 'customer':
            return CustomerProfileSerializer
        raise ValidationError(detail="Invalid role specified.")

    @handle_exceptions(action='listing profiles')
    def list(self, request, *args, **kwargs):
        """
        Handle GET: serialize and return all profiles for the role.

        Returns:
            Response: HTTP 200 with list of profiles.
        """
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class BusinessProfileListView(ProfileRoleListView):
    """
    Endpoint to list all business user profiles.

    Inherits ProfileRoleListView with role='business'.
    """
    role = 'business'


class CustomerProfileListView(ProfileRoleListView):
    """
    Endpoint to list all customer user profiles.

    Inherits ProfileRoleListView with role='customer'.
    """
    role = 'customer'
