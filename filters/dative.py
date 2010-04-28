# -*- coding: utf-8 -*-

from filter import Filter
from by_user_annotation import MixUsers, ByAttributeAnnotation
from .tools.hspell import get_infinitives

class DativeFilter(Filter):

    lamed = u'ל'
    vav_lamed = u'ול'
    lamed_fused_forms = [
        u'לי',
        u'לך',
        u'לו',
        u'לה',
        u'לנו',
        u'לכם',
        u'לכן',
        u'להם',
        u'להן'
    ]

    false_datives = [
        u'רגע',
        u'כבוד',
        u'צד',
        u'הנאה'
    ]

    infinitives = get_infinitives()

    class Annotation(ByAttributeAnnotation):
        attribute = 'pre_dative'
        prefix = 'dat'
        def get_highlight_area(self, sentence):
            m = min(sentence.lamed_indices)
            return (m, m)

    def __init__(self, pre_dative_lemmas=None, filter_infinitives=True, 
            **kwargs):
        '''
        pre_dative_lemmas: Only retain sentence if lemma before dative
            is in this list (default: None, retain everything)
        filter_infinitives: Boolean: check if alleged dative is in fact an
            infinitive using hspell's verb list
        '''
        Filter.__init__(self)
        self.pre_dative_lemmas = pre_dative_lemmas
        self.filter_infinitives = filter_infinitives
        if self.pre_dative_lemmas is not None:
            self.counters = dict((x, 0) for x in self.pre_dative_lemmas)
        self.limit = 5000

    def is_dative(self, word):
        dative = word.pos == 'noun' and \
                    word.lemma not in self.false_datives and \
                    word.prefix in (self.lamed, self.vav_lamed) \
                    or word.lemma == self.lamed \
                    or word.base in self.lamed_fused_forms
                # Last test is in theory redundant but works around
                # disambiguation errors
        if self.filter_infinitives:
            return dative and word.word not in self.infinitives 
        else:
            return dative

    def process(self, sentence):

        sentence.lamed_indices = []
        last_pre_dative_index = -10

        for index, word in enumerate(sentence.words):
            if self.pre_dative_lemmas is not None and \
                    word.lemma in self.pre_dative_lemmas:
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
