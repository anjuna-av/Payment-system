""" Serializers for payment related APIs. """

from rest_framework import serializers
from v1.payment.models import Client
from v1.payment.models import Project
from v1.payment.models import Invoice
from common import library as custom_lib


class ClientSerializer(serializers.ModelSerializer):
    """ Serializer for client """
    id = custom_lib.IdencodeField(read_only=True)

    class Meta:
        model = Client
        fields = ('id', 'first_name', 'last_name', 'email')

    def create(self, validated_data):
        """Overriding the create method."""
        self.validate_username(validated_data['email'])
        if not 'username' in validated_data.keys() or not validated_data[
            'username']:
            validated_data['username'] = validated_data['email']
        validated_data['first_name'] = validated_data['first_name'].title()
        validated_data['last_name'] = validated_data['last_name'].title()
        extra_keys = list(
            set([field.name for field in Client._meta.get_fields()]) ^
            set([*validated_data]))

        custom_lib._pop_out_from_dictionary(validated_data, extra_keys)
        user = Client.objects.create(**validated_data)
        if 'password' in validated_data.keys():
            user.set_password(validated_data['password'])
            user.save()
        return user


class ProjectSerializer(serializers.ModelSerializer):
    """ Serializer for Project """
    id = custom_lib.IdencodeField(read_only=True)
    client = custom_lib.IdencodeField(
        related_model=Client, serializer=ClientSerializer)

    class Meta:
        model = Project
        fields = '__all__'


class InvoiceSerializer(serializers.ModelSerializer):
    """ Serializer for Invoice """
    id = custom_lib.IdencodeField(read_only=True)
    project = custom_lib.IdencodeField(
        related_model=Project, serializer=ProjectSerializer)

    class Meta:
        model = Invoice
        fields = '__all__'
