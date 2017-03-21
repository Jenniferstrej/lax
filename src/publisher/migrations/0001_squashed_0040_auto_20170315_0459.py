# -*- coding: utf-8 -*-
# Generated by Django 1.9.12 on 2017-03-21 01:06
from __future__ import unicode_literals

import annoying.fields
import autoslug.fields
from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    replaces = [('publisher', '0001_initial'), ('publisher', '0002_auto_20150806_2254'), ('publisher', '0003_auto_20150914_0955'), ('publisher', '0004_auto_20150917_0832'), ('publisher', '0005_auto_20150922_1307'), ('publisher', '0006_auto_20150922_1621'), ('publisher', '0007_auto_20150923_1519'), ('publisher', '0008_articlecorrection'), ('publisher', '0009_journal_inception'), ('publisher', '0010_articleversion'), ('publisher', '0011_auto_20160405_1628'), ('publisher', '0012_auto_20160405_1746'), ('publisher', '0013_auto_20160411_1143'), ('publisher', '0014_auto_20160411_1145'), ('publisher', '0015_auto_20160412_1021'), ('publisher', '0016_auto_20160905_1603'), ('publisher', '0017_remove_article_datetime_submitted'), ('publisher', '0018_auto_20160906_1018'), ('publisher', '0019_remove_article_website_path'), ('publisher', '0020_auto_20160908_1806'), ('publisher', '0021_auto_20160913_1454'), ('publisher', '0022_auto_20160926_1010'), ('publisher', '0023_auto_20160926_1038'), ('publisher', '0024_auto_20161006_1745'), ('publisher', '0025_auto_20161011_1330'), ('publisher', '0026_articlefragment'), ('publisher', '0027_auto_20161011_1539'), ('publisher', '0028_auto_20161011_1627'), ('publisher', '0029_auto_20161014_1533'), ('publisher', '0030_auto_20161216_1154'), ('publisher', '0031_auto_20170109_1514'), ('publisher', '0032_auto_20170110_1414'), ('publisher', '0033_auto_20170115_1343'), ('publisher', '0034_auto_20170220_0714'), ('publisher', '0035_auto_20170221_0523'), ('publisher', '0036_auto_20170221_0559'), ('publisher', '0037_auto_20170228_2318'), ('publisher', '0038_auto_20170302_2304'), ('publisher', '0039_auto_20170303_0029'), ('publisher', '0040_auto_20170315_0459')]

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Article',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('doi', models.CharField(help_text=b"Article's unique ID in the wider world. All articles must have one as an absolute minimum", max_length=255, unique=True)),
                ('title', models.CharField(blank=True, help_text=b'The title of the article', max_length=255, null=True)),
                ('slug', autoslug.fields.AutoSlugField(blank=True, editable=False, help_text=b'A friendlier version of the title for machines', null=True, populate_from=b'title')),
                ('version', models.PositiveSmallIntegerField(default=1, help_text=b'The version of the article. All articles have at least a version 1')),
                ('volume', models.PositiveSmallIntegerField(blank=True, null=True)),
                ('status', models.CharField(blank=True, choices=[(b'poa', b'POA'), (b'vor', b'VOR')], max_length=3, null=True)),
                ('website_path', models.CharField(max_length=50)),
                ('datetime_submitted', models.DateTimeField(blank=True, help_text=b'Date author submitted article', null=True)),
                ('datetime_accepted', models.DateTimeField(blank=True, help_text=b'Date article accepted for publication', null=True)),
                ('datetime_published', models.DateTimeField(blank=True, help_text=b'Date article first appeared on website', null=True)),
                ('datetime_record_created', models.DateTimeField(auto_now_add=True, help_text=b'Date this article was created')),
                ('datetime_record_updated', models.DateTimeField(auto_now=True, help_text=b'Date this article was updated')),
            ],
        ),

        migrations.CreateModel(
            name='Journal',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(help_text=b'Name of the journal.', max_length=255)),
            ],
        ),
        migrations.CreateModel(
            name='Publisher',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255)),
            ],
        ),
        migrations.AddField(
            model_name='journal',
            name='publisher',
            field=models.ForeignKey(help_text="A publisher may have many journals. A journal doesn't necessarily need a Publisher.", null=True, on_delete=django.db.models.deletion.CASCADE, to='publisher.Publisher'),
        ),
        migrations.AddField(
            model_name='article',
            name='journal',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='publisher.Journal'),
        ),
        migrations.AddField(
            model_name='article',
            name='type',
            field=models.CharField(blank=True, max_length=50, null=True),
        ),
        migrations.AlterField(
            model_name='article',
            name='doi',
            field=models.CharField(help_text=b"Article's unique ID in the wider world. All articles must have one as an absolute minimum", max_length=255),
        ),
        migrations.AlterField(
            model_name='article',
            name='slug',
            field=autoslug.fields.AutoSlugField(always_update=True, blank=True, editable=False, help_text=b'A friendlier version of the title for machines', null=True, populate_from=b'title'),
        ),
        migrations.AlterField(
            model_name='article',
            name='version',
            field=models.PositiveSmallIntegerField(default=0, help_text=b'The version of the article. Version=0 means pre-publication'),
        ),
        migrations.AlterUniqueTogether(
            name='article',
            unique_together=set([('doi', 'version')]),
        ),
        migrations.AlterField(
            model_name='article',
            name='version',
            field=models.PositiveSmallIntegerField(default=None, help_text=b'The version of the article. Version=None means pre-publication'),
        ),
        migrations.AlterModelOptions(
            name='article',
            options={'ordering': ('version',)},
        ),
        migrations.AddField(
            model_name='journal',
            name='inception',
            field=models.DateTimeField(blank=True, help_text='Date journal was created.', null=True),
        ),
        migrations.CreateModel(
            name='ArticleVersion',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(blank=True, help_text=b'The title of the article', max_length=255, null=True)),
                ('doi', models.CharField(help_text=b"Article's unique ID in the wider world. All articles must have one as an absolute minimum", max_length=255)),
                ('version', models.PositiveSmallIntegerField(default=None, help_text=b'The version of the article. Version=None means pre-publication')),
                ('status', models.CharField(blank=True, choices=[(b'poa', b'POA'), (b'vor', b'VOR')], max_length=3, null=True)),
                ('datetime_published', models.DateTimeField(blank=True, help_text=b'Date article first appeared on website', null=True)),
                ('datetime_record_created', models.DateTimeField(auto_now_add=True, help_text=b'Date this article was created')),
                ('datetime_record_updated', models.DateTimeField(auto_now=True, help_text=b'Date this article was updated')),
            ],
        ),
        migrations.AlterModelOptions(
            name='article',
            options={},
        ),
        migrations.AlterField(
            model_name='article',
            name='doi',
            field=models.CharField(help_text=b"Article's unique ID in the wider world. All articles must have one as an absolute minimum", max_length=255, unique=True),
        ),
        migrations.AlterUniqueTogether(
            name='article',
            unique_together=set([]),
        ),
        migrations.RemoveField(
            model_name='article',
            name='datetime_published',
        ),
        migrations.RemoveField(
            model_name='article',
            name='version',
        ),
        migrations.RemoveField(
            model_name='article',
            name='status',
        ),
        migrations.RemoveField(
            model_name='article',
            name='title',
        ),
        migrations.RemoveField(
            model_name='article',
            name='slug',
        ),
        migrations.AddField(
            model_name='articleversion',
            name='article',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, to='publisher.Article'),
            preserve_default=False,
        ),
        migrations.RemoveField(
            model_name='ArticleVersion',
            name='doi',
        ),
        migrations.AddField(
            model_name='articleversion',
            name='article_json_v1',
            field=annoying.fields.JSONField(blank=True, help_text=b'Valid article-json.', null=True),
        ),
        migrations.AddField(
            model_name='articleversion',
            name='article_json_v1_snippet',
            field=annoying.fields.JSONField(blank=True, help_text=b'Valid article-json snippet, extracted from the valid article-json', null=True),
        ),
        migrations.AlterUniqueTogether(
            name='articleversion',
            unique_together=set([('article', 'version')]),
        ),
        migrations.RemoveField(
            model_name='article',
            name='datetime_accepted',
        ),
        migrations.AddField(
            model_name='article',
            name='date_full_decision',
            field=models.DateField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='article',
            name='date_full_qc',
            field=models.DateField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='article',
            name='date_initial_decision',
            field=models.DateField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='article',
            name='date_initial_qc',
            field=models.DateField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='article',
            name='date_rev1_decision',
            field=models.DateField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='article',
            name='date_rev1_qc',
            field=models.DateField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='article',
            name='date_rev2_decision',
            field=models.DateField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='article',
            name='date_rev2_qc',
            field=models.DateField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='article',
            name='date_rev3_decision',
            field=models.DateField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='article',
            name='date_rev3_qc',
            field=models.DateField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='article',
            name='date_rev4_decision',
            field=models.DateField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='article',
            name='date_rev4_qc',
            field=models.DateField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='article',
            name='decision',
            field=models.CharField(blank=True, choices=[(b'RJI', b'Reject Initial Submission'), (b'RJF', b'Reject Full Submission'), (b'RVF', b'Revise Full Submission'), (b'AF', b'Accept Full Submission'), (b'EF', b'Encourage Full Submission'), (b'SW', b'Simple Withdraw')], max_length=25, null=True),
        ),
        migrations.AddField(
            model_name='article',
            name='ejp_type',
            field=models.CharField(blank=True, choices=[(b'RA', b'Research article'), (b'SR', b'Short report'), (b'AV', b'Research advance'), (b'RR', b'Registered report'), (b'TR', b'Tools and resources')], help_text=b'article as exported from EJP submission system', max_length=3, null=True),
        ),
        migrations.AddField(
            model_name='article',
            name='initial_decision',
            field=models.CharField(blank=True, choices=[(b'RJI', b'Reject Initial Submission'), (b'RJF', b'Reject Full Submission'), (b'RVF', b'Revise Full Submission'), (b'AF', b'Accept Full Submission'), (b'EF', b'Encourage Full Submission'), (b'SW', b'Simple Withdraw')], max_length=25, null=True),
        ),
        migrations.AddField(
            model_name='article',
            name='rev1_decision',
            field=models.CharField(blank=True, choices=[(b'RJI', b'Reject Initial Submission'), (b'RJF', b'Reject Full Submission'), (b'RVF', b'Revise Full Submission'), (b'AF', b'Accept Full Submission'), (b'EF', b'Encourage Full Submission'), (b'SW', b'Simple Withdraw')], max_length=25, null=True),
        ),
        migrations.AddField(
            model_name='article',
            name='rev2_decision',
            field=models.CharField(blank=True, choices=[(b'RJI', b'Reject Initial Submission'), (b'RJF', b'Reject Full Submission'), (b'RVF', b'Revise Full Submission'), (b'AF', b'Accept Full Submission'), (b'EF', b'Encourage Full Submission'), (b'SW', b'Simple Withdraw')], max_length=25, null=True),
        ),
        migrations.AddField(
            model_name='article',
            name='rev3_decision',
            field=models.CharField(blank=True, choices=[(b'RJI', b'Reject Initial Submission'), (b'RJF', b'Reject Full Submission'), (b'RVF', b'Revise Full Submission'), (b'AF', b'Accept Full Submission'), (b'EF', b'Encourage Full Submission'), (b'SW', b'Simple Withdraw')], max_length=25, null=True),
        ),
        migrations.AddField(
            model_name='article',
            name='rev4_decision',
            field=models.CharField(blank=True, choices=[(b'RJI', b'Reject Initial Submission'), (b'RJF', b'Reject Full Submission'), (b'RVF', b'Revise Full Submission'), (b'AF', b'Accept Full Submission'), (b'EF', b'Encourage Full Submission'), (b'SW', b'Simple Withdraw')], max_length=25, null=True),
        ),
        migrations.AlterField(
            model_name='article',
            name='type',
            field=models.CharField(blank=True, help_text=b'xml article-type.', max_length=50, null=True),
        ),
        migrations.AddField(
            model_name='article',
            name='manuscript_id',
            field=models.PositiveIntegerField(help_text=b'article identifier from beginning of submission process right through to end of publication.', unique=True),
        ),
        migrations.AlterModelOptions(
            name='article',
            options={'ordering': ('-date_initial_qc',)},
        ),
        migrations.RemoveField(
            model_name='article',
            name='datetime_submitted',
        ),
        migrations.RemoveField(
            model_name='article',
            name='website_path',
        ),
        migrations.AlterField(
            model_name='journal',
            name='name',
            field=models.CharField(help_text=b'Name of the journal.', max_length=255, unique=True),
        ),
        migrations.CreateModel(
            name='ArticleFragment',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('fragment', annoying.fields.JSONField(help_text=b'partial piece of article data to be merged in')),
                ('article', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='publisher.Article')),
                ('position', models.PositiveSmallIntegerField(default=1, help_text=b'position in the merge order with lower fragments merged first')),
                ('type', models.CharField(default=None, help_text=b'the type of fragment, eg "xml", "content-header", etc', max_length=25, unique=True)),
                ('datetime_record_created', models.DateTimeField(auto_now_add=True, default=None)),
                ('version', models.PositiveSmallIntegerField(help_text=b'does the fragment apply to all articles or a specific version?', null=True)),
            ],
        ),
        migrations.AlterUniqueTogether(
            name='articlefragment',
            unique_together=set([('article', 'type')]),
        ),
        migrations.AlterField(
            model_name='articlefragment',
            name='type',
            field=models.CharField(help_text=b'the type of fragment, eg "xml", "content-header", etc', max_length=25),
        ),
        migrations.AlterUniqueTogether(
            name='articlefragment',
            unique_together=set([('article', 'type', 'version')]),
        ),
        migrations.AlterField(
            model_name='articlefragment',
            name='article',
            field=models.ForeignKey(help_text=b'all fragments belong to an article, only some fragments belong to an article version', on_delete=django.db.models.deletion.CASCADE, to='publisher.Article'),
        ),
        migrations.AlterField(
            model_name='articlefragment',
            name='version',
            field=models.PositiveSmallIntegerField(help_text=b'if null, fragment applies only to a specific version of article', null=True),
        ),
        migrations.AlterModelOptions(
            name='articleversion',
            options={'ordering': ('datetime_published',)},
        ),
        migrations.AlterModelOptions(
            name='articleversion',
            options={'ordering': ('version',)},
        ),
        migrations.AlterField(
            model_name='article',
            name='manuscript_id',
            field=models.BigIntegerField(help_text=b'article identifier from beginning of submission process right through to end of publication.', unique=True),
        ),
        migrations.AlterField(
            model_name='article',
            name='datetime_record_created',
            field=models.DateTimeField(auto_now_add=True, help_text='Date this article was created'),
        ),
        migrations.AlterField(
            model_name='article',
            name='datetime_record_updated',
            field=models.DateTimeField(auto_now=True, help_text='Date this article was updated'),
        ),
        migrations.AlterField(
            model_name='article',
            name='decision',
            field=models.CharField(blank=True, choices=[('RJI', 'Reject Initial Submission'), ('RJF', 'Reject Full Submission'), ('RVF', 'Revise Full Submission'), ('AF', 'Accept Full Submission'), ('EF', 'Encourage Full Submission'), ('SW', 'Simple Withdraw')], max_length=25, null=True),
        ),
        migrations.AlterField(
            model_name='article',
            name='doi',
            field=models.CharField(help_text="Article's unique ID in the wider world. All articles must have one as an absolute minimum", max_length=255, unique=True),
        ),
        migrations.AlterField(
            model_name='article',
            name='ejp_type',
            field=models.CharField(blank=True, choices=[('RA', 'Research article'), ('SR', 'Short report'), ('AV', 'Research advance'), ('RR', 'Registered report'), ('TR', 'Tools and resources')], help_text='article as exported from EJP submission system', max_length=3, null=True),
        ),
        migrations.AlterField(
            model_name='article',
            name='initial_decision',
            field=models.CharField(blank=True, choices=[('RJI', 'Reject Initial Submission'), ('RJF', 'Reject Full Submission'), ('RVF', 'Revise Full Submission'), ('AF', 'Accept Full Submission'), ('EF', 'Encourage Full Submission'), ('SW', 'Simple Withdraw')], max_length=25, null=True),
        ),
        migrations.AlterField(
            model_name='article',
            name='manuscript_id',
            field=models.BigIntegerField(help_text='article identifier from beginning of submission process right through to end of publication.', unique=True),
        ),
        migrations.AlterField(
            model_name='article',
            name='rev1_decision',
            field=models.CharField(blank=True, choices=[('RJI', 'Reject Initial Submission'), ('RJF', 'Reject Full Submission'), ('RVF', 'Revise Full Submission'), ('AF', 'Accept Full Submission'), ('EF', 'Encourage Full Submission'), ('SW', 'Simple Withdraw')], max_length=25, null=True),
        ),
        migrations.AlterField(
            model_name='article',
            name='rev2_decision',
            field=models.CharField(blank=True, choices=[('RJI', 'Reject Initial Submission'), ('RJF', 'Reject Full Submission'), ('RVF', 'Revise Full Submission'), ('AF', 'Accept Full Submission'), ('EF', 'Encourage Full Submission'), ('SW', 'Simple Withdraw')], max_length=25, null=True),
        ),
        migrations.AlterField(
            model_name='article',
            name='rev3_decision',
            field=models.CharField(blank=True, choices=[('RJI', 'Reject Initial Submission'), ('RJF', 'Reject Full Submission'), ('RVF', 'Revise Full Submission'), ('AF', 'Accept Full Submission'), ('EF', 'Encourage Full Submission'), ('SW', 'Simple Withdraw')], max_length=25, null=True),
        ),
        migrations.AlterField(
            model_name='article',
            name='rev4_decision',
            field=models.CharField(blank=True, choices=[('RJI', 'Reject Initial Submission'), ('RJF', 'Reject Full Submission'), ('RVF', 'Revise Full Submission'), ('AF', 'Accept Full Submission'), ('EF', 'Encourage Full Submission'), ('SW', 'Simple Withdraw')], max_length=25, null=True),
        ),
        migrations.AlterField(
            model_name='article',
            name='type',
            field=models.CharField(blank=True, help_text='xml article-type.', max_length=50, null=True),
        ),
        migrations.AlterField(
            model_name='articlefragment',
            name='article',
            field=models.ForeignKey(help_text='all fragments belong to an article, only some fragments belong to an article version', on_delete=django.db.models.deletion.CASCADE, to='publisher.Article'),
        ),
        migrations.AlterField(
            model_name='articlefragment',
            name='fragment',
            field=annoying.fields.JSONField(help_text='partial piece of article data to be merged in'),
        ),
        migrations.AlterField(
            model_name='articlefragment',
            name='position',
            field=models.PositiveSmallIntegerField(default=1, help_text='position in the merge order with lower fragments merged first'),
        ),
        migrations.AlterField(
            model_name='articlefragment',
            name='type',
            field=models.CharField(help_text='the type of fragment, eg "xml", "content-header", etc', max_length=25),
        ),
        migrations.AlterField(
            model_name='articlefragment',
            name='version',
            field=models.PositiveSmallIntegerField(help_text='if null, fragment applies only to a specific version of article', null=True),
        ),
        migrations.AlterField(
            model_name='articleversion',
            name='article_json_v1',
            field=annoying.fields.JSONField(blank=True, help_text='Valid article-json.', null=True),
        ),
        migrations.AlterField(
            model_name='articleversion',
            name='article_json_v1_snippet',
            field=annoying.fields.JSONField(blank=True, help_text='Valid article-json snippet, extracted from the valid article-json', null=True),
        ),
        migrations.AlterField(
            model_name='articleversion',
            name='datetime_published',
            field=models.DateTimeField(blank=True, help_text='Date article first appeared on website', null=True),
        ),
        migrations.AlterField(
            model_name='articleversion',
            name='datetime_record_created',
            field=models.DateTimeField(auto_now_add=True, help_text='Date this article was created'),
        ),
        migrations.AlterField(
            model_name='articleversion',
            name='datetime_record_updated',
            field=models.DateTimeField(auto_now=True, help_text='Date this article was updated'),
        ),
        migrations.AlterField(
            model_name='articleversion',
            name='status',
            field=models.CharField(blank=True, choices=[('poa', 'POA'), ('vor', 'VOR')], max_length=3, null=True),
        ),
        migrations.AlterField(
            model_name='articleversion',
            name='title',
            field=models.CharField(blank=True, help_text='The title of the article', max_length=255, null=True),
        ),
        migrations.AlterField(
            model_name='articleversion',
            name='version',
            field=models.PositiveSmallIntegerField(default=None, help_text='The version of the article. Version=None means pre-publication'),
        ),
        migrations.AlterField(
            model_name='journal',
            name='name',
            field=models.CharField(help_text='Name of the journal.', max_length=255, unique=True),
        ),
        migrations.CreateModel(
            name='ArticleVersionRelation',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('articleversion', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='publisher.ArticleVersion')),
                ('related_to', models.ForeignKey(help_text='the Article this ArticleVersion is related to', on_delete=django.db.models.deletion.CASCADE, to='publisher.Article')),
            ],
        ),
        migrations.AlterUniqueTogether(
            name='articleversionrelation',
            unique_together=set([('articleversion', 'related_to')]),
        ),
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
        migrations.AlterField(
            model_name='articlefragment',
            name='version',
            field=models.PositiveSmallIntegerField(blank=True, help_text='if null, fragment applies only to a specific version of article', null=True),
        ),
        migrations.AlterField(
            model_name='article',
            name='ejp_type',
            field=models.CharField(blank=True, choices=[('RA', 'Research article'), ('SR', 'Short report'), ('AV', 'Research advance'), ('RR', 'Registered report'), ('TR', 'Tools and resources'), ('RE', 'Unknown')], help_text='article as exported from EJP submission system', max_length=3, null=True),
        ),
        migrations.AlterField(
            model_name='article',
            name='ejp_type',
            field=models.CharField(blank=True, choices=[('RA', 'Research article'), ('SR', 'Short report'), ('AV', 'Research advance'), ('RR', 'Registered report'), ('TR', 'Tools and resources'), ('RE', 'Research exchange'), ('RS', 'Unknown')], help_text='article as exported from EJP submission system', max_length=3, null=True),
        ),
        migrations.AlterField(
            model_name='article',
            name='ejp_type',
            field=models.CharField(blank=True, choices=[('RA', 'Research article'), ('SR', 'Short report'), ('AV', 'Research advance'), ('RR', 'Registered report'), ('TR', 'Tools and resources'), ('RE', 'Research exchange'), ('RS', 'Replication Study')], help_text='article as exported from EJP submission system', max_length=3, null=True),
        ),
        migrations.AlterModelOptions(
            name='articlefragment',
            options={'ordering': ('position', 'datetime_record_created')},
        ),
    ]
