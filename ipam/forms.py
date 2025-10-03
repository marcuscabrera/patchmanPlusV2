"""Forms used by the IP address management module."""

from django import forms

from .models import IPAddress


class IPAddressForm(forms.ModelForm):
    """Model form that exposes the essential fields for CRUD operations."""

    class Meta:
        model = IPAddress
        fields = ['address', 'status', 'description']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 3}),
        }
        help_texts = {
            'address': 'Suporta endereços IPv4 e IPv6.',
        }
