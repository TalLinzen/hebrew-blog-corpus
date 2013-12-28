# -*- coding: utf-8 -*-
import codecs
import collections
import csv
import itertools
import os

import xlwt

from hbc.conf import data_dir
from hbc.io import BGUDir
from hbc.filters.count_lemmas import CountLemmas

def _count_lemmas_example(f):
    def res():
        d = BGUDir(os.path.join(os.environ['HBC_PATH'], '5'))
        cl = f()
        cl.process_many(d)
        return cl
    return res

@_count_lemmas_example
def count_lemmas_two_specific():
    return CountLemmas(lemmas=[u'אני', u'הוא'])

@_count_lemmas_example
def count_lemmas_all():
    return CountLemmas(lemmas=None)

@_count_lemmas_example
def count_lemmas_with_pos():
    return CountLemmas(lemmas=None, fields=['pos', 'lemma'])

def most_common_by_pos(how_many=5000):
    interesting_pos = ['adjective', 'adverb', 'noun', 'verb']
    d = BGUDir(os.environ['HBC_PATH'])
    clpos = CountLemmas(lemmas=None, fields=['pos', 'lemma'])
    clpos.process_many(d)

    items = sorted(clpos.counter.items())
    group_iter = itertools.groupby(items, lambda x: x[0][0])
    d = {pos: collections.Counter(dict(positems)) for 
         pos, positems in group_iter}

    wb = xlwt.Workbook()
    for pos in interesting_pos:
        sheet = wb.add_sheet(pos)
        for i, ((_, lemma), count) in enumerate(d[pos].most_common(how_many)):
            sheet.write(i, 0, lemma)
            sheet.write(i, 1, count)
    wb.save(os.path.join(data_dir, 'most_common_by_pos.xls'))
