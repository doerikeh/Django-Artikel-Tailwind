# Generated by Django 3.0.5 on 2020-06-17 07:20

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0003_artikel_tags'),
    ]

    operations = [
        migrations.AddField(
            model_name='tags',
            name='date_created',
            field=models.DateTimeField(auto_now_add=True, default=django.utils.timezone.now),
            preserve_default=False,
        ),
    ]
