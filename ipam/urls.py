"""URL configuration for the IPAM module."""

from django.urls import path

from . import views

app_name = 'ipam'

urlpatterns = [
    path('', views.IPAddressListView.as_view(), name='ipaddress-list'),
    path('novo/', views.IPAddressCreateView.as_view(), name='ipaddress-create'),
    path('<int:pk>/editar/', views.IPAddressUpdateView.as_view(), name='ipaddress-update'),
]
