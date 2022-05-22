"""Permissions of the app accounts."""

from rest_framework import permissions
from django.utils.timezone import activate as activate_timezone
from common.library import BadRequest
from common.library import UnauthorizedAccess
from common.library import AccessForbidden

from common.library import _decode

from .models import AccessToken, Invoice
from .constants import USER_TYPE_OWNER


class IsAuthenticated(permissions.BasePermission):
    """
    Check if the user is authenticated.

    Authentication to check if the user access token is valid
    and fetch the user from the token and add it to kwargs.
    """

    def has_permission(self, request, view):
        """Function to check token."""
        key = request.META.get('HTTP_TOKEN')
        user_id = _decode(request.META.get('HTTP_USER_ID'))

        if not key:
            raise BadRequest(
                'Can not find Bearer token in the request header.')
        if not user_id:
            raise BadRequest(
                'Can not find User-Id in the request header.')

        try:
            user = AccessToken.objects.get(
                key=key, user__id=user_id).user
        except:
            raise UnauthorizedAccess(
                'Invalid Bearer token or User-Id, please re-login.')

        request.user = user
        view.kwargs['user'] = user
        return True


class IsOwner(permissions.BasePermission):
    """
    Check if the user is an owner.

    """

    def has_permission(self, request, view):
        """
        Overriding permission check to check
        if the user type is an owner.
        """

        try:
            user = view.kwargs['user']
            if user.type != USER_TYPE_OWNER:
                raise AccessForbidden(
                    "You need to be Owner to perform this action.")
        except Exception as e:
            raise AccessForbidden(
                "You need to be owner to perform this action.")
        return True
