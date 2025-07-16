from rest_framework import status, generics
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.authtoken.models import Token

from auth_app.models import CustomUser
from .serializers import RegistrationSerializer, CustomLoginSerializer, SuccessResponseSerializer


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

        user = serializer.save()
        return self._build_response(user)

    def _validate_registration(self, data):
        if CustomUser.objects.filter(email=data['email']).exists():
            return Response({'email': ['This e-mail address is already taken!']}, status=status.HTTP_400_BAD_REQUEST)
        if data['password'] != data['repeated_password']:
            return Response({'password': ["The passwords don't match!"]}, status=status.HTTP_400_BAD_REQUEST)

    def _build_response(self, user):
        token, _ = Token.objects.get_or_create(user=user)
        response_data = {
            'token': token.key,
            'email': user.email,
            'username': user.username,
            'user_id': user.id,
        }
        output_serializer = SuccessResponseSerializer(response_data)
        return Response(output_serializer.data, status=status.HTTP_201_CREATED)


class CustomLoginView(generics.GenericAPIView):
    pass
