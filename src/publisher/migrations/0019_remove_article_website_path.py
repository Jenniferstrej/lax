# -*- coding: utf-8 -*-
# Generated by Django 1.9 on 2016-09-07 10:18


from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('publisher', '0018_auto_20160906_1018'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='article',
            name='website_path',
        ),
    ]
