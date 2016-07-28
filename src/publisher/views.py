from os.path import join
import os
from django.conf import settings
import json
from django.shortcuts import get_object_or_404, Http404
from annoying.decorators import render_to
import models, logic
from django.views.decorators.http import require_POST
from django.http import HttpResponse
import ingestor, rss
from django.core.urlresolvers import reverse
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.parsers import ParseError
from rest_framework import serializers as szr
from django.db.models import Q
from datetime import datetime, timedelta

import logging
LOG = logging.getLogger(__name__)

@render_to("publisher/landing.html")
def landing(request):
    project_root = os.path.abspath(join(settings.SRC_DIR, '..'))
    return {
        'readme': open(join(project_root, 'README.md')).read()
    }
