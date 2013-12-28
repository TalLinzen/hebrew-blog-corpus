# -*- coding: utf-8 -*-
from hbc.data.word_lists import pd_verbs, possession_black_list
from hbc.filters.parsing_filter import *
from hbc.tools.hspell import infinitives

clitic_forms = [u'י', u'ך', u'ו', u'ה', u'נו', u'כם', u'כן', u'ם', u'ן']
clitic_forms_special = [u'י', u'ך', u'ו', u'ה', u'נו', u'כם', u'כן', u'הם',
                        u'הן']
lamed_fused_forms = [u'ל' + form for form in clitic_forms_special]
lamed_fused_forms += [u'ו' + x for x in lamed_fused_forms]
lamed_reflexive_fused_forms = [u'לעצמ' + form for form in clitic_forms]
lamed_reflexive_fused_forms += [u'ו' + x for x in lamed_reflexive_fused_forms]
lamed_quasi_pronouns = (lamed_reflexive_fused_forms + 
                        [u'לאנשים', u'לדברים', u'לזה'])
lamed_quasi_pronouns += [u'ו' + x for x in lamed_quasi_pronouns]
shel_fused_forms = set([u'של' + form for form in clitic_forms_special])


class Bishvil(ParsingFilter):

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
    dative = (word.pos == 'noun' and 
              word.lemma not in false_datives and 
              word.prefix in (u'ל', u'ול') or 
              word.lemma == u'ל' or 
              word.base in lamed_fused_forms)
            # Last test is in theory redundant but works around
            # disambiguation errors
    if filter_infinitives:
        return dative and word.word not in infinitives 
    else:
        return dative

def is_dative_wrapped(word, state):
    if is_dative(word):
        if (word.word in lamed_fused_forms or 
            word.word in lamed_reflexive_fused_forms):
            state['argument'] = 'pronoun'
            return True
        elif word.word in lamed_quasi_pronouns:
            state['argument'] = 'quasi'
            return True
        else:
            state['argument'] = 'lexical'
            return True

class YeshDative(ParsingFilter):
    predicates = [ 
        one_of('word', (u'יש', u'אין'), export_field='lemma'),
        Once(is_dative_wrapped, highlight=True)
    ]

benefactive_verbs = (u'אפה', u'הכין', u'צייר', u'ארגן', u'בישל')
class Ditransitives(ParsingFilter):
    predicates = [ 
        one_of('lemma', benefactive_verbs, export_field='lemma'),
        Once(is_dative_wrapped, highlight=True)
    ]

governed_verbs = (u'שיקר', u'לעג', u'עזר', u'סלח', u'יעץ')
class GovernedDatives(ParsingFilter):
    predicates = [
        one_of('lemma', governed_verbs, export_field='lemma'),
        Once(is_dative_wrapped, highlight=True)
    ]

pd_verbs_short = (u'הרס', u'שבר', u'אכל', u'הסתכל', u'הרים')
transfer_verbs = (u'נתן', u'מסר', u'שלח', u'תרם', u'העביר')

def QuickDativePredicatesClass(p):
    class Class(ParsingFilter):
        predicates =  [
            one_of('lemma', p, export_field='lemma'),
            Once(is_dative_wrapped, highlight=True)
        ]
    return Class

class MiraDatives(ParsingFilter):
    predicates = [
        one_of('lemma', governed_verbs + benefactive_verbs + 
               pd_verbs_short + transfer_verbs, export_field='lemma'),
        Once(is_dative_wrapped, highlight=True)
    ]

class EthicalDatives(ParsingFilter):
    predicates = [
        one_of('lemma', (u'קיטר', u'התבכיין', u'התיפיף', u'נרדם'), 
               export_field='lemma'),
        Once(is_dative_wrapped, highlight=True)
    ]

def lucene_dative_topicalized(verbs, extra_query=''):
    '''
    lucene_dative([u'אפה', u'הכין', u'צייר', u'ארגן'],
        'birthyear:[1970 TO 1980]')

    after=True: dative should be after verb
    '''
    from hbc.io import BGULuceneSearch

    class Filt(ParsingFilter):
        predicates = [
                not_equal('pos', 'verb'), 
                Once(is_dative_wrapped, highlight=True),
                AnyNumberOf(equal('chunk', 'I-NP')),
                And(one_of('lemma', verbs, export_field='lemma'), 
                    equal('prefix', '_'))
            ]

    filt = Filt()
    query = '(%s)' % ' OR '.join(['l' + verb for verb in verbs])
    if extra_query != '':
        query += ' AND ' + extra_query
    print query
    luc = BGULuceneSearch(query)
    filt.process_many(luc)
    return filt
       

class DitransitivesPD(ParsingFilter):
    predicates = [
        one_of('lemma', (u'לקח', u'גנב'), export_field='lemma'),
        Once(is_dative_wrapped, highlight=True)
    ]

class YeshAfterDative(ParsingFilter):
    predicates = [
        Once(is_dative_wrapped, highlight=True),
        AnyNumberOf(equal('chunk', 'I-NP')),
        one_of('word', (u'יש', u'אין'), export_field='lemma')
    ]

class NatanDative(ParsingFilter):
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


class AnyDativeWithPronoun(ParsingFilter):
    predicates = [
        And(not_one_of('lemma', possession_black_list),
            equal('pos', 'verb'), on_match=store('lemma', 'verb'),
            highlight=True),
        Once(one_of('word', lamed_fused_forms)),
        Once(is_preposition)
    ]

class ReflexiveDative(ParsingFilter):
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
    match = (len(set((word.lemma, word.prefix)) & 
                 set(expected_prepositions)) > 0)
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

class PossessiveDative(ParsingFilter):
    # Abstract class; use one of the subclasses that define self.dative
    private = ['in_chunk']
    before_dative = [Once(one_of('lemma', set(pd_verbs.keys()),
            export_field='verb'))]
    after_dative = [
        #AnyNumberOf(equal('chunk', 'I-NP')),      # Not for one word
        And(is_the_expected_preposition, set_in_chunk),
        Conditional(store_possessum, lambda s: not s['in_chunk']),
        ZeroWidth(not_equal('chunk', 'I-NP'))
    ]
    def build_predicate_list(self):
        return self.before_dative + [self.dative] + self.after_dative

class PossessiveDativeWithPronoun(PossessiveDative):
    dative = Once(one_of('word', lamed_fused_forms), highlight=True)

class PossessiveDativeOneWord(PossessiveDative):
    dative = Once(is_dative_wrapped, highlight=True)

class Genitive(ParsingFilter):
    private = ['in_chunk']
    before_genitive = [
        Once(one_of('lemma', set(pd_verbs.keys()),
            export_field='verb'), highlight=True),
        ZeroWidth(set_in_chunk),
        Once(is_the_expected_preposition),
        Conditional(store_possessum, lambda s: not s['in_chunk'])
    ]
    def build_predicate_list(self):
        return self.before_genitive + self.genitive

def is_shel(word, state):
    if word.word == u'של': 
        state['argument'] = 'lexical'
        return True
    elif word.word in shel_fused_forms:
        state['argument'] = 'pronoun'
        return False

class GenitiveWithPronoun(Genitive):
    genitive = [
        And(equal('pos', 'shel-preposition'),
            one_of('word', shel_fused_forms))
    ]

class GenitiveOneWord(Genitive):
    genitive = [
        Once(is_shel),
        Conditional(equal('chunk', 'I-NP'), 
                    lambda s: s['argument'] == 'lexical'),
        ZeroWidth(not_equal('chunk', 'I-NP')),
        ZeroWidth(not_equal('prefix', u'ש'))
    ]
