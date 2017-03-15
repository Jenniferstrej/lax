# -*- coding: utf-8 -*-
from functools import partial
import copy
from os.path import join
import json
from datetime import datetime, timedelta
from .base import BaseCase
from publisher import ajson_ingestor, models, utils
from publisher.ajson_ingestor import StateError
from publisher.utils import lmap
from unittest import skip
from jsonschema.exceptions import ValidationError
from publisher import logic
from django.test import Client, override_settings
from django.core.urlresolvers import reverse

class Ingest(BaseCase):
    def setUp(self):
        f1 = join(self.fixture_dir, 'ajson', 'elife-20105-v1.xml.json')
        self.ajson = self.load_ajson(f1)

        f2 = join(self.fixture_dir, 'ajson', 'elife-01968-v1-bad.xml.json')
        self.bad_ajson = self.load_ajson(f2)

        f3 = join(self.fixture_dir, 'ajson', 'elife-01968-v1.xml.json')
        self.invalid_ajson = self.load_ajson(f3)
        self.invalid_ajson['article']['title'] = '' # ha! my invalid json is now valid. make it explicitly invalid.

    def tearDown(self):
        pass

    def test_article_ingest(self):
        """valid article-json is successfully ingested, creating an article,
        an article version and storing the ingestion request"""
        self.assertEqual(models.Journal.objects.count(), 0)
        self.assertEqual(models.Article.objects.count(), 0)
        self.assertEqual(models.ArticleVersion.objects.count(), 0)

        ajson_ingestor.ingest(self.ajson)

        self.assertEqual(models.Journal.objects.count(), 1)
        self.assertEqual(models.Article.objects.count(), 1)
        self.assertEqual(models.ArticleVersion.objects.count(), 1)

    def test_article_ingest_does_not_publish(self):
        """ingesting article json does not cause an article to become published
        (gain a published date) even if a published date was supplied"""
        expected = "2016-04-13T01:00:00"
        self.ajson['article']['published'] = expected
        _, _, av = ajson_ingestor.ingest(self.ajson)
        self.assertNotEqual(av.datetime_published, expected)

    def test_article_ingest_update(self):
        "ingesting article data twice successfully updates the Article object"
        _, _, av = ajson_ingestor.ingest(self.ajson)

        self.assertEqual(models.ArticleVersion.objects.count(), 1)
        self.assertEqual(av.title, self.ajson['article']['title'])
        self.assertEqual(av.datetime_published, None) # not published

        # do it again to cause an update
        expected_title = 'flub'
        self.ajson['article']['title'] = expected_title
        _, _, av = ajson_ingestor.ingest(self.ajson)

        self.assertEqual(models.ArticleVersion.objects.count(), 1)
        self.assertEqual(av.title, expected_title)
        self.assertEqual(av.datetime_published, None) # still not published

    def test_article_can_be_ingested_many_times_before_publication(self):
        "before an article is published it can be ingested many times"
        cases = json1, json2, json3 = lmap(copy.deepcopy, [self.ajson] * 3)

        json2['article']['title'] = 'foo'
        json3['article']['title'] = 'bar'

        # iterate through the three different cases,
        # assert each case is different from last
        prev_fragment = None
        for ajson in cases:
            _, a, av = ajson_ingestor.ingest(ajson)
            self.freshen(a)
            fragment = a.articlefragment_set.get(type=models.XML2JSON)
            if not prev_fragment:
                prev_fragment = fragment
                continue

            self.assertNotEqual(prev_fragment.fragment, fragment.fragment)

    def test_article_update_does_not_publish(self):
        "ingesting article data twice still does not cause publication"
        _, _, av = ajson_ingestor.ingest(self.ajson)
        self.assertEqual(av.datetime_published, None)

        expected = "2016-04-13T01:00:00"
        self.ajson['article']['published'] = expected

        _, _, av = ajson_ingestor.ingest(self.ajson)
        self.assertEqual(av.datetime_published, None)

    def test_article_ingest_fails_for_published_articles(self):
        "ingesting article data for a published article version fails"
        _, _, av = ajson_ingestor.ingest(self.ajson)
        # edit data directly
        av.datetime_published = '2001-01-01'
        av.save()
        self.assertTrue(av.published())

        # attempt another ingest
        self.assertRaises(StateError, ajson_ingestor.ingest, self.ajson)

    def test_article_ingest_for_published_articles_succeeds_if_forced(self):
        "ingesting article data for a published article version succeeds if force=True"
        _, _, av = ajson_ingestor.ingest(self.ajson)
        # edit data directly
        av.datetime_published = '2001-01-01'
        av.save()
        self.assertTrue(av.published())

        # attempt another ingest
        expected_title = 'foo'
        self.ajson['article']['title'] = expected_title
        _, _, av = ajson_ingestor.ingest(self.ajson, force=True)
        self.assertEqual(av.title, expected_title)

    @skip("we don't scrape journal data any more. we may in future")
    def test_article_ingest_bad_journal(self):
        "bad journal data will fail an ingest of article json"
        self.assertEqual(models.Journal.objects.count(), 0)
        del self.ajson['journal']
        self.assertRaises(Exception, ajson_ingestor.ingest, self.ajson)
        self.assertEqual(models.Journal.objects.count(), 0)

    def test_article_ingest_bad_article(self):
        "bad article data will fail an ingest of article json"
        self.assertEqual(models.Journal.objects.count(), 0)
        self.assertEqual(models.Article.objects.count(), 0)
        del self.ajson['article']
        self.assertRaises(Exception, ajson_ingestor.ingest, self.ajson)
        self.assertEqual(models.Journal.objects.count(), 0)
        self.assertEqual(models.Article.objects.count(), 0)

    def test_article_ingest_bad_article_version(self):
        "bad article version data will fail an ingest of article json"
        self.assertEqual(models.Journal.objects.count(), 0)
        self.assertEqual(models.Article.objects.count(), 0)
        self.assertEqual(models.ArticleVersion.objects.count(), 0)
        del self.ajson['article']['title']
        self.assertRaises(Exception, ajson_ingestor.ingest, self.ajson)
        self.assertEqual(models.Journal.objects.count(), 0)
        self.assertEqual(models.Article.objects.count(), 0)
        self.assertEqual(models.ArticleVersion.objects.count(), 0)

    @override_settings(VALIDATE_FAILS_FORCE=False)
    def test_out_of_sequence_ingest_fails(self):
        "attempting to ingest an article with a version greater than 1 when no article versions currently exists fails"
        # no article exists, attempt to ingest a v2
        self.assertEqual(models.ArticleVersion.objects.count(), 0)
        self.ajson['article']['version'] = 2
        # force=True to get it past the validation errors.
        # this used to work when we ignored validation errors on ingest
        self.assertRaises(StateError, partial(ajson_ingestor.ingest, force=True), self.ajson) # v2 POA
        self.assertEqual(models.Article.objects.count(), 0)
        self.assertEqual(models.ArticleVersion.objects.count(), 0)

    @override_settings(VALIDATE_FAILS_FORCE=False)
    def test_out_of_sequence_ingest_fails2(self):
        "attempting to ingest an article with a version greater than another unpublished version fails"
        _, _, av = ajson_ingestor.ingest(self.ajson) # v1
        self.assertEqual(models.ArticleVersion.objects.count(), 1)
        self.assertEqual(av.version, 1)

        # now attempt to ingest a v3
        self.ajson['article']['version'] = 3
        # force=True to get it past the validation errors.
        # this used to work when we ignored validation errors on ingest
        self.assertRaises(StateError, partial(ajson_ingestor.ingest, force=True), self.ajson)

        self.assertEqual(models.Article.objects.count(), 1)
        self.assertEqual(models.ArticleVersion.objects.count(), 1)
        av = self.freshen(av)
        self.assertEqual(av.version, 1) # assert the version hasn't changed

    def test_ingest_dry_run(self):
        "specifying a dry run does not commit changes to database"
        self.assertEqual(models.ArticleVersion.objects.count(), 0)
        _, _, av = ajson_ingestor.ingest(self.ajson, dry_run=True)
        self.assertEqual(models.ArticleVersion.objects.count(), 0)
        self.assertEqual(av.version, 1) # all the data that would have been saved

    # test ajson stored if valid

    def test_article_json_fails_on_bad_data(self):
        "INGEST events on bad data (distinct from 'invalid') should fail with a ValueError"
        self.assertRaises(ValueError, ajson_ingestor.ingest, self.bad_ajson)

    def test_article_json_stored_if_valid(self):
        """INGEST and PUBLISH events cause the fragments to be merged and stored
        but only if valid. ensure ajson is stored if result of merge is valid."""
        _, _, av = ajson_ingestor.ingest(self.ajson)
        av = self.freshen(av)
        # not a great test ...
        self.assertNotEqual(av.article_json_v1, None)
        self.assertNotEqual(av.article_json_v1_snippet, None)

    @override_settings(VALIDATE_FAILS_FORCE=False)
    def test_article_json_not_stored_if_invalid(self):
        """INGEST and PUBLISH events cause the fragments to be merged and stored but
        only if valid. ensure nothing is stored if result of merge is invalid"""
        _, _, av = ajson_ingestor.ingest(self.invalid_ajson, force=True)
        av = self.freshen(av)
        self.assertEqual(av.article_json_v1, None)
        self.assertEqual(av.article_json_v1_snippet, None)


class Publish(BaseCase):
    def setUp(self):
        self.ajson_fixture1 = join(self.fixture_dir, 'ajson', 'elife-01968-v1.xml.json')
        self.ajson = self.load_ajson(self.ajson_fixture1)
        self.msid = self.ajson['article']['id']
        self.version = self.ajson['article']['version'] # v1

    def tearDown(self):
        pass

    def test_article_publish_v1(self):
        "an unpublished v1 article can be successfully published"
        _, _, av = ajson_ingestor.ingest(self.ajson)
        self.assertEqual(models.Journal.objects.count(), 1)
        self.assertEqual(models.Article.objects.count(), 1)
        self.assertEqual(models.ArticleVersion.objects.count(), 1)
        self.assertFalse(av.published())

        # publish
        av = ajson_ingestor.publish(self.msid, self.version)

        # aaand just make sure we still have the expected number of objects
        self.assertEqual(models.Journal.objects.count(), 1)
        self.assertEqual(models.Article.objects.count(), 1)
        self.assertEqual(models.ArticleVersion.objects.count(), 1)

        self.assertTrue(av.published())
        self.assertTrue(isinstance(av.datetime_published, datetime))

        # the pubdate of an unpublished v1 article is the same as that found in the
        # given json.
        av = self.freshen(av)
        expected_pubdate = utils.ymd(utils.todt(self.ajson['article']['published']))
        self.assertEqual(expected_pubdate, utils.ymd(av.datetime_published))

    def test_article_publish_v2(self):
        "an unpublished v2 article can be successfully published"
        _, _, av = ajson_ingestor.ingest(self.ajson)
        self.assertEqual(models.Journal.objects.count(), 1)
        self.assertEqual(models.Article.objects.count(), 1)
        self.assertEqual(models.ArticleVersion.objects.count(), 1)
        self.assertFalse(av.published())

        ajson_ingestor.publish(self.msid, self.version)
        av = self.freshen(av)
        self.assertTrue(av.published())

        # modify to a v2 and publish
        self.ajson['article']['version'] = 2
        _, _, av2 = ajson_ingestor.ingest_publish(self.ajson)

        av2 = self.freshen(av2)
        self.assertEqual(models.ArticleVersion.objects.count(), 2)
        self.assertTrue(av2.published())
        self.assertEqual(utils.ymd(datetime.now()), utils.ymd(av2.datetime_published))

    @skip("forced pubdate update of non-v1 articles disabled until xml supports version history")
    def test_article_publish_v2_forced(self):
        "an unpublished v2 article can be successfully published again, if forced"
        # ingest and publish the v1
        _, _, av = ajson_ingestor.ingest(self.ajson)
        ajson_ingestor.publish(self.msid, self.version)
        av = self.freshen(av)
        self.assertTrue(av.published())

        # modify and ingest+publish a v2
        self.ajson['article']['version'] = 2
        _, _, av2 = ajson_ingestor.ingest_publish(self.ajson)
        av2 = self.freshen(av2)
        self.assertTrue(av2.published())

        # the v2 should have been published normally.
        self.assertEqual(utils.ymd(datetime.now()), utils.ymd(av2.datetime_published))

        # give the article-json a 'versionDate' - this won't ordinarily happen until further down the line
        # but lets embed this logic while it's still fresh in everybody's heads.

        # modify the versionDate of the v2 and ingest+publish again
        yesterday = datetime.now() - timedelta(days=1)
        self.ajson['article']['versionDate'] = yesterday
        _, _, av2v2 = ajson_ingestor.ingest_publish(self.ajson, force=True)
        av2v2 = self.freshen(av2v2)
        self.assertEqual(utils.ymd(yesterday), utils.ymd(av2v2.datetime_published))

    def test_article_publish_v2_forced2(self):
        "a PUBLISHED v2 article can be successfully published (again), if forced"
        _, _, av = ajson_ingestor.ingest(self.ajson)
        ajson_ingestor.publish(self.msid, self.version)
        av = self.freshen(av)
        self.assertTrue(av.published())

        # modify and ingest+publish a v2
        self.ajson['article']['version'] = 2
        # there is a versionDate here, but because we're not forcing it, it doesn't get looked for
        # lax is the distributor of non-v1 pub dates. this may find their way into xml later, but
        # they will always come from lax.
        _, _, av2 = ajson_ingestor.ingest_publish(self.ajson)
        av2 = self.freshen(av2)
        self.assertTrue(av2.published())
        self.assertEqual(utils.ymd(datetime.now()), utils.ymd(av2.datetime_published))

        # don't set a versionDate, just force a publish
        # we expect the v2.datetime_publish to remain unchanged
        del self.ajson['article']['versionDate'] # remember, this was copied from a v1 that had a versionDate!
        _, _, av2v2 = ajson_ingestor.ingest_publish(self.ajson, force=True)
        av2v2 = self.freshen(av2v2)

        self.assertEqual(av2.datetime_published, av2v2.datetime_published)

    def test_article_publish_fails_if_already_published(self):
        "a published article CANNOT be published again"
        _, _, av = ajson_ingestor.ingest(self.ajson)
        av = ajson_ingestor.publish(self.msid, self.version)
        av = self.freshen(av)
        self.assertTrue(av.published())

        # publish again
        self.assertRaises(StateError, ajson_ingestor.publish, self.msid, self.version)

    def test_article_publish_succeeds_for_published_article_if_forced(self):
        "publication of an already published article can occur only if forced"
        _, _, av = ajson_ingestor.ingest(self.ajson)
        av = ajson_ingestor.publish(self.msid, self.version)
        av = self.freshen(av)
        expected_pubdate = utils.ymd(utils.todt(self.ajson['article']['published']))
        self.assertEqual(expected_pubdate, utils.ymd(av.datetime_published))

        # publish again, no changes to pubdate expected
        av = ajson_ingestor.publish(self.msid, self.version, force=True)
        av = self.freshen(av)
        self.assertEqual(expected_pubdate, utils.ymd(av.datetime_published))

        # ingest new pubdate, force publication
        new_pubdate = utils.todt('2016-01-01')
        self.ajson['article']['published'] = new_pubdate
        ajson_ingestor.ingest_publish(self.ajson, force=True)
        av = self.freshen(av)
        self.assertEqual(utils.ymd(new_pubdate), utils.ymd(av.datetime_published))

    def test_out_of_sequence_publish_fails(self):
        "attempting to ingest an article with a version greater than another *published* version fails"
        # ingest and publish a v1
        _, _, av = ajson_ingestor.ingest(self.ajson) # v1
        ajson_ingestor.publish(self.msid, self.version)

        # now attempt to ingest a v3
        self.ajson['article']['version'] = 3
        self.assertRaises(StateError, ajson_ingestor.ingest, self.ajson)

        self.assertEqual(models.Article.objects.count(), 1)
        self.assertEqual(models.ArticleVersion.objects.count(), 1)
        av = self.freshen(av)
        self.assertEqual(av.version, 1) # assert the version hasn't changed

    def test_publish_fails_if_no_article(self):
        self.assertEqual(models.ArticleVersion.objects.count(), 0)
        self.assertRaises(StateError, ajson_ingestor.publish, self.msid, self.version)

    def test_publish_dry_run(self):
        "specifying a dry run does not commit changes to database"
        _, _, saved_av = ajson_ingestor.ingest(self.ajson) # do an actual ingest first
        unsaved_av = ajson_ingestor.publish(self.msid, self.version, dry_run=True)
        self.assertEqual(models.ArticleVersion.objects.count(), 1)
        # ensure the article version stored has no published date
        models.ArticleVersion.objects.get(pk=saved_av.pk, datetime_published=None)
        # and that the object returned *does* have a datetime published
        self.assertTrue(unsaved_av.published())

    def test_publish_fails_if_invalid(self):
        "an article cannot be published if it's article-json is invalid."
        self.ajson['article']['title'] = ''
        # ValidationError is raised during ingest
        self.assertRaises(ValidationError, ajson_ingestor.ingest_publish, self.ajson)
        # TODO: affect a valid INGEST but an invalid PUBLISH
        #self.assertRaises(StateError, ajson_ingestor.ingest_publish, self.ajson)

class IngestPublish(BaseCase):
    def setUp(self):
        self.ajson_fixture1 = join(self.fixture_dir, 'ajson', 'elife-01968-v1.xml.json')
        self.ajson = self.load_ajson(self.ajson_fixture1)

    def tearDown(self):
        pass

    def test_ingest_publish(self):
        "ensure the shortcut ingest_publish behaves as expected"
        self.assertEqual(models.Journal.objects.count(), 0)
        self.assertEqual(models.Article.objects.count(), 0)
        self.assertEqual(models.ArticleVersion.objects.count(), 0)

        _, _, av = ajson_ingestor.ingest_publish(self.ajson)

        self.assertEqual(models.Journal.objects.count(), 1)
        self.assertEqual(models.Article.objects.count(), 1)
        self.assertEqual(models.ArticleVersion.objects.count(), 1)

        av = self.freshen(av)
        self.assertEqual(av.version, 1)
        self.assertTrue(av.published())

    def test_ingest_publish_force(self):
        "we can do silent corrections/updates if we force it to"
        _, _, av = ajson_ingestor.ingest_publish(self.ajson)
        expected_title = 'pants-party'
        self.ajson['article']['title'] = expected_title
        _, _, av = ajson_ingestor.ingest_publish(self.ajson, force=True)
        av = self.freshen(av)
        self.assertEqual(av.title, expected_title)

    def test_ingest_publish_no_force(self):
        "attempting to do an update without force=True fails"
        # ingest once
        _, _, av = ajson_ingestor.ingest_publish(self.ajson)
        # attempt second ingest
        self.assertRaises(StateError, ajson_ingestor.ingest_publish, self.ajson)

    def test_ingest_publish_dry_run(self):
        "specifying a dry run does not commit changes to database"
        self.assertEqual(models.Journal.objects.count(), 0)
        self.assertEqual(models.Article.objects.count(), 0)
        self.assertEqual(models.ArticleVersion.objects.count(), 0)

        j, a, av = ajson_ingestor.ingest_publish(self.ajson, dry_run=True)

        # all counts are still zero
        self.assertEqual(models.Journal.objects.count(), 0)
        self.assertEqual(models.Article.objects.count(), 0)
        self.assertEqual(models.ArticleVersion.objects.count(), 0)

        # article version believes itself to be published
        self.assertTrue(av.published())


class CLI(BaseCase):
    def setUp(self):
        self.nom = 'ingest'
        self.msid = "01968"
        self.version = "1"
        self.ajson_fixture1 = join(self.fixture_dir, 'ajson', 'elife-01968-v1.xml.json')

    def tearDown(self):
        pass

    def test_ingest_from_cli(self):
        "ingest script requires the --ingest flag and a source of data"
        args = [self.nom, '--ingest', '--id', self.msid, '--version', self.version, self.ajson_fixture1]
        errcode, stdout = self.call_command(*args)
        self.assertEqual(errcode, 0)
        # article has been ingested
        self.assertEqual(models.ArticleVersion.objects.count(), 1)
        # message returned is json encoded with all the right keys and values
        result = json.loads(stdout)
        self.assertTrue(utils.has_all_keys(result, ['status', 'id', 'datetime']))
        self.assertEqual(result['status'], 'ingested')
        # the date and time is roughly the same as right now, ignoring microseconds
        expected_datetime = utils.utcnow()
        actual_datetime = utils.todt(result['datetime'])
        delta = expected_datetime - actual_datetime
        threshold = 2 # seconds
        self.assertTrue(delta.seconds <= threshold)

    def test_publish_from_cli(self):
        args = [self.nom, '--ingest', '--id', self.msid, '--version', self.version, self.ajson_fixture1]
        errcode, stdout = self.call_command(*args)
        self.assertEqual(errcode, 0)
        # article has been ingested
        self.assertEqual(models.ArticleVersion.objects.count(), 1)

        args = [self.nom, '--publish', '--id', self.msid, '--version', self.version]
        errcode, stdout = self.call_command(*args)
        self.assertEqual(errcode, 0)
        # ensure response is json
        result = json.loads(stdout)
        self.assertTrue(utils.has_all_keys(result, ['status', 'id', 'datetime']))
        self.assertEqual(result['status'], 'published')

    def test_ingest_publish_from_cli(self):
        args = [self.nom, '--ingest+publish', '--id', self.msid, '--version', self.version, self.ajson_fixture1]
        errcode, stdout = self.call_command(*args)
        self.assertEqual(errcode, 0)
        # article has been ingested
        av = models.ArticleVersion.objects.get(article__manuscript_id=self.msid, version=self.version)
        # article has been published
        self.assertTrue(av.published())
        # ensure response is json and well-formed
        result = json.loads(stdout)
        self.assertTrue(utils.has_all_keys(result, ['status', 'id', 'datetime']))
        # ensure response data is correct
        self.assertEqual(result['status'], 'published')
        self.assertEqual(result['datetime'], utils.ymdhms(av.datetime_published))

    def test_ingest_publish_dry_run_from_cli(self):
        # ensure nothing exists
        self.assertEqual(models.Journal.objects.count(), 0)
        self.assertEqual(models.Article.objects.count(), 0)
        self.assertEqual(models.ArticleVersion.objects.count(), 0)

        args = [self.nom, '--ingest+publish', '--id', self.msid, '--version', self.version,
                self.ajson_fixture1, '--dry-run']
        errcode, stdout = self.call_command(*args)
        self.assertEqual(errcode, 0)

        # ensure nothing was created
        self.assertEqual(models.Journal.objects.count(), 0)
        self.assertEqual(models.Article.objects.count(), 0)
        self.assertEqual(models.ArticleVersion.objects.count(), 0)

        # ensure response is json and well-formed
        result = json.loads(stdout)
        self.assertTrue(utils.has_all_keys(result, ['status', 'id', 'datetime', 'message']))
        # ensure response data is correct
        self.assertEqual(result['status'], 'published')

        ajson = json.load(open(self.ajson_fixture1, 'r'))
        self.assertEqual(result['datetime'], ajson['article']['published'])
        self.assertEqual(result['message'], "(dry-run)")


class UnicodePreserved(BaseCase):
    '''
    ensures unicode isn't being mangled at any step of the processing
    http://jira.elifesciences.org:8080/browse/ELPP-2013

        {"type":"person","name":{"index":"Lengyel, MĂĄtĂŠ","preferred":"MĂĄtĂŠ Lengyel"}}

        If I generate JSON locally using bot-lax-adaptor I get

                    {
                        "type": "person",
                        "name": {
                            "preferred": "M\u00e1t\u00e9 Lengyel",
                            "index": "Lengyel, M\u00e1t\u00e9"
                        },

        The web and Lens it shows as

        Máté Lengyel
    '''

    def setUp(self):
        self.nom = 'ingest'
        self.msid = "12215"
        self.version = "1"
        self.ajson_fixture1 = join(self.fixture_dir, 'ajson', 'elife-12215-v1.xml.json')

    def test_ingest_publish_dont_alter_unicode(self):
        "the unicode value in the scraped json isn't altered when it's ingested and published"
        ajson = json.load(open(self.ajson_fixture1, 'r'))
        _, _, av = ajson_ingestor.ingest_publish(ajson)
        av = utils.freshen(av)
        expected = ajson['snippet']['authors'][1]['name']['preferred']
        given = av.article_json_v1['authors'][1]['name']['preferred']
        self.assertEqual(expected, given)

    def test_logic_doesnt_mangle_unicode(self):
        "the api logic doesn't alter unicode values"
        ajson = json.load(open(self.ajson_fixture1, 'r'))
        ajson_ingestor.ingest_publish(ajson)

        expected = ajson['snippet']['authors'][1]['name']['preferred']

        # /articles/{id}
        given = logic.most_recent_article_version(self.msid).article_json_v1['authors'][1]['name']['preferred']
        self.assertEqual(expected, given)

        # /articles/{id}/versions/{version}
        given = logic.article_version(self.msid, self.version).article_json_v1['authors'][1]['name']['preferred']
        self.assertEqual(expected, given)

    def test_api_doesnt_mangle_unicode(self):
        ajson = json.load(open(self.ajson_fixture1, 'r'))
        ajson_ingestor.ingest_publish(ajson)
        expected = ajson['snippet']['authors'][1]['name']['preferred']

        c = Client()
        resp = c.get(reverse('v2:article', kwargs={'id': self.msid}))
        data = json.loads(resp.content.decode('utf-8'))
        # data = resp.json() # https://github.com/tomchristie/django-rest-framework/issues/4491
        given = data['authors'][1]['name']['preferred']

        self.assertEqual(expected, given)

        resp = c.get(reverse('v2:article-version', kwargs={'id': self.msid, 'version': self.version}))
        data = json.loads(resp.content.decode('utf-8'))
        given = data['authors'][1]['name']['preferred']

    def test_cli_ingest_doesnt_mangle_unicode(self):
        ajson = json.load(open(self.ajson_fixture1, 'r'))
        expected = ajson['snippet']['authors'][1]['name']['preferred']

        args = [self.nom, '--ingest+publish', '--id', self.msid, '--version', self.version, self.ajson_fixture1]
        errcode, stdout = self.call_command(*args)
        self.assertEqual(errcode, 0)
        # article has been ingested
        av = models.ArticleVersion.objects.get(article__manuscript_id=self.msid, version=self.version)

        given = av.article_json_v1['authors'][1]['name']['preferred']
        self.assertEqual(expected, given)
