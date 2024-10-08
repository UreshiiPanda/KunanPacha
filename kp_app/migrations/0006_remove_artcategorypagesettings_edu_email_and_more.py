# Generated by Django 5.0.2 on 2024-09-29 16:17

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('kp_app', '0005_alter_artwork_category'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='artcategorypagesettings',
            name='edu_email',
        ),
        migrations.AddField(
            model_name='homepage2settings',
            name='homepage2_text_bottom',
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='homepage2settings',
            name='homepage2_title',
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
        migrations.AddField(
            model_name='homepage4settings',
            name='homepage4_text_left',
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='homepage4settings',
            name='homepage4_text_right',
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='homepage4settings',
            name='homepage4_title',
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
    ]
