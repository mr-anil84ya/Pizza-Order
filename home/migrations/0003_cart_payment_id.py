# Generated by Django 5.0.7 on 2024-07-26 11:23

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('home', '0002_cart_instamojo_id'),
    ]

    operations = [
        migrations.AddField(
            model_name='cart',
            name='payment_id',
            field=models.CharField(default='', max_length=100),
            preserve_default=False,
        ),
    ]
