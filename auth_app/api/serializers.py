from rest_framework import serializers

from auth_app.models import CustomUser


class RegistrationSerializer(serializers.ModelSerializer):
    repeated_password = serializers.CharField(write_only=True)

    class Meta:
        model = CustomUser
        fields = ['username', 'email', 'password', 'repeated_password', 'type']
        extra_kwargs = {
            'username': {'required': True},
            'email': {'required': True},
            'password': {'write_only': True},
        }

    def create(self, validated_data):
        validated_data.pop('repeated_password', None)
        return super().create(validated_data)


class CustomLoginSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ['username', 'password']


class SuccessResponseSerializer(serializers.Serializer):
    token = serializers.CharField()
    username = serializers.CharField()
    email = serializers.EmailField()
    user_id = serializers.IntegerField()
