# Generated by Django 5.0.2 on 2024-09-07 17:16

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("kp_app", "0002_blogpagesettings_blogpost"),
    ]

    operations = [
        migrations.CreateModel(
            name="ArtCategory",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("name", models.CharField(max_length=100)),
                ("image_filename", models.CharField(max_length=255)),
            ],
        ),
        migrations.AddField(
            model_name="artwork",
            name="category",
            field=models.ForeignKey(
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="artworks",
                to="kp_app.artcategory",
            ),
        ),
    ]
