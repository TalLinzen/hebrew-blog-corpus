# -*- coding: utf-8 -*-

from possessive import PossessiveFilter
from by_user_annotation import ByUserAnnotation

class GenitiveFilter(PossessiveFilter):

    class Annotation(ByUserAnnotation):

        prefix = 'gen'
        def get_highlight_area(self, sentence):
            m = min(sentence.shel_verb_indices)
            return (m, m)

    def process(self, sentence):
        last_verb_index = -1
        obstructor_indices = []
        last_preposition = -1
        sentence.shel_verb_indices = set()
        chunk_starts = []

        for index, word in enumerate(sentence.words):

            if word.pos == 'punctuation' or word.prefix == u'ש':
                obstructor_indices.append(index)

            if self.is_relevant_verb(word):
                last_verb_index = index
                obstructor_indices = []
                chunk_starts = []

            if self.is_preposition(word):
                last_preposition = index

            if word.pos == 'shel-preposition':
                if len(chunk_starts) == 1 and \
                        last_verb_index != -1 and \
                        last_preposition == last_verb_index + 1 and \
                        len(obstructor_indices) == 0:
                    sentence.shel_verb_indices.add(last_verb_index)

            if word.chunk == 'B-NP':
                chunk_starts.append(index)
            
        return len(sentence.shel_verb_indices) > 0


