# -*- coding: utf-8 -*-

from filter import Filter

class CountLemmas(Filter):

    def __init__(self, lemmas, word_limit=None, predicate=None):
        '''
        Lemmas should be utf8 encoded
        '''
        Filter.__init__(self)
        self.counters = dict((lemma.decode('utf8'), 0) for lemma in lemmas)
        self.word_limit = word_limit
        self.predicate = predicate
        self.total_word_count = 0

    def process(self, sentence):
        for word in sentence.words:
            if word.lemma in self.counters and \
                    self.predicate is not None and self.predicate(word):
                self.counters[word.lemma] += 1
            self.total_word_count += 1
            if self.total_word_count == self.word_limit:
                self.running = False
                break

        return False # Never save sentences

    def display(self):
        for lemma, count in self.counters.items():
            print lemma, count
