# Generated by Django 4.1.4 on 2022-12-21 22:35

import contabilidade.models
from django.db import migrations
import stdimage.models


class Migration(migrations.Migration):

    dependencies = [
        ('contabilidade', '0002_alter_razao_options_alter_nota_contacredito_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='equipe',
            name='foto',
            field=stdimage.models.StdImageField(force_min_size=False, upload_to=contabilidade.models.get_file_path, variations={'thumb': {'crop': True, 'height': 480, 'width': 480}}, verbose_name='Foto'),
        ),
    ]
