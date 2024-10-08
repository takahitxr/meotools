# Generated by Django 3.2.25 on 2024-07-31 07:15

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('QAS', '0007_alter_reviewsetting_user'),
    ]

    operations = [
        migrations.AlterField(
            model_name='reviewsetting',
            name='dissatisfied_redirect_url',
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
        migrations.AlterField(
            model_name='reviewsetting',
            name='neutral_redirect_url',
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
        migrations.AlterField(
            model_name='reviewsetting',
            name='satisfied_redirect_url',
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
        migrations.AlterField(
            model_name='reviewsetting',
            name='very_dissatisfied_redirect_url',
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
        migrations.AlterField(
            model_name='reviewsetting',
            name='very_satisfied_redirect_url',
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
    ]
