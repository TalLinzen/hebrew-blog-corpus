# -*- coding: utf-8 -*-

import codecs, os
import xlwt
from filter import Filter

class CountLemmas(Filter):

    def __init__(self, lemmas, field='lemma', word_limit=None, predicate=None):
        '''
        Lemmas should be utf8 encoded
        '''
        Filter.__init__(self)
        self.lemmas = lemmas
        self.counters = dict((lemma, 0) for lemma in lemmas)
        self.word_limit = word_limit
        self.predicate = predicate
        self.total_word_count = 0
        self.field = field

    @classmethod
    def from_file(cls, filename, **args):
        handle = codecs.open(filename, encoding='utf8')
        lemmas = [x.replace('"', '').strip() for x in handle.readlines()]
        obj = cls(lemmas, **args)
        obj.filename = filename
        return obj

    def process(self, sentence):
        for word in sentence.rich_words:
            value = getattr(word, self.field)
            if value in self.counters and \
                    (self.predicate is None or self.predicate(word)):
                self.counters[value] += 1
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
