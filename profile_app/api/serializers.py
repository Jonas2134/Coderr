from rest_framework import serializers

from profile_app.models import UserProfile


class BaseProfileSerializer(serializers.ModelSerializer):
    """
    Base serializer for UserProfile that includes read-only user identity fields.

    Fields:
        user (int): Primary key of the related User (read-only).
        username (str): Username of the related User (read-only).
        first_name (str): First name of the related User (read-only).
        last_name (str): Last name of the related User (read-only).
        file (File): Profile file (e.g. avatar or document).
    """
    user = serializers.PrimaryKeyRelatedField(read_only=True)
    username = serializers.CharField(source='user.username', read_only=True)
    first_name = serializers.CharField(source='user.first_name', read_only=True)
    last_name = serializers.CharField(source='user.last_name', read_only=True)

    class Meta:
        model = UserProfile
        fields = ['user', 'username', 'first_name', 'last_name', 'file']


class ProfileDetailSerializer(BaseProfileSerializer):
    """
    Detailed serializer for viewing a full UserProfile, including user metadata.

    Extends BaseProfileSerializer by adding:
        type (str): The user’s account type.
        email (str): The user’s email address.
        created_at (datetime): When the user account was created.
        location (str): Profile location field.
        tel (str): Profile telephone number.
        description (str): Profile description.
        working_hours (str): Profile working hours.
    """
    type = serializers.CharField(source='user.type', read_only=True)
    email = serializers.EmailField(source='user.email', read_only=True)
    created_at = serializers.DateTimeField(source='user.date_joined', read_only=True)

    class Meta:
        model = UserProfile
        fields = BaseProfileSerializer.Meta.fields + ['location', 'tel', 'description', 'working_hours', 'type', 'email', 'created_at']


class ProfileDetailPatchSerializer(serializers.ModelSerializer):
    """
    Serializer for updating a UserProfile and related User fields.

    Allows patching:
        first_name (str): User’s first name.
        last_name (str): User’s last name.
        email (str): User’s email.
        location (str): Profile location.
        tel (str): Profile telephone.
        description (str): Profile description.
        working_hours (str): Profile working hours.

    The update() method synchronizes changes to both User and UserProfile.
    """
    first_name = serializers.CharField(source='user.first_name')
    last_name = serializers.CharField(source='user.last_name')
    email = serializers.EmailField(source='user.email')

    class Meta:
        model = UserProfile
        fields = ['first_name', 'last_name', 'location', 'tel', 'description', 'working_hours', 'email']

    def update(self, instance, validated_data):
        """
        Persist changes to the related User and the UserProfile instance.

        1. Pop and apply any user data (first_name, last_name, email).
        2. Save the User.
        3. Apply remaining fields to the UserProfile.
        4. Save and return the updated UserProfile.
        """
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
    """
    Serializer for business-user profiles.

    Extends BaseProfileSerializer by adding:
        location (str)
        tel (str)
        description (str)
        working_hours (str)
        type (str): Always 'business'.
    """
    type = serializers.CharField(source='user.type', read_only=True)

    class Meta:
        model = UserProfile
        fields = BaseProfileSerializer.Meta.fields + ['location', 'tel', 'description', 'working_hours', 'type']


class CustomerProfileSerializer(BaseProfileSerializer):
    """
    Serializer for customer-user profiles.

    Extends BaseProfileSerializer by adding:
        uploaded_at (datetime): When the user joined.
        type (str): Always 'customer'.
    """
    uploaded_at = serializers.DateTimeField(source='user.date_joined', read_only=True)
    type = serializers.CharField(source='user.type', read_only=True)

    class Meta:
        model = UserProfile
        fields = BaseProfileSerializer.Meta.fields + ['uploaded_at', 'type']
