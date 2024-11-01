# Generated by Django 5.1.2 on 2024-11-01 06:55

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0018_examuseranswer_quizuseranswer_delete_useranswer'),
    ]

    operations = [
        migrations.AlterField(
            model_name='healthprovideruser',
            name='telephone',
            field=models.CharField(blank=True, max_length=15, null=True, unique=True),
        ),
        migrations.CreateModel(
            name='OneTimePassword',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('otp', models.CharField(max_length=6)),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
