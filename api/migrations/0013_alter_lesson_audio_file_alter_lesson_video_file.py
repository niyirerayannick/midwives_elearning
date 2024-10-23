# Generated by Django 5.1.2 on 2024-10-23 21:47

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0012_grade_update_alter_lesson_options_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='lesson',
            name='audio_file',
            field=models.FileField(blank=True, help_text='Optional audio file for the lesson', null=True, upload_to='lessons/audios/', verbose_name='Audio File'),
        ),
        migrations.AlterField(
            model_name='lesson',
            name='video_file',
            field=models.FileField(blank=True, help_text='Optional video file for the lesson', null=True, upload_to='lessons/videos/', verbose_name='Video File'),
        ),
    ]
