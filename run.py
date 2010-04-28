# -*- coding: utf-8 -*-
from pdb import pm
import codecs
from sqlobject import *

from db import setup_connection, WebPage, User
from israblog.clean import IsrablogCleaner, run_morph_analyzer
from israblog.harvest import IsrablogHarvester
from filters.pd import PossessiveDativeFilter
from filters.genitive import GenitiveFilter
from filters.dative import DativeFilter
from filters.filter import Filter
from filters.subcat import SubcategorizationFrames
from filters.subcat_annotation import SubcatAnnotation
from filters.by_user_annotation import MixUsers, ByAttributeAnnotation
from filters.count_lemmas import CountLemmas
from tools.process_annotation import AnnotationProcessor
from bgutag import BGUFile, BGUDir, BGUQuery
from verbs_for_subcat import verbs_for_subcat
from word_lists import *

cleaner = IsrablogCleaner()
harvester = IsrablogHarvester()

subcat_annotation_destinations = {'AL': 'PP-על',
        'EL': 'PP-אל',
        'L': 'PP-ל',
        'LE': 'PP-ל',
        'M': 'PP-מן',
        'ME': 'PP-מן',
        ' ': 'NONE',
        'K': 'PP-כ',
        'MIN': 'PP-מן',
        'B': 'PP-ב',
        'BE': 'PP-ב'}

subcat_annotation_processor = AnnotationProcessor(
        destinations=subcat_annotation_destinations)

def pufc(count, n=1000, rev=True):
    'Print frequency count where keys are in Unicode'
    items = list(count.items())
    items.sort(key=lambda x: -x[1])
    for key, value in items[:n]:
        if rev:
            key = ''.join(reversed(key))
        print '%10s %d' % (key, value)

def age_histogram():
    return WebPage._connection.queryAll('select age, count(*) from user group by age')

def apply_filters_by_age(min_age, max_age, filters, annotator):
    filters = list(filters)
    if (min_age >= max_age):
        raise ValueError("min_age must be lower than max_age")
    old = list(User.select(AND(User.q.age >= min_age, User.q.age < max_age, 
        User.q.chars > 500000)))
    for i, user in enumerate(old):
        print '%d (%s) out of %d' % (i, user, len(old))
        q = BGUQuery(WebPage.select(WebPage.q.user == user.number))
        filters[0].process_many(filters, q)
    for filter in filters:
        dirname = '%s_%dto%d' % (filter.annotation_prefix, min_age, max_age)
        annotator.set_filter(filter)
        annotator.write(dirname)
    return filters
