# -*- coding: utf-8 -*-
from generic import *
from .tools.hspell import infinitives
from .data.word_lists import pd_verbs, possession_black_list

clitic_forms = [u'י', u'ך', u'ו', u'ה', u'נו', u'כם', u'כן', u'ם', u'ן']
clitic_forms_special = [u'י', u'ך', u'ו', u'ה', u'נו', u'כם', u'כן', u'הם', u'הן']
lamed_fused_forms = [u'ל' + form for form in clitic_forms_special]
lamed_reflexive_fused_forms = [u'לעצמ' + form for form in clitic_forms]
lamed_quasi_pronouns = [u'לאנשים', u'לדברים', u'לזה']
shel_fused_forms = set([u'של' + form for form in clitic_forms_special])


class Bishvil(GenericFilter):

    bishvil_fused = [u'בשביל' + c for c in clitic_forms]

    def bishvil(word, state):
        if word.word == u'בשביל':
            state['argument'] = 'lexical'; return True
        elif word.word in Bishvil.bishvil_fused:
            state['argument'] = 'pronoun'; return True

    def not_conjunction(word, state):
        good = word.tense != 'inf' and \
                (word.prefix is None or u'ש' not in word.prefix) and \
                word.word not in infinitives
        return good

    predicates = [
        Once(bishvil, highlight=True),
        not_conjunction
    ]

false_datives = [
    u'רגע',
    u'כבוד',
    u'צד',
    u'הנאה'
]

def is_dative(word, filter_infinitives=True):
    dative = word.pos == 'noun' and \
                word.lemma not in false_datives and \
                word.prefix in (lamed, vav_lamed) \
                or word.lemma == lamed \
                or word.base in lamed_fused_forms
            # Last test is in theory redundant but works around
            # disambiguation errors
    if filter_infinitives:
        return dative and word.word not in infinitives 
    else:
        return dative

def is_dative_wrapped(word, state):
    if is_dative(word):
        if word.word in lamed_fused_forms or \
                word.word in lamed_reflexive_fused_forms:
            state['argument'] = 'pronoun'
        elif word.word in lamed_quasi_pronouns:
            state['argument'] = 'quasi'
        else:
            state['argument'] = 'lexical'
        return True


class YeshDative(GenericFilter):
    predicates = [
        one_of('word', (u'יש', u'אין'), export_field='lemma'),
        Once(is_dative_wrapped, highlight=True)
    ]

class NatanDative(GenericFilter):
    # Annotate by 'argument'
    predicates = [
            equal('lemma', u'נתן'),
            Once(is_dative_wrapped, highlight=True),
            AnyNumberOf(equal('chunk', 'I-NP')),
            one_of('chunk', ['B-NP', 'I-NP']),
            AnyNumberOf(equal('chunk', 'I-NP')),
            not_one_of('word', infinitives)
        ]

def is_preposition(word, state):
    clitic_prepositions = set([
        u'ל',
        u'ב',
        u'כ',
        u'מ'
    ])

    if word.prefix == u'ש':
        return False

    if word.pos == 'at-preposition' or word.pos == 'preposition':
        state['preposition'] = word.lemma
        return True
    elif word.prefix in clitic_prepositions:
        state['preposition'] = word.prefix
        return True


class AnyDativeWithPronoun(GenericFilter):
    predicates = [
        And(not_one_of('lemma', possession_black_list),
            equal('pos', 'verb'), on_match=store('lemma', 'verb'),
            highlight=True),
        Once(one_of('word', lamed_fused_forms)),
        Once(is_preposition)
    ]

class ReflexiveDative(GenericFilter):
    predicates = [
        And(not_one_of('lemma', possession_black_list),
            equal('pos', 'verb'),
            equal('person', '1'),
            equal('number', 's'),
            on_match=store('lemma', 'verb'),
            highlight=True),
        Once(equal('word', u'לי')),
        Once(is_preposition)
    ]

def is_the_expected_preposition(word, state):
    if word.prefix in (u'ש', u'וש'):
        return False

    expected_prepositions = pd_verbs[state['verb']]
    match = len(set((word.lemma, word.prefix)) & \
            set(expected_prepositions)) > 0
    return match

def store_possessum(word, state):
    pronouns = {
        '1smf': u'אני',
        '1sf': u'אני',
        '2sm': u'אתה',
        '2sf': u'את',
        '3sm': u'הוא',
        '3sf': u'היא',
        '1pmf': u'אנחנו',
        '2pm': u'אתם',
        '2pf': u'אתן',
        '3pm': u'הם',
        '3pf': u'הן'
    }

    if word.suftype == 'pron':
        pron_repr = '%s%s%s' % (word.sufperson, word.sufnum, word.sufgen)
        state['possessum'] = pronouns.get(pron_repr, pron_repr)
    else:
        state['possessum'] = word.lemma
    return True

def set_in_chunk(word, state):
    state['in_chunk'] = word.chunk == 'B-NP' and word.word != u'את'
    # chunker behaves differently for את and על
    if state['in_chunk']:
        store_possessum(word, state)
    return True

class PossessiveDativeWithPronoun(GenericFilter):
    private = ['in_chunk']
    predicates = [
        Once(one_of('lemma', set(pd_verbs.keys()),
            export_field='verb')),
        Once(one_of('word', lamed_fused_forms), highlight=True),
        AnyNumberOf(equal('chunk', 'I-NP')),
        And(is_the_expected_preposition, set_in_chunk),
        Conditional(store_possessum, lambda s: not s['in_chunk']),
        Once(not_equal('chunk', 'I-NP'))
    ]

class PossessiveDativeWithPronoun(GenericFilter):
    private = ['in_chunk']
    predicates = [
        Once(one_of('lemma', set(pd_verbs.keys()),
            export_field='verb')),
        Once(is_dative_wrapped, highlight=True),
        AnyNumberOf(equal('chunk', 'I-NP')),
        And(is_the_expected_preposition, set_in_chunk),
        Conditional(store_possessum, lambda s: not s['in_chunk']),
        Once(not_equal('chunk', 'I-NP'))
    ]

class GenitiveWithPronoun(GenericFilter):
    private = ['in_chunk']
    predicates = [
        Once(one_of('lemma', set(pd_verbs.keys()),
            export_field='verb'), highlight=True),
        ZeroWidth(set_in_chunk),
        Once(is_the_expected_preposition),
        Conditional(store_possessum, lambda s: not s['in_chunk']),
        
        And(equal('pos', 'shel-preposition'),
            one_of('word', shel_fused_forms))
    ]


