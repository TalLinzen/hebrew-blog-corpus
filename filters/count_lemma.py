# -*- coding: utf-8 -*-

from filter import Filter

class CountLemma(Filter):

    def __init__(self, lemmas):
        Filter.__init__(self)
        self.lemmas = set(lemmas)
        self.counters = {}
        for lemma in lemmas:
            self.counters[lemma] = 0

    def process(self, sentence):
        for word in sentence.words:
            if word.lemma in self.lemmas:
                self.counters[lemma] += 1
