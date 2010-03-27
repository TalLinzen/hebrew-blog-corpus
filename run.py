# -*- coding: utf-8 -*-
from pdb import pm
import codecs
from sqlobject import *

from db import setup_connection, WebPage, User
from israblog.clean import IsrablogCleaner, run_morph_analyzer
from israblog.harvest import IsrablogHarvester
from filters.pd import PossessiveDative
from filters.subcat import SubcategorizationFrames
from filters.pd_annotation import PDAnnotation
from filters.subcat_annotation import SubcatAnnotation
from bgutag import BGUFile, BGUDir, BGUQuery
from verbs_for_subcat import verbs_for_subcat

cleaner = IsrablogCleaner()
harvester = IsrablogHarvester()

def pheb(s):
    h = s.decode('cp1255')
    p = []
    for line in h.split('\n'):
        p.append(''.join(reversed(line)))
    print '\n'.join(p)

def age_histogram():
    return WebPage._connection.queryAll('select age, count(*) from user group by age')

def query_by_age(min_age, max_age):
    old = list(User.select(AND(User.q.age >= min_age, User.q.age < max_age, 
        User.q.chars > 500000)))
    pd = PossessiveDative()
    for i, user in enumerate(old):
        print '%d (%s) out of %d' % (i, user, len(old))
        pd.process_many(BGUQuery(WebPage.select(WebPage.q.user == user.number)))
    pda = PDAnnotation()
    pda.create(pd, 'pd%dto%d' % (min_age, max_age))
    return pd
