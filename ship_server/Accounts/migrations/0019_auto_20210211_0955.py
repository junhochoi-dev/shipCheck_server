# Generated by Django 2.2.4 on 2021-02-11 09:55

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Accounts', '0018_auto_20210211_0955'),
    ]

    operations = [
        migrations.AlterField(
            model_name='account',
            name='regit_date',
            field=models.DateField(default=datetime.datetime(2021, 2, 11, 9, 55, 44, 371085)),
        ),
    ]
