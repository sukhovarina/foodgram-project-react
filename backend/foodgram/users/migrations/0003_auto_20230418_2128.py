# Generated by Django 3.2.18 on 2023-04-18 18:28

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0002_alter_follow_options'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='customuser',
            options={'verbose_name': 'Пользователь', 'verbose_name_plural': 'Пользователи'},
        ),
        migrations.AlterModelOptions(
            name='follow',
            options={'ordering': ('-author',), 'verbose_name': 'Подписки', 'verbose_name_plural': 'Подписки'},
        ),
    ]
