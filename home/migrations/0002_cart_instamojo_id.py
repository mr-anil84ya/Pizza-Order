# Generated by Django 5.0.7 on 2024-07-26 08:44

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('home', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='cart',
            name='instamojo_id',
            field=models.CharField(default='', max_length=1000),
            preserve_default=False,
        ),
    ]
