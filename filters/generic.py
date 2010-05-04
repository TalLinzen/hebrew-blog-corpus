# -*- coding: utf-8 -*-
from filter import Filter
from .tools.hspell import infinitives
import unittest

clitic_forms = [u'י', u'ך', u'ו', u'ה', u'נו', u'כם', u'כן', u'ם', u'ן']
clitic_forms_special = [u'י', u'ך', u'ו', u'ה', u'נו', u'כם', u'כן', u'הם', u'הן']
debug = False

class State(dict):
    
    def __init__(self, *args, **kwargs):
        dict.__init__(self, *args, **kwargs)
        self.lookahead = False

    def __setitem__(self, attr, value):
        if not self.lookahead:
            dict.__setitem__(self, attr, value)

def is_obstructor(word, state):
    return word.pos == 'punctuation' or word.prefix in (u'ש', u'וש')

def anything(word, state):
    return True

def Equal(field, value):
    def predicate(word, state):
        return getattr(word, field) == value
    return predicate

def OneOf(field, values, export_field=None):
    if export_field:
        def predicate(word, state):
            attr = getattr(word, field)
            if attr in values:
                state[export_field] = attr
                return True
    else:
        def predicate(word, state):
            return getattr(word, field) in values
    return predicate

class PredicateModifier(object):
    def __init__(self, predicate, **options):
        self.predicate = predicate
        self.options = options

    def lookahead(self, index, sentence, state):
        state.lookahead = True
        matched, index = self.parse(index, sentence, state)
        state.lookahead = False
        return matched

    def is_zero_length(self):
        return False

class Once(PredicateModifier):
    def parse(self, index, sentence, state):
        matched = self.predicate(sentence.rich_words[index], state)
        if matched:
            index += 1
        return matched, index

class Repeated(PredicateModifier):
    unlimited = -1

    def __init__(self, predicate, at_least=0, at_most=unlimited,
            greedy=False, **options):
        PredicateModifier.__init__(self, predicate, **options)
        self.at_least = at_least
        self.at_most = at_most
        self.greedy = greedy

    def parse(self, index, sentence, state):
        original_index = index
        next_predicate = state['next_predicate']

        while index < len(sentence.rich_words):
            current_word = sentence.rich_words[index]
            if not self.greedy and not state.lookahead and \
                    next_predicate is not None:
                if next_predicate.lookahead(index, sentence, state):
                    break

            if not self.at_most == Repeated.unlimited:
                if index - original_index == self.at_most:
                    break

            if not self.predicate(current_word, state):
                break

            index += 1

        matched = index - original_index >= self.at_least
        return matched, index

    def is_zero_length(self):
        return self.at_least == 0

class AnyNumberOf(Repeated):
    '''
    An alias for Repeated(0, unlimited), for clarity
    '''
    def __init__(self, predicate, greedy=False, **options):
        Repeated.__init__(self, predicate, at_least=0, 
                at_most=Repeated.unlimited, greedy=greedy, **options)

class GenericFilter(Filter):

    predicates = []
    internal = ['next_predicate']
    private = []

    def __init__(self):
        Filter.__init__(self)
        if len(self.predicates) == 0:
            raise NotImplementedError("Must provide at least one predicate")
        self.predicates = [self.wrap_in_modifier(x) for x in self.predicates]

    def wrap_in_modifier(self, predicate):
        if not isinstance(predicate, PredicateModifier):
            return Once(predicate)
        else:
            return predicate

    def process(self, sentence):
        state = State()
        index = 0
        predicate_index = 0
        while index != len(sentence.rich_words):
            predicate = self.predicates[predicate_index]
            old_index = index

            if predicate_index + 1 == len(self.predicates):
                state['next_predicate'] = None
            else:
                state['next_predicate'] = \
                        self.predicates[predicate_index + 1]

            matched, index = predicate.parse(index, sentence, state)

            if matched:
                if debug:
                    print '%d: %d -> %d' % (predicate_index, old_index, index)
                predicate_index += 1
                if predicate.options.get('highlight', False):
                    sentence.highlight = (old_index, index - 1)
            else:
                if debug:
                    print
                assert index == old_index, "Index shouldn't change if no match"
                index += 1
                predicate_index = 0
                state = State()

            if predicate_index == len(self.predicates):
                break

        rest_are_zero = all(p.is_zero_length() for \
                p in self.predicates[predicate_index:]) 
        if predicate_index == len(self.predicates) or rest_are_zero:
            for key, value in state.items():
                if key not in self.private + self.internal:
                    sentence.metadata[key] = state[key]
            self.post_process(sentence)
            return True
        else:
            return False

    def post_process(self, sentence):
        pass

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

from dative import is_dative
from .tools.hspell import infinitives

lamed_fused_forms = [u'ל' + form for form in clitic_forms_special]
lamed_reflexive_fused_forms = [u'לעצמ' + form for form in clitic_forms]
lamed_quasi_pronouns = [u'לאנשים', u'לדברים', u'לזה']

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

shel_fused_forms = set([u'של' + form for form in clitic_forms_special])

def is_shel(word, state):
    if word.word == u'של':
        state['argument'] = 'lexical'
        return True
    elif word.word in shel_fused_forms:
        state['argument'] = 'pronoun'
        return True

class YeshDative(GenericFilter):
    # Annotate by 'lemma' and 'argument'
    def yesh_or_ein(word, state):
        if word.word in (u'יש', u'אין'):
            state['lemma'] = word.word
            return True

    predicates = [
        OneOf('word', (u'יש', u'אין'), export_field='lemma'),
        Once(is_dative_wrapped, highlight=True)
    ]

class NatanDative(GenericFilter):
    # Annotate by 'argument'
    def noun(word, state):
        return word.pos == 'noun' and word.word not in infinitives

    def not_infinitive(word, state):
        return word.word not in infinitives

    predicates = [
            Equal('lemma', u'נתן'),
            Once(is_dative_wrapped, highlight=True),
            AnyNumberOf(Equal('chunk', 'I-NP')),
            OneOf('chunk', ['B-NP', 'I-NP']),
            AnyNumberOf(Equal('chunk', 'I-NP')),
            not_infinitive
        ]



governed_preps = {
    u'אכל': u'את',
    u'הרס': u'את',
    u'הרים': u'את',
    u'הסתכל': u'על'
}

for key in governed_preps.keys():
    if isinstance(governed_preps[key], basestring):
        governed_preps[key] = (governed_preps[key],)

def is_the_expected_preposition(word, state):
    if word.prefix in (u'ש', u'וש'):
        return False

    expected_prepositions = governed_preps[state['verb']]
    return len(set((word.lemma, word.prefix)) & set(expected_prepositions)) > 0

class PossessiveDative(GenericFilter):

    predicates = [
            OneOf('lemma', set(governed_preps.keys()), export_field='verb'),
            Once(is_dative_wrapped, highlight=True),
            AnyNumberOf(Equal('chunk', 'I-NP')),
            is_the_expected_preposition
        ]

class Genitive(GenericFilter):
    predicates = [
            Once(OneOf('lemma', set(governed_preps.keys()),
                export_field='verb'), highlight=True),
            is_the_expected_preposition,
            AnyNumberOf(Equal('chunk', 'I-NP')),
            Once(Equal('pos', 'shel-preposition'))
        ]


class DS(object):
    'Dummy Sentence'
    def __init__(self, words):
        self.rich_words = words
        self.metadata = {}

def eq(c):
    return lambda x, s: x == c

class Tests(unittest.TestCase):

    sentence = DS(list('abbbccd'))

    def t(self, preds):
        class TestFilter(GenericFilter):
            predicates = preds
        self.assertTrue(TestFilter().process(self.sentence))

    def test_repeated(self):
        self.t([eq('a'), Repeated(eq('b'), 3, 3), eq('c')])

    def test_anynumber(self):
        self.t([AnyNumberOf(eq('o')), Repeated(eq('b'), 1, 4), eq('c')])

    def test_anynumber_at_end(self):
        self.t([eq('d'), AnyNumberOf(eq('e'))])

    def test_repeat_at_end(self):
        self.t([Repeated(eq('d'), 1)])

    def test_notgreedy(self):
        self.t([Repeated(eq('b')), eq('b')])

    def test_greedy(self):
        class TestFilter(GenericFilter):
            predicates = [Repeated(eq('b'), greedy=True), eq('b')]
        self.assertFalse(TestFilter().process(self.sentence))

    def test_notgreedy2(self):
        self.t([AnyNumberOf(anything), eq('b'), AnyNumberOf(anything)])

    def test_anything(self):
        self.t([eq('a'), Repeated(anything, 5, 5), eq('d')])

    def runTest(self):
        self.test_repeated()
        self.test_anynumber()
        self.test_anynumber_at_end()
        self.test_repeat_at_end()
        self.test_notgreedy()
        self.test_greedy()
        self.test_notgreedy2()
        self.test_anything()
