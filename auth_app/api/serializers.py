from rest_framework import serializers

from auth_app.models import CustomUser


class RegistrationSerializer(serializers.ModelSerializer):
    """
    Serializer for user registration endpoint.

    Validates that both password fields are provided and forwards them for
    custom validation in the view. Inherits from ModelSerializer to
    automatically handle username, email, password, and type fields of
    CustomUser.

    Fields:
        repeated_password (str): Write-only field to confirm the password.
    """
    repeated_password = serializers.CharField(write_only=True)

    class Meta:
        """
        Meta options for RegistrationSerializer.

        Attributes:
            model (Model): The Django model this serializer maps to (CustomUser).
            fields (list): Fields to include in serialization/deserialization.
            extra_kwargs (dict): Additional settings per field.
        """
        model = CustomUser
        fields = ['username', 'email', 'password', 'repeated_password', 'type']
        extra_kwargs = {
            'username': {'required': True},
            'email': {'required': True},
            'password': {'write_only': True},
        }


class CustomLoginSerializer(serializers.Serializer):
    """
    Serializer for user login endpoint.

    Validates that both username and password are provided in the request.
    Does not map to a model.
    """
    username = serializers.CharField(required=True, write_only=True)
    password = serializers.CharField(required=True, write_only=True)


class SuccessResponseSerializer(serializers.Serializer):
    """
    Serializer for standard success responses after registration or login.

    Returns the authentication token and basic user information.
    """
    token = serializers.CharField()
    username = serializers.CharField()
    email = serializers.EmailField()
    user_id = serializers.IntegerField()
