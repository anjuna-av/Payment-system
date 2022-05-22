"""All custom used functions and class are declared here."""
from django.utils.crypto import get_random_string
from hashids import Hashids
from rest_framework import serializers
from rest_framework import status
from rest_framework.response import Response
from django.conf import settings
from rest_framework.exceptions import APIException


class BaseAPIException(APIException):
    """ Base API Exception to provide option to fail silently"""
    send_to_sentry = True

    def __init__(self, *args, **kwargs):
        if 'send_to_sentry' in kwargs:
            self.send_to_sentry = kwargs.pop('send_to_sentry')
        super(BaseAPIException, self).__init__(*args, **kwargs)


def _get_file_path(instance, filename):
    """
    Function to get filepath for a file to be uploaded
    Args:
        instance: instance of the file object
        filename: uploaded filename

    Returns:
        path: Path of file
    """
    type = instance.__class__.__name__.lower()
    path = '%s/%s/%s:%s' % (
        type, instance.id,
        get_random_string(10), filename)
    return path


def _pop_out_from_dictionary(dictionary, keys):
    """
    Function to remove keys from dictionary.

    Input Params:
        dictionary(dict): dictionary
        keys(list)
    Returns:
        dictionary(dictionary): updated dictionary.
    """
    for key in keys:
        dictionary.pop(key, None)
    return dictionary


def _encode(value):
    """
    Function to  hash hid the int value.

    Input Params:
        value(int): int value
    Returns:
        hashed string.
    """
    hasher = Hashids(
        min_length=settings.HASHHID_MIN_LENGTH,
        salt=settings.HASHHID_SALT)
    try:
        value = int(value)
        return hasher.encode(value)
    except:
        return None


def _decode(value):
    """
    Function to  decode hash hid value.

    Input Params:
        value(str): str value
    Returns:
        int value.
    """
    hasher = Hashids(
        min_length=settings.HASHHID_MIN_LENGTH,
        salt=settings.HASHHID_SALT)
    try:
        return hasher.decode(value)[0]
    except:
        return None


class IDConverter:
    """
    Converter to convert encoded id in url to integer id
    """
    regex = '[0-9a-zA-Z]{%d,}' % settings.HASHHID_MIN_LENGTH

    def to_python(self, value):
        return _decode(value)

    def to_url(self, value):
        return _encode(value)


class IdencodeField(serializers.CharField):
    """Encoded id field."""

    serializer = None
    related_model = None

    def __init__(self, serializer=None, related_model=None, *args, **kwargs):
        """Initializing field object."""
        self.serializer = serializer
        self.related_model = related_model
        super(IdencodeField, self).__init__(*args, **kwargs)

    def to_representation(self, value):
        """
        Override the returning method.

        This function will check if the serializer is supplied
        in case of foreign key field. In case of foreign key, the
        value will be and object. If it is  normal id then it is
        going to be type int.
        """
        if not value:
            return None
        if self.serializer:
            return self.serializer(value).data
        if isinstance(value, int):
            return _encode(value)
        try:
            return _encode(value.id)
        except:
            return None

    def to_internal_value(self, value):
        """To convert value for saving."""
        if self.related_model and isinstance(value, self.related_model):
            return value
        try:
            value = _decode(value) or int(value)
        except:
            value = float('-inf')
        if not value:
            raise serializers.ValidationError(
                'Invalid id/pk format')
        related_model = self.related_model
        if not related_model:
            try:
                related_model = self.parent.Meta.model._meta.get_field(
                    self.source).related_model
            except:
                raise serializers.ValidationError(
                    'Invalid key, the key should be same as the model. ')
        try:
            return related_model.objects.get(id=value)
        except:
            raise serializers.ValidationError('Invalid pk - object does not exist.')


def _success_response(data=None, message=None, status=status.HTTP_200_OK):
    """
    Function to create success Response.

    This function will create the standardized success response.
    """
    data = data if data else {}
    response = {
        'success': True,
        'detail': message,
        'code': status,
        'data': data
    }
    if not message:
        response['detail'] = 'Success.'
    return Response(response, status=status)


class UnauthorizedAccess(BaseAPIException):
    """user Authorization failed."""

    status_code = 401
    default_detail = 'User is not authorized to access.'
    default_code = 'unauthorized_access'
    send_to_sentry = False


class BadRequest(BaseAPIException):
    """Request method is invalid."""

    status_code = 400
    default_detail = 'Request details are invalid.'
    default_code = 'bad_request'
    send_to_sentry = True


class AccessForbidden(BaseAPIException):
    """User is not allowed to access."""

    status_code = 403
    default_detail = 'User access is forbidden.'
    default_code = 'access_forbidden'
    send_to_sentry = True