# -*- coding: utf-8 -*-

from filter import Filter


class SubcategorizationFrames(Filter):

    nonclitic_prepositions = set([
        u'עם',
        u'על',
        u'אל',
        u'מן',
        u'אצל',
        u'מפני',
        u'בפני',
        u'אחרי'
    ])

    clitic_prepositions = set([
        u'ל',
        u'ב',
        u'כ',
        u'מ'
    ])

    question_words = set([
        u'אם',
        u'איך',
        u'כיצד',
        u'מתי',
        u'כמה',
        u'איזה',
        u'למה',
        u'מדוע'
    ])

    at_comitative_forms = set([
        u'איתי',
        u'אתי',
        u'איתך',
        u'אתך',
        u'איתו',
        u'אתו',
        u'איתה',
        u'אתה',
        u'איתנו',
        u'אתנו',
        u'איתכם',
        u'איתכן',
        u'איתם',
        u'אתם',
        u'איתן',
        u'אתן'
    ])
    # slight problem with homographous accusative and comitative forms atkm 
    # and atkn - we exclude them from the list so they will always be
    # analyzed as accusative

    def __init__(self, interesting_verbs=[], max_tokens=200):
        self.dict = {}
        self.counters = {}
        self.max_tokens = max_tokens
        self.interesting_verbs = interesting_verbs

    def process(self, sentence):
        self.sentence = sentence
        self.verb_index = -10
        self.argument = 'UNKNOWN'
        self.potential_argument_zone = False
        self.possibly_in_relative_clause = False
        self.dangling_direct_object = False
        self.stop = False
        self.last_preposition_index = -5
        self.last_punctuation = -5
        self.last_np_chunk = -5
        self.verb_found = False

        for index, word in enumerate(sentence.words):
            self.index = index
            self.feed_word(word)
            if self.stop:
                break

        self.post_process()

    def argument_found(self, kind):
        self.sentence.argument = kind
        self.potential_argument_zone = False
        self.stop = True

    def post_process(self):
        if not hasattr(self.sentence, 'verb_index'):
            return
        lemma = self.sentence.words[self.sentence.verb_index].lemma
        l = self.dict.setdefault(lemma, [])
        if len(l) < self.max_tokens:
            l.append(self.sentence)

    def feed_word(self, word):
        #if lemma == 'ali' and named_entity == 'I_PERS':    # specific hack
        #    lemma, analysis, base_form, named_entity, np_chunk = ('ali', ['', 'IN', ''], 'al', 'O', 'O')

        is_verb = word.pos in ('verb', 'modal')
        if word.pos == 'participle' and word.lemma != word.word:
            is_verb = True
        is_rel = word.psub and self.last_preposition_index != self.index - 1
        is_question = word.pos == 'interrogative' \
                or word.lemma in self.question_words
        is_np_chunk = word.chunk in ('B-NP', 'I-NP') or word.pos == 'noun' \
                or word.pos == 'participle' and word.lemma == word.word
        is_nonclitic_preposition = word.pos == 'preposition' and \
                word.lemma in self.nonclitic_prepositions

        if is_nonclitic_preposition:
            self.last_preposition_index = self.index
            self.last_preposition = word.lemma
        if is_verb:
            self.verb_found = True
        if word.pos == 'at-preposition' and self.verb_found == False:
            self.dangling_direct_object = True
        if is_rel and self.last_np_chunk == self.index - 1:
            self.possibly_in_relative_clause = True
        if word.pos == 'punctuation':
            self.last_punctuation = self.index
            
        if self.possibly_in_relative_clause and \
                self.last_punctuation == self.index - 1:
            self.possibly_in_relative_clause = False
        if is_np_chunk:
            self.last_np_chunk = self.index
        if word.pos == 'preposition' and not is_np_chunk:    
            # dangling clitic preposition
            self.last_preposition_index = self.index
            self.last_preposition = word.prefix

        if not self.potential_argument_zone and is_verb:
            self.process_verb(word)
        else:
            if self.potential_argument_zone:
                if word.pos == 'punctuation' or word.pconj:  
                    # Punctuation or conjunction usually mean end of interesting
                    # VP (though not always - "open and close the door")
                    self.ended_without_determined_object()
                elif is_rel:
                    if self.last_preposition_index == self.index - 1:
                        self.argument_found('NONE(CP)')
                    else:
                        self.argument_found('CP')
                elif is_question:
                    self.argument_found('Q')
                elif word.tense == 'inf':
                    self.argument_found('IP')
                elif is_verb:   
                    # Another non-infinitive verb: interesting VP finished
                    self.ended_without_determined_object()
                elif is_np_chunk or word.pos == 'preposition':
                    preposition = self.detect_preposition(word)
                    if preposition:
                        self.argument_found(u'PP-%s' % preposition)
                    elif word.pos == 'preposition':
                        # Some other prep that doesn't introduce arguments
                        self.argument_found('NONE')
                    else:
                        # Should be NP. Is it a probable direct object? 
                        # If definite, needs "at"
                        if word.lemma == u'הוא' and \
                                word.pos != 'at-preposition' or \
                                word.pos == 'pronoun' or \
                                getattr(word, 'def') and \
                                word.base not in (u'הכל', u'הכול'):
                            self.ended_without_determined_object()
                        else:
                            self.argument_found('NP')

    def process_verb(self, word):
        if self.potential_argument_zone:
            self.argument_found('NONE')
        if word.lemma in self.interesting_verbs:
            self.counters[word.lemma] = self.counters.get(word.lemma, 0) + 1
            self.good_sentence = True
            self.sentence.verb_index = self.index
            self.potential_argument_zone = True
        if self.counters.get(word.lemma, 0) >= self.max_tokens:
            self.stop = True

    def detect_preposition(self, word):
        preposition = None
        if word.prefix in self.clitic_prepositions:
            preposition = word.prefix
        elif word.lemma in self.clitic_prepositions:
            preposition = word.lemma
        elif word.pos == 'at-preposition' and \
                word.word in self.at_comitative_forms:
            preposition = u'עם'
        elif word.pos == 'preposition' and \
                word.lemma in self.nonclitic_prepositions:
            preposition = word.lemma
        elif self.last_preposition_index == self.index - 1:
            preposition = self.last_preposition

        if preposition == u'מן':
            preposition = u'מ'

        return preposition

    def ended_without_determined_object(self):

        self.punctuation_found = True
        if self.possibly_in_relative_clause or self.dangling_direct_object:
            self.argument_found('NONE(NP)')
        elif self.last_preposition_index == self.index - 1: 
            # dangling preposition, sometimes happens with 'lSm' to there,
            # 'ali' to me etc
            self.argument_found('PP')
        else:
            self.argument_found('NONE')

class DativeFinder(SubcategorizationFrames):

    verbs_selecting_l = [u'נתן',
            u'היה',
            u'הראה',
            u'בישר',
            u'חסר',
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
            u'תרם',
            u'הציע',
            u'נענה',
            u'התרגל',
            u'חיכה',
            u'קנה',
            u'הרשה',
            u'העביר',
            u'סיפר',
            u'עזר',
            u'הגיד',
            u'החזיר']

    def __init__(self):
        SubcategorizationFrames.__init__(self, max_tokens=9999999)
        self.dict = {'all': []}

    def post_process(self):
        if not hasattr(self.sentence, 'verb_index') or \
                not hasattr(self.sentence, 'argument_type'):
            return
        verb_lemma = self.sentence.words[self.sentence.verb_index].lemma
        if self.sentence.argument_type == u'PP-ל' and \
                verb_lemma not in self.verbs_selecting_l:
            self.dict['all'].append(self.sentence)
