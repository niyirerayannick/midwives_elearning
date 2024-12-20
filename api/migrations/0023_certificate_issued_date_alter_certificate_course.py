# Generated by Django 5.1.2 on 2024-11-02 19:49

import django.db.models.deletion
import django.utils.timezone
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0022_remove_certificate_certificate_file_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='certificate',
            name='issued_date',
            field=models.DateField(default=django.utils.timezone.now),
        ),
        migrations.AlterField(
            model_name='certificate',
            name='course',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='api.course'),
        ),
    ]
