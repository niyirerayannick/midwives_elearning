# Generated by Django 5.0.3 on 2024-10-10 22:14

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0004_lesson_video_url'),
    ]

    operations = [
        migrations.AddField(
            model_name='lesson',
            name='pdf_file',
            field=models.FileField(blank=True, null=True, upload_to='lessons/pdfs/'),
        ),
    ]
