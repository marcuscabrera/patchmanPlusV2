"""Serializers for the IPAM REST API."""

from rest_framework import serializers

from .models import IPAddress


class IPAddressSerializer(serializers.ModelSerializer):
    """Serialize :class:`IPAddress` instances for REST consumption."""

    class Meta:
        model = IPAddress
        fields = ['id', 'address', 'status', 'description', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']
