# -*- coding: utf-8 -*-

from filter import Filter

class PossessiveDative(Filter):

    verbs_selecting_l = set([u'נתן',
            u'היה',
            u'הראה',
            u'נמאס',
            u'האמין',
            u'הודיע',
            u'הבטיח',
            u'הזכיר',
            u'נדמה'
            u'נראה',
            u'מסר',
            u'לקח',
            u'העניק',
            u'הסביר',
            u'גילה',
            u'קרה',
            u'בא',
            u'אמר',
            u'קנה',
            u'הרשה',
            u'העביר',
            u'סיפר',
            u'עזר',
            u'הגיד',
            u'החזיר'])

    lamed = u'ל'
    vav_lamed = u'ול'
    lamed_fused_forms = [u'לי', u'לך', u'לו', u'לה', u'לנו', u'לכם', u'לכן',
            u'להם', u'להן']
    max_distance = 0      # Between a verb and its associated lamed phrase
    debug = False

    clitic_prepositions = set([
        u'ל',
        u'ב',
        u'כ',
        u'מ'
    ])

    def __init__(self):
        Filter.__init__(self)
        self.natan = []

    def process(self, sentence):
        verb_indices = set()
        lamed_phrases = []
        punctuation_indices = set()
        preposition_indices = set()
        last_start_of_lamed_phrase = -1

        for index, word in enumerate(sentence.words):
            if word.lemma == u'נתן':
                self.natan.append(sentence)
            if word.pos == 'punctuation':
                punctuation_indices.add(index)
            if last_start_of_lamed_phrase != -1 and \
                    word.chunk != 'I-NP':
                lamed_phrases.append(
                        (last_start_of_lamed_phrase, index - 1))
                last_start_of_lamed_phrase = -1
            if word.pos == 'verb' and \
                    word.lemma not in self.verbs_selecting_l:
                verb_indices.add(index)
            if word.pos == 'at-preposition' \
                    or word.pos == 'preposition' \
                    or word.prefix in self.clitic_prepositions \
                    or word.pos == 'noun': # and getattr(word, 'def') == False:
                preposition_indices.add(index)
            if word.pos == 'noun' and \
                    word.prefix in (self.lamed, self.vav_lamed) \
                    or word.lemma == self.lamed \
                    or word.base in self.lamed_fused_forms:
                # Last test is in theory redundant but works around
                # disambiguation errors
                last_start_of_lamed_phrase = index

        if last_start_of_lamed_phrase != -1:
            lamed_phrases.append(
                    (last_start_of_lamed_phrase, index))
        
        sentence.lamed_indices = [(start, end) \
                for start, end in lamed_phrases \
                if start - 1 in verb_indices \
                and end + 1 in preposition_indices]

        if self.debug:
            sentence.pprint(reverse=True)

            for i, w in enumerate(sentence.words):
                print i, w

            print 'punctuation:', punctuation_indices
            print 'preposition:', preposition_indices
            print 'lamed:', lamed_phrases
            print
            print

        return len(sentence.lamed_indices) > 0

