# -*- coding: utf-8 -*-
# Generated by Django 1.9.12 on 2017-02-21 05:23
from __future__ import unicode_literals

import annoying.fields
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('publisher', '0034_auto_20170220_0714'),
    ]

    operations = [
        migrations.CreateModel(
            name='ArticleVersionExtRelation',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('uri', models.URLField(help_text='location of external object', max_length=2000)),
                ('citation', annoying.fields.JSONField(help_text='snippet of json describing the external link')),
                ('articleversion', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='publisher.ArticleVersion')),
            ],
        ),
        migrations.AlterUniqueTogether(
            name='articleversionextrelation',
            unique_together=set([('articleversion', 'uri')]),
        ),
    ]
