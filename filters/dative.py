# -*- coding: utf-8 -*-

from filter import Filter
from by_user_annotation import MixUsers, ByAttributeAnnotation

class DativeFilter(Filter):

    lamed = u'ל'
    vav_lamed = u'ול'
    lamed_fused_forms = [u'לי', u'לך', u'לו', u'לה', u'לנו', u'לכם', u'לכן',
            u'להם', u'להן']

    class Annotation(ByAttributeAnnotation):
        attribute = 'pre_dative'
        prefix = 'dat'
        def get_highlight_area(self, sentence):
            m = min(sentence.lamed_indices)
            return (m, m)

    def __init__(self, pre_dative_lemmas=None):
        Filter.__init__(self)
        self.pre_dative_lemmas = pre_dative_lemmas
        self.counters = dict((x, 0) for x in self.pre_dative_lemmas)
        self.limit = 5000

    def is_dative(self, word):
        return word.pos == 'noun' and \
                    word.prefix in (self.lamed, self.vav_lamed) \
                    or word.lemma == self.lamed \
                    or word.base in self.lamed_fused_forms
                # Last test is in theory redundant but works around
                # disambiguation errors

    def process(self, sentence):

        sentence.lamed_indices = []
        last_pre_dative_index = -10

        for index, word in enumerate(sentence.words):
            if word.lemma in self.pre_dative_lemmas:
                self.counters[word.lemma] += 1
                if self.counters[word.lemma] < self.limit:
                    last_pre_dative_index = index
                    sentence.metadata['pre_dative'] = word.lemma
            elif self.is_dative(word) and \
                    (self.pre_dative_lemmas is None or \
                    last_pre_dative_index == index - 1):
                sentence.lamed_indices.append(index)
                break
                
        return len(sentence.lamed_indices) > 0
