# -*- coding: utf-8 -*-

from possessive import PossessiveFilter
from dative import DativeFilter
from by_user_annotation import ByUserAnnotation

class PossessiveDativeFilter(PossessiveFilter, DativeFilter):

    def __init__(self, single_word_complement=False, **kwargs):
        PossessiveFilter.__init__(self, **kwargs)
        self.single_word_complement = single_word_complement

    class Annotation(ByUserAnnotation):

        prefix = 'pd'
        def get_highlight_area(self, sentence):
            m = min(sentence.lamed_indices)[0]
            return (m, m)

    def process(self, sentence):
        verb_indices = set()
        lamed_phrases = []
        punctuation_indices = set()
        preposition_indices = set()
        last_start_of_lamed_phrase = -1
    
        for index, word in enumerate(sentence.words):
            if word.pos == 'punctuation':
                punctuation_indices.add(index)

            if last_start_of_lamed_phrase != -1 and \
                    word.chunk != 'I-NP':
                lamed_phrases.append(
                        (last_start_of_lamed_phrase, index - 1))
                last_start_of_lamed_phrase = -1

            if self.is_relevant_verb(word):
                verb_indices.add(index)

            if self.is_preposition(word):
                preposition_indices.add(index)

            if self.is_dative(word):
                last_start_of_lamed_phrase = index

            if last_start_of_lamed_phrase != -1:
                lamed_phrases.append(
                        (last_start_of_lamed_phrase, index))
        
        sentence.lamed_indices = [(start, end) \
                for start, end in lamed_phrases \
                if start - 1 in verb_indices \
                and end + 1 in preposition_indices]

        if len(sentence.lamed_indices) > 0:
            start = sentence.lamed_indices[0][0]
            sentence.first_verb = sentence.words[start - 1].lemma
            return True
        else:
            return False

