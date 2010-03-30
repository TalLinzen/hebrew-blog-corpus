# -*- coding: utf-8 -*-

from possessive import PossessiveFilter

class GenitiveFilter(PossessiveFilter):

    def process(self, sentence):
        last_verb_index = -1
        obstructor_indices = []
        preposition_indices = []
        sentence.shel_verb_indices = set()
        chunk_starts = []

        for index, word in enumerate(sentence.words):

            if word.pos == 'punctuation' or word.prefix == u'ש':
                obstructor_indices.append(index)

            if word.pos == 'verb' and \
                    word.lemma not in self.verbs_selecting_l:
                last_verb_index = index
                obstructor_indices = []
                chunk_starts = []

            #if word.pos == 'at-preposition' \
            #        or word.pos == 'preposition' \
            #        or word.prefix in self.clitic_preposition:
            #    preposition_indices.add(index)

            if word.pos == 'shel-preposition':
                if len(chunk_starts) == 1 and \
                        last_verb_index != -1 and \
                        len(obstructor_indices) == 0:
                    sentence.shel_verb_indices.add(last_verb_index)

            if word.chunk == 'B-NP':
                chunk_starts.append(index)
            
        if self.debug:
            sentence.pprint(reverse=True)

            for i, w in enumerate(sentence.words):
                print i, w

            print 'punctuation:', punctuation_indices
            print 'preposition:', preposition_indices
            print 'lamed:', lamed_phrases
            print
            print

        return len(sentence.shel_verb_indices) > 0


