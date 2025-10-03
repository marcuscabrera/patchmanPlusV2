"""Views for the IPAM module covering REST and traditional interfaces."""

from django.contrib import messages
from django.urls import reverse_lazy
from django.utils.translation import gettext_lazy as _
from django.views import generic

from django_filters import rest_framework as django_filters
from rest_framework import filters, viewsets

from .forms import IPAddressForm
from .models import IPAddress
from .serializers import IPAddressSerializer


class IPAddressViewSet(viewsets.ModelViewSet):
    """API endpoint that allows IP addresses to be CRUDed."""

    queryset = IPAddress.objects.all()
    serializer_class = IPAddressSerializer
    filterset_fields = ['status']
    search_fields = ['address', 'description']
    ordering_fields = ['address', 'status', 'created_at']
    ordering = ['address']
    filter_backends = [filters.OrderingFilter, filters.SearchFilter, django_filters.DjangoFilterBackend]


class IPAddressListView(generic.ListView):
    """Render a simple table with all IP addresses."""

    template_name = 'ipam/ipaddress_list.html'
    model = IPAddress
    context_object_name = 'ip_addresses'
    paginate_by = 25


class IPAddressCreateView(generic.CreateView):
    """Handle the creation of IP addresses via a basic form."""

    template_name = 'ipam/ipaddress_form.html'
    form_class = IPAddressForm
    success_url = reverse_lazy('ipam:ipaddress-list')

    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, _('Endereço IP criado com sucesso.'))
        return response


class IPAddressUpdateView(generic.UpdateView):
    """Allow editing an IP address from the browser."""

    template_name = 'ipam/ipaddress_form.html'
    form_class = IPAddressForm
    model = IPAddress
    success_url = reverse_lazy('ipam:ipaddress-list')

    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, _('Endereço IP atualizado com sucesso.'))
        return response
