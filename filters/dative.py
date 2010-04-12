# -*- coding: utf-8 -*-

from filter import Filter
from by_user_annotation import ByUserAnnotation

class DativeFilter(Filter):

    lamed = u'ל'
    vav_lamed = u'ול'
    lamed_fused_forms = [u'לי', u'לך', u'לו', u'לה', u'לנו', u'לכם', u'לכן',
            u'להם', u'להן']

    class Annotation(ByUserAnnotation):

        prefix = 'dat'
        def get_highlight_area(self, sentence):
            m = min(sentence.lamed_indices)
            return (m, m)

    def is_dative(self, word):
        return word.pos == 'noun' and \
                    word.prefix in (self.lamed, self.vav_lamed) \
                    or word.lemma == self.lamed \
                    or word.base in self.lamed_fused_forms
                # Last test is in theory redundant but works around
                # disambiguation errors

    def process(self, sentence):

        sentence.lamed_indices = []

        for index, word in enumerate(sentence.words):
            if self.is_dative(word):
                sentence.lamed_indices.append(index)
                
        return len(sentence.lamed_indices) > 0
