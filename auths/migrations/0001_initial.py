# Generated by Django 4.2.13 on 2024-05-09 15:17

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Account',
            fields=[
                ('customer_xid', models.UUIDField(primary_key=True, serialize=False)),
            ],
        ),
    ]