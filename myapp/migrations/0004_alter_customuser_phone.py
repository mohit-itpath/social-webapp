# Generated by Django 4.2 on 2023-04-20 12:22

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('myapp', '0003_alter_customuser_dob_alter_customuser_phone'),
    ]

    operations = [
        migrations.AlterField(
            model_name='customuser',
            name='phone',
            field=models.CharField(max_length=10, null=True),
        ),
    ]
