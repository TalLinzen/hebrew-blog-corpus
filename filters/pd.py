# -*- coding: utf-8 -*-

from possessive import PossessiveFilter
from dative import DativeFilter

class PossessiveDativeFilter(PossessiveFilter, DativeFilter):

    def __init__(self, single_word_complement=False, **kwargs):
        PossessiveFilter.__init__(self, **kwargs)
        DativeFilter.__init__(self, **kwargs)
        self.single_word_complement = single_word_complement

    annotation_prefix = 'pd'
    def get_highlight_area(self, sentence):
        m = sentence.lamed_index
        return (m, m)

    def process(self, sentence):
        verb_indices = set()
        lamed_phrases = []
        obstructor_indices = set()
        preposition_indices = set()
        last_start_of_lamed_phrase = -1
    
        for index, word in enumerate(sentence.words):
            if last_start_of_lamed_phrase != -1 and \
                    word.chunk != 'I-NP':
                lamed_phrases.append(
                        (last_start_of_lamed_phrase, index - 1))
                last_start_of_lamed_phrase = -1

            if self.is_relevant_verb(word):
                verb_indices.add(index)

            if self.is_preposition(word):
                preposition_indices.add(index)

            if self.is_obstructor(word):
                obstructor_indices.add(index)

            if self.is_dative(word):
                last_start_of_lamed_phrase = index

            if last_start_of_lamed_phrase != -1:
                lamed_phrases.append(
                        (last_start_of_lamed_phrase, index))
        
        lamed_indices = [(start, end) \
                for start, end in lamed_phrases \
                if start - 1 in verb_indices \
                and end + 1 in preposition_indices \
                and len(set(range(start, end + 1)) & obstructor_indices) == 0]

        if len(lamed_indices) > 0:
            sentence.lamed_index = lamed_indices[0][0]
            print 'LAMED:', sentence.lamed_index
            verb_index = max(i for i in verb_indices if \
                    i < sentence.lamed_index)
            print 'VERB:', verb_index
            verb = sentence.words[verb_index].lemma
            if self.verb_count_still_low(verb):
                sentence.metadata['verb'] = verb
                print 'VERB:', sentence.metadata['verb'].encode('utf8')
                return True

        return False

