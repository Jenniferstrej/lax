# -*- coding: utf-8 -*-
# Generated by Django 1.9 on 2016-04-05 16:04
from __future__ import unicode_literals

from django.db import migrations
from publisher import utils, logic

from . import to_dict, turn_off_auto_now, turn_off_auto_now_add

def populate(apps, schema_editor):
    "populate the ArticleVersion table with content"
    Article = apps.get_model("publisher", "Article")
    ArticleVersion = apps.get_model("publisher", "ArticleVersion")

    turn_off_auto_now_add(ArticleVersion, "datetime_record_created")
    turn_off_auto_now(ArticleVersion, "datetime_record_updated")
    
    attrs = [
        'doi',
        'version',
        'status',
        'datetime_published',
        'datetime_record_created',
        'datetime_record_updated'
    ]
    av_list = map(lambda art: ArticleVersion(**utils.subdict(to_dict(art), attrs)), Article.objects.all())
    ArticleVersion.objects.bulk_create(av_list)

def depopulate(apps, schema_editor):
    ArticleVersion = apps.get_model("publisher", "ArticleVersion")
    return ArticleVersion.objects.delete()

def prune_articles(apps, schema_editor):
    Article = apps.get_model("publisher", "Article")

    turn_off_auto_now_add(Article, "datetime_record_created")
    turn_off_auto_now(Article, "datetime_record_updated")
    
    for rawart in logic.not_latest_articles():
        art = Article.objects.get(pk=rawart.id)
        art.delete()

class Migration(migrations.Migration):

    dependencies = [
        ('publisher', '0010_articleversion'),
    ]

    operations = [
        migrations.RunPython(populate, depopulate),
        migrations.RunPython(prune_articles)
    ]
