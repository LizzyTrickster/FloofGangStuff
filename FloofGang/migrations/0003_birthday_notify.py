# Generated by Django 3.1.2 on 2020-10-27 00:11

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('FloofGang', '0002_auto_20201026_1136'),
    ]

    operations = [
        migrations.AddField(
            model_name='birthday',
            name='notify',
            field=models.BooleanField(default=False),
        ),
    ]
