# -*- coding: utf-8 -*-
from hbc.filters.dative import PossessiveDativeOneWord, GenitiveOneWord, \
        QuickDativePredicatesClass
from hbc.annotation import ByAttributeAnnotation
from hbc.io import BGUDir
import os, csv, codecs
from collections import Counter

d = BGUDir(os.path.expanduser("~/data/hbc_analyzed"))

def pd_example():
    pd = PossessiveDativeOneWord()
    pd.process_many(d)
    b = ByAttributeAnnotation('Verbs', sentences=pd.sentences,
            attributes=['lemma', 'argument'])
    b.write('/tmp/annotations')
    return pd

def gen_example():
    gen = GenitiveOneWord()
    gen.process_many(d)
    return gen

def print_sentences(sentences):
    for sentence in sentences:
        print ' '.join(sentence.words), '\n'

def count_by_metadata(sentences):
    count = Counter((x.metadata['lemma'], x.metadata['argument'])
        for x in sentences)
    f = codecs.open('/tmp/counts.csv', 'w', 'utf16')
    for ((x, y), z) in sorted(count.items()):
        f.write('%s,%s,%s\n' % (x, y, z))

def all_possible_pds():
    fname = os.path.expanduser("~/Dropbox/hbc/data/possessive_dative_verbs.csv")
    r = csv.reader(codecs.open(fname, 'rU'))
    verbs = [x[0].decode('utf8') for x in r]
    q = QuickDativePredicatesClass(verbs)()
    q.process_many(d)
    b = ByAttributeAnnotation('Verbs', sentences=q.sentences,
            attributes=['lemma', 'argument'])
    b.write('/tmp/annotations')
    return q

