# Generated by Django 3.2.8 on 2021-11-06 14:36

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('backend', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='reservation',
            name='professor',
            field=models.CharField(blank=True, max_length=3000, null=True),
        ),
    ]
