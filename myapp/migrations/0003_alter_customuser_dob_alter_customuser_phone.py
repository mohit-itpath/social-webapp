# Generated by Django 4.2 on 2023-04-20 09:27

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('myapp', '0002_customuser_is_staff'),
    ]

    operations = [
        migrations.AlterField(
            model_name='customuser',
            name='dob',
            field=models.DateField(null=True),
        ),
        migrations.AlterField(
            model_name='customuser',
            name='phone',
            field=models.IntegerField(null=True),
        ),
    ]
