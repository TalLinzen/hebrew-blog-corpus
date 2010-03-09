# -*- coding: utf-8 -*-

from filter import Filter

interesting_verbs = u'אכל'

class SubcategorizationFrames(Filter):

    nonclitic_prepositions = {
        u'עם': 'im',
        u'על': 'al',
        u'אל': 'el',
        u'מן': 'min',
        u'אצל': 'etsel',
        u'מפני': 'mipnei',
        u'בפני': 'bifnei',
        u'אחרי': 'achrei'
    }

    clitic_prepositions = {
        u'ל': 'le',
        u'ב': 'be',
        u'כ': 'ke',
        u'מ': 'me'
    }

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
        self.dicts = {}
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
            self.feed_word(index, word)
            if self.stop:
                break

    def argument_found(self, kind):
        self.sentence.argument = kind
        self.potential_argument_zone = False
        self.stop = True

    def feed_word(self, index, word):
        global w
        w = word
        #if lemma == 'ali' and named_entity == 'I_PERS':    # specific hack
        #    lemma, analysis, base_form, named_entity, np_chunk = ('ali', ['', 'IN', ''], 'al', 'O', 'O')

        is_verb = word.pos in ('verb', 'participle', 'modal')
        includes_conj = word.pos == 'conjunction'
        is_rel = word.prefix == 'rel-subconj' and \
                self.last_preposition_index != index - 1
        is_punc = word.pos == 'punctuation'
        is_question = word.pos == 'interrogative' \
                or word.lemma in self.question_words
        is_infinitive = word.person == 'inf'   # HACK! Should be word.tense
        is_np_chunk = word.chunk in ('B-NP', 'I-NP') or word.pos == 'noun' 
        # Originally: analysis[1].startswith('NN'), makes any difference?
        is_pronoun = word.pos == 'pronoun'
        is_nonclitic_preposition = word.pos == 'preposition' and \
                word.lemma in self.nonclitic_prepositions

        if is_nonclitic_preposition:
            self.last_preposition_index = index
            self.last_preposition = word.lemma
        if is_verb:
            self.verb_found = True
        if word.pos == 'at-preposition' and self.verb_found == False:
            self.dangling_direct_object = True
        if is_rel and self.last_np_chunk == index - 1:
            if debug: print '%d: Possibly in relative clause' % index
            self.possibly_in_relative_clause = True
        if is_punc:
            self.last_punctuation = index
            
        if self.possibly_in_relative_clause and \
                self.last_punctuation == index - 1:
            if debug: print '%d: No longer in relative clause' % index
            self.possibly_in_relative_clause = False
        if is_np_chunk:
            self.last_np_chunk = index
        if word.pos == 'preposition' and not is_np_chunk:    
            # dangling clitic preposition
            self.last_preposition_index = index
            self.last_preposition = word.prefix
            # problem when prefix is composed of more than one clitic elements
            # (ve-be, she-be), should be parsed as 'v^b^xxx' but this does not 
            # always happen. but is this ever an actual problem?

        if not self.potential_argument_zone and is_verb:
            if word.lemma in self.interesting_verbs:
                self.counters[word.lemma] = self.counters.get(word.lemma, 0) + 1
            self.verb_index = index
            if self.counters.get(word.lemma, 0) >= self.max_tokens:
                self.stop = True
                return
            self.verb = word.lemma
            if self.potential_argument_zone:
                self.argument_found('NONE')
            if word.lemma in self.interesting_verbs:
                self.good_sentence = True
                self.potential_argument_zone = True
                l = self.dicts.setdefault(word.lemma, [])
                l.append(self.sentence)

        else:
            if self.potential_argument_zone:
                if is_punc or includes_conj:  
                    # Punctuation or conjunction usually mean end of interesting
                    # VP (though not always - "open and close the door")
                    self.ended_without_determined_object(index)
                elif is_rel:
                    if self.last_preposition_index == index - 1:
                        self.argument_found('NONE (CP?)')
                    else:
                        self.argument_found('CP')
                elif is_question:
                    self.argument_found('Q')
                elif is_infinitive:
                    self.argument_found('IP')
                elif is_verb:   
                    # Another non-infinitive verb: interesting VP finished
                    self.ended_without_determined_object(index)
                elif is_np_chunk:

                    preposition = None
                    if word.prefix in self.clitic_prepositions:
                        preposition = self.clitic_prepositions[word.prefix]
                    elif word.pos == 'at-preposition' and \
                            word.base in self.at_comitative_forms:
                        preposition = u'עם'
                    elif word.pos == 'preposition' and \
                            word.lemma in self.nonclitic_prepositions:
                        preposition = self.nonclitic_prepositions[word.lemma]
                    elif self.last_preposition_index == index - 1:
                        preposition = self.last_preposition

                    if preposition == 'min':
                        preposition = 'me'

                    if preposition:
                        self.argument_found(u'PP-%s' % preposition)
                    else:
                        # Should be NP. Is it a probable direct object? 
                        # If definite, needs "at"
                        if word.lemma == u'הוא' and \
                                word.pos != 'at-preposition' or \
                                getattr(word, 'def') and \
                                word.base not in (u'הכל', u'הכול'):
                            self.ended_without_determined_object(index)
                        else:
                            self.argument_found('NP')


    def ended_without_determined_object(self, index):

        self.punctuation_found = True
        if self.possibly_in_relative_clause or self.dangling_direct_object:
            self.argument_found('NONE (NP?)')
        elif self.last_preposition_index == index - 1: 
            # dangling preposition, sometimes happens with 'lSm' to there,
            # 'ali' to me etc
            self.argument_found('PP')
        else:
            self.argument_found('NONE')

