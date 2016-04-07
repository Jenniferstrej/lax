import copy
import pytz
from dateutil import parser
from django.utils import timezone
from functools import partial
import os, sys
import logging

LOG = logging.getLogger(__name__)

def nth(idx, x):
    try:
        return x[idx]
    except IndexError:
        return None
    except TypeError:
        raise

def first(x):
    return nth(0, x)

def second(x):
    return nth(1, x)

def delall(ddict, lst):
    def delkey(key):
        try:
            del ddict[key]
            return True
        except KeyError:
            return False
    return zip(lst, map(delkey, lst))

def todt(val):
    "turn almost any formatted datetime string into a UTC datetime object"
    dt = parser.parse(val)
    if not dt.tzinfo:
        LOG.warn("encountered naive timestamp %r. UTC assumed.", val)
        return pytz.utc.localize(dt)
    else:
        # ensure tz is UTC??
        pass
    return dt


def filldict(ddict, keys, default):
    def filldictslot(ddict, key, val):
        if not ddict.has_key(key):
            ddict[key] = val
    data = copy.deepcopy(ddict)
    for key in keys:
        if isinstance(key, tuple):
            key, val = key
        else:
            val = default
        filldictslot(data, key, val)
    return data
    

# stolen from:
# http://stackoverflow.com/questions/10823877/what-is-the-fastest-way-to-flatten-arbitrarily-nested-lists-in-python
def flatten(container):
    for i in container:
        if isinstance(i, list) or isinstance(i, tuple):
            for j in flatten(i):
                yield j
        else:
            yield i

def future_date(date):
    "predicate. returns True if given timezone-aware date is in the future"
    return date > timezone.now()

def subdict(dt, ks):
    return {k:v for k, v in dt.items() if k in ks}

def dictmap(func, data, **funcargs):
    "applies the given function over the values of the given data map. optionally passes any keyword args"
    if funcargs:
        func = partial(func, **funcargs)
    return {k:func(v) for k, v in data.items()}

def djobj_hasattr(djobj, key):
    return key in map(lambda f: f.name, djobj._meta.get_fields())

from django.db.models.fields.related import ManyToManyField
def to_dict(instance):
    opts = instance._meta
    data = {}
    for f in opts.concrete_fields + opts.many_to_many:
        if isinstance(f, ManyToManyField):
            if instance.pk is None:
                data[f.name] = []
            else:
                data[f.name] = list(f.value_from_object(instance).values_list('pk', flat=True))
        else:
            data[f.name] = f.value_from_object(instance)
    return data

def updatedict(ddict, **kwargs):
    newdata = copy.deepcopy(ddict)
    for key, val in kwargs.items():
        newdata[key] = val
    return newdata
