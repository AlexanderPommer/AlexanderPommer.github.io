# Generated by Django 4.1 on 2023-04-01 10:39

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('board', '0004_alter_match_winner'),
    ]

    operations = [
        migrations.AddField(
            model_name='match',
            name='bk_can_castle',
            field=models.CharField(default='b', max_length=1),
        ),
        migrations.AddField(
            model_name='match',
            name='bk_check',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='match',
            name='en_passant',
            field=models.CharField(default='', max_length=8),
        ),
        migrations.AddField(
            model_name='match',
            name='wk_can_castle',
            field=models.CharField(default='b', max_length=1),
        ),
        migrations.AddField(
            model_name='match',
            name='wk_check',
            field=models.BooleanField(default=False),
        ),
    ]
