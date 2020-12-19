# Generated by Django 2.2.6 on 2020-12-19 05:51

from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('posts', '0026_auto_20201219_1027'),
    ]

    operations = [
        migrations.AddField(
            model_name='post',
            name='post_like',
            field=models.ManyToManyField(blank=True, related_name='post_liked', to=settings.AUTH_USER_MODEL),
        ),
    ]
