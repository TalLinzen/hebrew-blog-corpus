# -*- coding: utf-8 -*-
from collections import Counter
import codecs
import csv
import os

from hbc.annotation.by_attribute import ByAttributeAnnotation
from hbc.filters.dative import PossessiveDativeOneWord, GenitiveOneWord, \
        QuickDativePredicatesClass
from hbc.io import BGUDir
from hbc.conf import data_dir

d = BGUDir(os.path.join(os.environ['HBC_PATH'], '5'))

def pd_example():
    '''
    Get all sentences with a potential single-word Possessive Dative, then 
    create an annotation file for each combination of verb and argument type 
    (e.g. "break" with a pronoun argument)
    '''
    pd = PossessiveDativeOneWord()
    pd.process_many(d)
    b = ByAttributeAnnotation('Verbs', sentences=pd.sentences, 
                              attributes=['verb', 'argument'])
    b.write('/tmp/annotations')
    return pd

def gen_example():
    '''
    Get all sentences with a potential single-word genitive argument.
    '''
    gen = GenitiveOneWord()
    gen.process_many(d)
    return gen

def print_sentences(sentences):
    for sentence in sentences:
        print ' '.join(sentence.words), '\n'

def count_by_metadata(sentences):
    count = Counter((x.metadata['verb'], x.metadata['argument']) 
                    for x in sentences)
    f = codecs.open('/tmp/counts.csv', 'w', 'utf16')
    for ((x, y), z) in sorted(count.items()):
        f.write('%s,%s,%s\n' % (x, y, z))

def pds_from_verb_list():
    '''
    Get all Possessive Dative sentences that have one of the verbs in the
    candidate list as their main verb.
    '''
    fname = os.path.join(data_dir, 'possessive_dative_verbs.csv')
    r = csv.reader(codecs.open(fname, 'rU'))
    verbs = [x[0].decode('utf8') for x in r]
    q = QuickDativePredicatesClass(verbs)()
    q.process_many(d)
    b = ByAttributeAnnotation('Verbs', sentences=q.sentences, 
                              attributes=['lemma', 'argument'])
    b.write('/tmp/annotations')
    return q
