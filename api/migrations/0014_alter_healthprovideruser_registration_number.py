# Generated by Django 5.1.2 on 2024-10-26 11:16

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0013_alter_lesson_audio_file_alter_lesson_video_file'),
    ]

    operations = [
        migrations.AlterField(
            model_name='healthprovideruser',
            name='registration_number',
            field=models.CharField(max_length=10, unique=True, validators=[django.core.validators.RegexValidator(message='Registration number must be in the format: LICXXXRW to LICXXXXRW (e.g., LIC123RW, LIC1234RW, LIC123456RW)', regex='^LIC\\d{3,6}RW$')]),
        ),
    ]