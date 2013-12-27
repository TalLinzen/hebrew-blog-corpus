# -*- coding: utf-8 -*-

import codecs
import collections
import os

import xlwt
from filter import Filter

class CountLemmas(Filter):

    def __init__(self, lemmas=None, fields=['lemma'], word_limit=None,
                 predicate=None):
        '''
        lemmas : None | iterable
            Only count lemmas that are in this list. If None, count all lemmas.
        fields : iterable
            Field combination to count. By default count lemmas; e.g.
            fields=['lemma', 'pos'] will count noun and verb occurrences of the
            same lemma separately.
        word_limit : None | int
            Stop after this number of words have been processed.
        predicate : None | callable
            If not None, lemmas are only counted if this function return True
            (when passed the whole word). E.g., `lambda x: x['pos'] == 'noun'`
            would only count nouns.
        '''
        Filter.__init__(self)
        self.lemmas = None if lemmas is None else list(lemmas)
        self.counter = collections.Counter()
        self.word_limit = word_limit
        self.predicate = predicate
        self.total_word_count = 0
        self.sentence_count = 0
        self.fields = list(fields)

    @classmethod
    def from_file(cls, filename, **args):
        handle = codecs.open(filename, encoding='utf8')
        lemmas = [x.replace('"', '').strip() for x in handle.readlines()]
        obj = cls(lemmas, **args)
        obj.filename = filename
        return obj

    def process(self, sentence):
        self.sentence_count += 1
        for word in sentence.rich_words:
            value = tuple(getattr(word, f) for f in self.fields)
            if len(value) == 1:
                value = value[0]
            if ((self.lemmas is None or value in self.lemmas) and 
                (self.predicate is None or self.predicate(word))):
                self.counter[value] += 1
            self.total_word_count += 1
            if self.total_word_count == self.word_limit:
                self.running = False
                break

        return False # Never save sentences

    def save_xls(self, filename=None):
        if filename is None and hasattr(self, 'filename'):
            base = os.path.splitext(self.filename)[0]
            filename = base + '.xls'
        wb = xlwt.Workbook()
        sheet = wb.add_sheet('Count')
        for row, lemma in enumerate(self.lemmas):
            sheet.write(row, 0, lemma)
            sheet.write(row, 1, self.counters[lemma])
        wb.save(filename)

    def display(self):
        for value, count in self.counters.items():
            print value, count
