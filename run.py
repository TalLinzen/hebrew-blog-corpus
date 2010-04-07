# -*- coding: utf-8 -*-
from pdb import pm
import codecs
from sqlobject import *

from db import setup_connection, WebPage, User
from israblog.clean import IsrablogCleaner, run_morph_analyzer
from israblog.harvest import IsrablogHarvester
from filters.pd import PossessiveDativeFilter
from filters.genitive import GenitiveFilter
from filters.subcat import SubcategorizationFrames
from filters.subcat_annotation import SubcatAnnotation
from tools.process_annotation import AnnotationProcessor
from bgutag import BGUFile, BGUDir, BGUQuery
from verbs_for_subcat import verbs_for_subcat

cleaner = IsrablogCleaner()
harvester = IsrablogHarvester()

subcat_annotation_destinations = {'al': 'PP-על',
        'el': 'PP-אל',
        'l': 'PP-ל',
        'm': 'PP-מן',
        'k': 'PP-כ',
        'min': 'PP-מן',
        'b': 'PP-ב'}

subcat_annotation_processor = AnnotationProcessor(
        destinations=subcat_annotation_destinations)

def pheb(s):
    h = s.decode('cp1255')
    p = []
    for line in h.split('\n'):
        p.append(''.join(reversed(line)))
    print '\n'.join(p)

def age_histogram():
    return WebPage._connection.queryAll('select age, count(*) from user group by age')

def possessive_by_age(min_age, max_age, cls):
    old = list(User.select(AND(User.q.age >= min_age, User.q.age < max_age, 
        User.q.chars > 500000)))
    filtr = cls()
    for i, user in enumerate(old):
        print '%d (%s) out of %d' % (i, user, len(old))
        q = BGUQuery(WebPage.select(WebPage.q.user == user.number))
        filtr.process_many(q)
    dirname = '%s_%dto%d' % (filtr.Annotation.prefix, min_age, max_age)
    annotation = filtr.Annotation(filtr)
    annotation.write(dirname)
    return filtr
