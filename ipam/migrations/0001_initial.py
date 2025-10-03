# Generated manually to introduce the IPAddress model.

from django.db import migrations, models


class Migration(migrations.Migration):
    """Create the IPAddress table with basic metadata fields."""

    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name='IPAddress',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('address', models.GenericIPAddressField(help_text='Informe um endereço IPv4 ou IPv6 válido.', unique=True, verbose_name='Endereço IP')),
                ('status', models.CharField(choices=[('free', 'Livre'), ('reserved', 'Reservado'), ('in_use', 'Utilizado')], default='free', max_length=16, verbose_name='Status')),
                ('description', models.TextField(blank=True, verbose_name='Descrição')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='Criado em')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='Atualizado em')),
            ],
            options={
                'ordering': ('address',),
                'verbose_name': 'Endereço IP',
                'verbose_name_plural': 'Endereços IP',
            },
        ),
    ]
