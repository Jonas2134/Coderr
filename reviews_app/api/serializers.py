from django.db import IntegrityError
from rest_framework import serializers
from rest_framework.validators import UniqueTogetherValidator

from reviews_app.models import Review

class ReviewSerializer(serializers.ModelSerializer):
    """
    Serializer for retrieving review details.

    Fields:
        - id (int, read-only): The unique identifier of the review.
        - business_user (int): The ID of the business user being reviewed.
        - reviewer (int): The ID of the user who wrote the review.
        - rating (float): The numeric rating given by the reviewer.
        - description (str): Optional textual feedback from the reviewer.
        - created_at (datetime, read-only): Timestamp of when the review was created.
        - updated_at (datetime, read-only): Timestamp of the most recent update.

    Use Case:
        Used primarily for `GET` requests to retrieve a full review instance.
    """
    class Meta:
        model = Review
        fields = ['id', 'business_user', 'reviewer', 'rating', 'description', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']


class ReviewCreateSerializer(serializers.ModelSerializer):
    """
    Serializer for creating a new review.

    Fields:
        - business_user (int): The ID of the business user being reviewed.
        - rating (float): The numeric rating to assign.
        - description (str): Optional feedback text.

    Behavior:
        - The reviewer is automatically assigned from the authenticated user in the request context.
        - Prevents clients from manually setting the `reviewer` field.

    Use Case:
        Used with `POST` requests to submit a new review.
    """
    class Meta:
        model = Review
        fields = ['business_user', 'rating', 'description']
    
    def validate(self, attrs):
        """
        Perform two key validations before creating a Review:

        1. Automatically assign the current user as the `reviewer`.
        2. Enforce that each user may only submit one review per business:
           if a review by this user for the given business_user already exists,
           raise a ValidationError.

        Args:
            attrs (dict): The incoming, unvalidated data from the request.

        Raises:
            serializers.ValidationError:
                If a review by this user for the same business_user is found,
                with an error keyed on 'business_user'.

        Returns:
            dict: The validated attributes, now including the `reviewer`
                  field set to request.user.
        """
        user = self.context['request'].user
        attrs['reviewer'] = user
        if Review.objects.filter(reviewer=user, business_user=attrs['business_user']).exists():
            raise serializers.ValidationError({'business_user': 'You have already submitted a review for this business user.'})
        return super().validate(attrs)

    def create(self, validated_data):
        """
        Overrides the default create method to associate the review with the
        currently authenticated user as the reviewer.

        Args:
            validated_data (dict): Validated input data from the request.

        Returns:
            Review: A new Review instance linked to the authenticated user.
        """
        reviewer = self.context['request'].user
        return Review.objects.create(reviewer=reviewer, **validated_data)


class ReviewUpdateSerializer(serializers.ModelSerializer):
    """
    Serializer for updating an existing review.

    Fields:
        - rating (float): Updated rating value.
        - description (str): Updated feedback text.

    Use Case:
        Used with `PATCH` or `PUT` requests to modify the rating or description of an existing review.
    """
    class Meta:
        model = Review
        fields = ['rating', 'description']
