# Generated by Django 4.2 on 2023-04-29 11:56

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('orders', '0002_orderitem_stripe_id'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='orderitem',
            name='stripe_id',
        ),
        migrations.AddField(
            model_name='order',
            name='stripe_id',
            field=models.CharField(blank=True, max_length=250),
        ),
    ]
