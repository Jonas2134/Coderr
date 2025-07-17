from rest_framework import serializers

from profile_app.models import UserProfile


class BaseProfileSerializer(serializers.ModelSerializer):
    user = serializers.PrimaryKeyRelatedField(read_only=True)
    username = serializers.CharField(source='user.username', read_only=True)
    first_name = serializers.CharField(source='user.first_name', read_only=True)
    last_name = serializers.CharField(source='user.last_name', read_only=True)

    class Meta:
        model = UserProfile
        fields = ['user', 'username', 'first_name', 'last_name', 'file']


class ProfileDetailSerializer(BaseProfileSerializer):
    type = serializers.CharField(source='user.type', read_only=True)
    email = serializers.EmailField(source='user.email', read_only=True)
    created_at = serializers.DateTimeField(source='user.date_joined', read_only=True)

    class Meta:
        model = UserProfile
        fields = BaseProfileSerializer.Meta.fields + ['location', 'tel', 'description', 'working_hours', 'type', 'email', 'created_at']


class ProfileDetailPatchSerializer(serializers.ModelSerializer):
    first_name = serializers.CharField(source='user.first_name')
    last_name = serializers.CharField(source='user.last_name')
    email = serializers.EmailField(source='user.email')

    class Meta:
        model = UserProfile
        fields = ['first_name', 'last_name', 'location', 'tel', 'description', 'working_hours', 'email']

    def update(self, instance, validated_data):
        user_data = validated_data.pop('user', {})
        user = instance.user
        for attr, value in user_data.items():
            setattr(user, attr, value)
        user.save()
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        return instance


class BusinessProfileSerializer(BaseProfileSerializer):
    type = serializers.CharField(source='user.type', read_only=True)

    class Meta:
        model = UserProfile
        fields = BaseProfileSerializer.Meta.fields + ['location', 'tel', 'description', 'working_hours', 'type']


class CustomerProfileSerializer(BaseProfileSerializer):
    uploaded_at = serializers.DateTimeField(source='user.date_joined', read_only=True)
    type = serializers.CharField(source='user.type', read_only=True)

    class Meta:
        model = UserProfile
        fields = BaseProfileSerializer.Meta.fields + ['uploaded_at', 'type']

