# Generated by Django 3.0.8 on 2020-07-21 20:20

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('salam', '0003_auto_20200721_0931'),
    ]

    operations = [
        migrations.AddField(
            model_name='order',
            name='side',
            field=models.CharField(choices=[('BUY', 'BUY'), ('SELL', 'SELL')], default='BUY', max_length=4, verbose_name='Trade Side'),
            preserve_default=False,
        ),
    ]
