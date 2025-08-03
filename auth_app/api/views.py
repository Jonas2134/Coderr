from django.contrib.auth import authenticate
from rest_framework import status, generics
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from rest_framework.authtoken.models import Token

from .serializers import RegistrationSerializer, CustomLoginSerializer, SuccessResponseSerializer
from auth_app.models import CustomUser


def build_response(user, status_code):
    """
    Build a standardized successful authentication or registration response.

    Fetches (or creates) the auth token for the given user and serializes
    the key together with basic user info.

    Args:
        user (CustomUser): The authenticated or newly created user.
        status_code (int): HTTP status code to return (e.g. 200, 201).

    Returns:
        rest_framework.response.Response: A DRF Response containing:
            - token (str): Auth token key
            - email (str): User's email
            - username (str): User's username
            - user_id (int): User's primary key
    """
    token, _ = Token.objects.get_or_create(user=user)
    response_data = {
        'token': token.key,
        'email': user.email,
        'username': user.username,
        'user_id': user.id,
    }
    output_serializer = SuccessResponseSerializer(response_data)
    return Response(output_serializer.data, status=status_code)


class RegistrationView(generics.CreateAPIView):
    """
    API endpoint for user registration.

    Accepts username, email, password, repeated_password, and user type;
    performs validation to ensure unique email and matching passwords;
    creates a CustomUser and returns an auth token.

    Attributes:
        permission_classes (list): [AllowAny] so unauthenticated users can register.
        serializer_class (Serializer): RegistrationSerializer for input validation.
    """
    permission_classes = [AllowAny]
    serializer_class = RegistrationSerializer

    def create(self, request, *args, **kwargs):
        """
        Handle POST to register a new user.

        1. Validate input via serializer.
        2. Run custom validation (_validate_registration).
        3. Create user (_create_user) if valid.
        4. Return token+user info via build_response.

        Returns:
            Response: DRF Response with token and user info on success,
                      or error details and 400 status on failure.
        """
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data

        error_response = self._validate_registration(data)
        if error_response:
            return error_response

        user = self._create_user(
            username=data['username'],
            email=data['email'],
            password=data['password'],
            type=data['type']
        )
        return build_response(user, status.HTTP_201_CREATED)

    def _validate_registration(self, data):
        """
        Run extra validation rules on registration payload.

        Args:
            data (dict): Validated data from RegistrationSerializer.

        Returns:
            Response or None: DRF Response with 400 status on error,
                              or None if validation passes.
        """
        if CustomUser.objects.filter(email=data['email']).exists():
            return Response({'email': ['This e-mail address is already taken!']}, status=status.HTTP_400_BAD_REQUEST)
        if data['password'] != data['repeated_password']:
            return Response({'password': ["The passwords don't match!"]}, status=status.HTTP_400_BAD_REQUEST)

    def _create_user(self, username, email, password, type):
        """
        Persist a new CustomUser in the database.

        Args:
            username (str): Desired username.
            email (str): User's email address.
            password (str): Raw password (will be hashed).
            type (str): One of the choices defined on CustomUser.type.

        Returns:
            CustomUser: The newly created user instance.
        """
        user = CustomUser(username=username, email=email, type=type)
        user.set_password(password)
        user.save()
        return user


class CustomLoginView(generics.GenericAPIView):
    """
    API endpoint for user login.

    Accepts username and password, authenticates the user, checks active status,
    and returns an auth token plus basic user info on success.

    Attributes:
        permission_classes (list): [AllowAny] so unauthenticated users can log in.
        serializer_class (Serializer): CustomLoginSerializer for input validation.
    """
    permission_classes = [AllowAny]
    serializer_class = CustomLoginSerializer

    def post(self, request, *args, **kwargs):
        """
        Handle POST to authenticate user.

        1. Validate input via serializer.
        2. Attempt authentication (_authenticate_user).
        3. Return error response if credentials invalid or account inactive.
        4. On success, return token+user info via build_response.

        Returns:
            Response: DRF Response with token and user info on success,
                      or error details and 400 status on failure.
        """
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = self._authenticate_user(serializer.validated_data)
        if isinstance(user, Response):
            return user
        return build_response(user, status.HTTP_200_OK)

    def _authenticate_user(self, data):
        """
        Verify user credentials and active status.

        Args:
            data (dict): Validated data containing 'username' and 'password'.

        Returns:
            CustomUser or Response: Authenticated user instance on success,
                                    or DRF Response with error on failure.
        """
        user = authenticate(request=self.request, username=data['username'], password=data['password'])
        if not user:
            return Response({"detail": "Invalid username or password."}, status=status.HTTP_400_BAD_REQUEST)
        if not user.is_active:
            return Response({"detail": "This account is not active."}, status=status.HTTP_400_BAD_REQUEST)
        return user
