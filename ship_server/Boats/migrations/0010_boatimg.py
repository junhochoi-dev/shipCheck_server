# Generated by Django 2.2.4 on 2021-01-21 11:34

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('Boats', '0009_auto_20201223_1328'),
    ]

    operations = [
        migrations.CreateModel(
            name='BoatImg',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('img', models.ImageField(blank=True, null=True, upload_to='boat_img')),
                ('lon', models.FloatField(default=0)),
                ('lat', models.FloatField(default=0)),
                ('point', models.TextField()),
                ('s_id', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='boat', to='Boats.Boat')),
            ],
        ),
    ]
