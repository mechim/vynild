# Generated by Django 5.1.1 on 2024-10-04 07:55

import releases.models
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Release',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('release_name', models.CharField(max_length=150)),
                ('artist_name', models.CharField(max_length=150)),
                ('discussion_identifier', models.CharField(default=releases.models.Release.generate_identifier, max_length=8, unique=True)),
            ],
        ),
    ]
