"""Database models for the IP address management (IPAM) module."""

from django.db import models
from django.urls import reverse


class IPAddress(models.Model):
    """Simple representation of an IP address and its allocation state."""

    STATUS_FREE = 'free'
    STATUS_RESERVED = 'reserved'
    STATUS_IN_USE = 'in_use'
    STATUS_CHOICES = (
        (STATUS_FREE, 'Livre'),
        (STATUS_RESERVED, 'Reservado'),
        (STATUS_IN_USE, 'Utilizado'),
    )

    address = models.GenericIPAddressField(
        unique=True,
        verbose_name='Endereço IP',
        help_text='Informe um endereço IPv4 ou IPv6 válido.',
    )
    status = models.CharField(
        max_length=16,
        choices=STATUS_CHOICES,
        default=STATUS_FREE,
        verbose_name='Status',
    )
    description = models.TextField(blank=True, verbose_name='Descrição')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Criado em')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Atualizado em')

    class Meta:
        ordering = ('address',)
        verbose_name = 'Endereço IP'
        verbose_name_plural = 'Endereços IP'

    def __str__(self) -> str:
        return self.address

    def get_absolute_url(self) -> str:
        """Return the canonical URL for the IP detail/edit page."""

        return reverse('ipam:ipaddress-update', kwargs={'pk': self.pk})
