# Generated by Django 3.2.25 on 2024-08-01 09:31

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('QAS', '0011_auto_20240801_1638'),
    ]

    operations = [
        migrations.CreateModel(
            name='Questionmodel',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('question_text', models.CharField(max_length=100)),
                ('is_required', models.BooleanField(default=False)),
                ('review_setting', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='questions_group1', to='QAS.reviewsetting')),
            ],
        ),
    ]
