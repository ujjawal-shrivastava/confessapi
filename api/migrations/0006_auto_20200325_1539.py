# Generated by Django 3.0.4 on 2020-03-25 10:09

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0005_confession_confid'),
    ]

    operations = [
        migrations.AlterField(
            model_name='confession',
            name='confId',
            field=models.CharField(editable=False, max_length=10, unique=True),
        ),
    ]
