# Generated by Django 3.2.25 on 2024-09-02 07:25

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('QAS', '0028_alter_autoresponse_filter_text'),
    ]

    operations = [
        migrations.AddField(
            model_name='autoresponse',
            name='bool_text',
            field=models.BooleanField(blank=True, default=False),
        ),
    ]
