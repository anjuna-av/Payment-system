"""Serializers related to the auth."""

from rest_framework import serializers
from django.contrib.auth import authenticate
from common.library import UnauthorizedAccess


class LoginSerializer(serializers.Serializer):
    """Serializer to login."""

    username = serializers.CharField()
    password = serializers.CharField()

    def create(self, validated_data):
        """Overriding the create method."""
        user = authenticate(
            username=validated_data['username'],
            password=validated_data['password'])
        if not user:
            raise UnauthorizedAccess('Invalid email or password')

        validated_data['user'] = user.id
        return user

    def to_representation(self, obj):
        """Overriding the value returned when returning the
        serializer."""
        data = {
            'token': obj.issue_access_token(),
            'id': obj.idencode,
            'email_verified': obj.email_verified,
            'terms_accepted': obj.terms_accepted
        }
        return data