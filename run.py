# -*- coding: utf-8 -*-
from pdb import pm
import codecs, glob, os, csv
from sqlobject import *

from io import BGUFile, BGUDir, BGUQuery, BGUQueries
from db import setup_connection, WebPage, User
import conf

from israblog.clean import IsrablogCleaner, run_morph_analyzer
from israblog.harvest import IsrablogHarvester
cleaner = IsrablogCleaner()
harvester = IsrablogHarvester()

from filters.subcat import SubcategorizationFrames
from filters.subcat_annotation import SubcatAnnotation
from filters.count_lemmas import CountLemmas
from filters.annotation import *
from filters.dative import *
from tools.process_annotation import AnnotationProcessor
import tools.transliterated_hebrew
from data.word_lists import *

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
    query = 'select age, count(*) from user group by age'
    return WebPage._connection.queryAll(query)

def by_user_condition(condition):
    queries = []
    res = list(User.select(condition))
    for i, user in enumerate(res):
        queries.append(WebPage.select(WebPage.q.user == user.number))
    return queries

def users_by_age(min_age, max_age):
    if (min_age >= max_age):
        raise ValueError("min_age must be lower than max_age")
    return BGUQueries(by_user_condition(
        AND(User.q.age >= min_age, User.q.age < max_age)))

def apply_filters_by_age(min_age, max_age, filters, annotator, name=None):
    if type(filters) != list:
        filters = [filters]
    filters[0].process_many(users_by_age(min_age, max_age), filters[1:])
    for filter in filters:
        dirname = '%dto%d_%s' % (min_age, max_age,
                filter.__class__.__name__ if name is None else name)
        annotator.set_sentences(filter.sentences)
        annotator.write(dirname)
    return filters

ages = [(13, 17), (18, 19), (24, 28), (30, 38), (40, 70)]

def possessive_with_pronouns(ages):
    for min_age, max_age in ages:
        g = GenitiveWithPronoun()
        pd = PossessiveDativeWithPronoun()
        input = users_by_age(min_age, max_age)
        pd.process_many(input, [g])

        name = '%dto%d_GenPron' % (min_age, max_age)
        annotator = ByAttributeAnnotation(name, 'verb', 
                mode='single_workbook', single_workbook_name=name,
                custom_fields=('possessum',))
        annotator.set_sentences(g.sentences)
        annotator.write(name)

        name = '%dto%d_PDPron' % (min_age, max_age)
        annotator = ByAttributeAnnotation(name, 'verb', 
                mode='single_workbook', single_workbook_name=name,
                custom_fields=('possessum',))
        annotator.set_sentences(pd.sentences)
        annotator.write(name)

def possessive_one_word(ages):
    for min_age, max_age in ages:
        g = GenitiveOneWord()
        pd = PossessiveDativeOneWord()
        input = users_by_age(min_age, max_age)
        pd.process_many(input, [g])

        name = '%dto%d_GenOneWord' % (min_age, max_age)
        annotator = ByAttributeAnnotation(name, 'verb', 
                mode='single_workbook', single_workbook_name=name,
                custom_fields=('possessum', 'argument'))
        annotator.set_sentences(g.sentences)
        annotator.write(name)

        name = '%dto%d_PDOneWord' % (min_age, max_age)
        annotator = ByAttributeAnnotation(name, 'verb', 
                mode='single_workbook', single_workbook_name=name,
                custom_fields=('possessum', 'argument'))
        annotator.set_sentences(pd.sentences)
        annotator.write(name)

prongendir = os.path.join(conf.annotation_dir, 'PronounGen')
pronpddir = os.path.join(conf.annotation_dir, 'PronounPD')

def read_dir(d):
    l = []
    for subdir in sorted(glob.glob(os.path.join(d, '*'))):
        if os.path.isdir(subdir):
            s = read_sentence_file(os.path.join(subdir, 'sentences.json'))
            l.append(s)
    return l

def get_sentence(filter, sentence):
    bq = BGUQuery(WebPage.get(sentence.metadata['webpage_id']))
    filter.process(list(bq)[sentence.metadata['index']])
    return filter

def r_data_frame(pd_sentences, gen_sentences):
    #def q(dirname):
    #    return reduce(lambda x, y: x + y, 
    #            [[x for x in y if x.metadata['possessum'] in body_parts] \
    #                for y in read_dir(dirname)])

    #pronpd = q(pronpddir)
    #prongen = q(prongendir)

    for sentence in gen_sentences:
        sentence.metadata['type'] = 'gen'
    for sentence in pd_sentences:
        sentence.metadata['type'] = 'pd'
    writer = csv.writer(open(os.path.join(conf.data_dir, 'r_data.csv'), 'w'))
    writer.writerow(['type', 'user', 'age', 'sex', 'verb', 'bp'])
    for sentence in gen_sentences + pd_sentences:
        writer.writerow([sentence.metadata['type'], 
                sentence.metadata['user'],
                sentence.metadata['age'],
                sentence.metadata['sex'], 
                sentence.metadata['verb'].encode('transliterated-hebrew'),
                str(sentence.metadata['possessum'] in body_parts)[0]])

# dict((key, float(len([x for x in value if x.metadata['possessum'] in body_parts])) / len(value)) for key, value in pos.items())

# c = [CountLemmas.from_file(x, field='word') for x in glob.glob('/Users/tal/Dropbox/University/Einat/unknown_words/*.txt')]
# q = BGUQueries(by_user_condition(User.q.number < 5000), limit=1000000, distribute=True)
# c[0].process_many(q, c[1:])
# for x in c: x.save_xls()
