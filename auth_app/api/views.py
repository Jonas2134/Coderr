from rest_framework import status, generics
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from rest_framework.authtoken.models import Token
from django.contrib.auth import authenticate

from auth_app.models import CustomUser
from .serializers import RegistrationSerializer, CustomLoginSerializer, SuccessResponseSerializer


def build_response(user, status_code):
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
    permission_classes = [AllowAny]
    serializer_class = RegistrationSerializer

    def create(self, request, *args, **kwargs):
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
        if CustomUser.objects.filter(email=data['email']).exists():
            return Response({'email': ['This e-mail address is already taken!']}, status=status.HTTP_400_BAD_REQUEST)
        if data['password'] != data['repeated_password']:
            return Response({'password': ["The passwords don't match!"]}, status=status.HTTP_400_BAD_REQUEST)
    
    def _create_user(self, username, email, password, type):
        user = CustomUser(username=username, email=email, type=type)
        user.set_password(password)
        user.save()
        return user


class CustomLoginView(generics.GenericAPIView):
    permission_classes = [AllowAny]
    serializer_class = CustomLoginSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = self._authenticate_user(serializer.validated_data)
        if isinstance(user, Response):
            return user
        return build_response(user, status.HTTP_200_OK)

    def _authenticate_user(self, data):
        user = authenticate(request=self.request, username=data['username'], password=data['password'])
        if not user:
            return Response({"detail": "Invalid username or password."}, status=status.HTTP_400_BAD_REQUEST)
        if not user.is_active:
            return Response({"detail": "This account is not active."}, status=status.HTTP_400_BAD_REQUEST)
        return user
