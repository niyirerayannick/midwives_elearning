# Generated by Django 5.1.2 on 2024-11-07 08:26

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0024_remove_progress_completed_lessons_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='enrollment',
            name='completion_status',
            field=models.CharField(choices=[('in_progress', 'In Progress'), ('completed', 'Completed')], default=0, max_length=50),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='exam',
            name='is_completed',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='lesson',
            name='is_completed',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='quiz',
            name='is_completed',
            field=models.BooleanField(default=False),
        ),
        migrations.AlterField(
            model_name='examuseranswer',
            name='question',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='api.examquestion'),
        ),
        migrations.AlterField(
            model_name='examuseranswer',
            name='selected_answer',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='api.examanswer'),
        ),
    ]
