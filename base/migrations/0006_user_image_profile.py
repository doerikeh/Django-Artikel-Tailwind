# Generated by Django 3.0.5 on 2020-06-18 02:12

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0005_auto_20200617_2120'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='image_profile',
            field=models.ImageField(default=django.utils.timezone.now, upload_to='profile/'),
            preserve_default=False,
        ),
    ]