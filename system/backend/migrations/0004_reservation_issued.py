# Generated by Django 3.2.8 on 2021-10-23 16:45

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('backend', '0003_alter_reservation_returned'),
    ]

    operations = [
        migrations.AddField(
            model_name='reservation',
            name='issued',
            field=models.IntegerField(default=0),
        ),
    ]
