# Generated by Django 2.2.4 on 2019-08-26 13:02

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('weather', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='sensortype',
            name='average',
            field=models.BooleanField(default=True, verbose_name='Calculate average for this type'),
        ),
    ]