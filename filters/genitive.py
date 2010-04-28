# -*- coding: utf-8 -*-

from possessive import PossessiveFilter

class GenitiveFilter(PossessiveFilter):

    def __init__(self, single_word_complement=False, **kwargs):
        PossessiveFilter.__init__(self, **kwargs)
        self.single_word_complement = single_word_complement

    annotation_prefix = 'gen'

    def process(self, sentence):
        last_verb_index = -1
        obstructor_indices = []
        last_preposition = -1
        verb_index = None
        chunk_starts = []

        for index, word in enumerate(sentence.rich_words):

            if self.is_obstructor(word):
                obstructor_indices.append(index)

            if self.is_relevant_verb(word):
                last_verb_index = index
                obstructor_indices = []
                chunk_starts = []

            if self.is_preposition(word):
                last_preposition = index

            if word.pos == 'shel-preposition':
                if len(chunk_starts) == 1 and \
                        ((not self.single_word_complement) or \
                            (index - 2 in chunk_starts)) and \
                        last_verb_index != -1 and \
                        last_preposition == last_verb_index + 1 and \
                        len(obstructor_indices) == 0:
                    verb_index = last_verb_index
                    break

            if word.chunk == 'B-NP':
                chunk_starts.append(index)

        if verb_index is not None:
            verb = sentence.rich_words[verb_index].lemma
            if self.verb_count_still_low(verb):
                sentence.metadata['verb'] = verb
                sentence.highlight = (verb_index, verb_index)
                return True

        return False


