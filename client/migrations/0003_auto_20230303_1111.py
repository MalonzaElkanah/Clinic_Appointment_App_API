# Generated by Django 3.2.18 on 2023-03-03 11:11

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("client", "0002_auto_20230101_1642"),
    ]

    operations = [
        migrations.AlterField(
            model_name="activitylog",
            name="id",
            field=models.BigAutoField(
                auto_created=True, primary_key=True, serialize=False, verbose_name="ID"
            ),
        ),
        migrations.AlterField(
            model_name="myuser",
            name="id",
            field=models.BigAutoField(
                auto_created=True, primary_key=True, serialize=False, verbose_name="ID"
            ),
        ),
    ]