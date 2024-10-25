# Generated by Django 5.1.1 on 2024-10-04 07:55

import django.core.validators
import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('releases', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Review',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('user_id', models.IntegerField()),
                ('review_text', models.CharField(blank=True, default='', max_length=255)),
                ('review_mark', models.IntegerField(validators=[django.core.validators.MinValueValidator(1), django.core.validators.MaxValueValidator(10)])),
                ('release', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='reviews', to='releases.release')),
            ],
        ),
    ]
