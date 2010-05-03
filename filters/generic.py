# -*- coding: utf-8 -*-
from filter import Filter
from .tools.hspell import infinitives
import unittest

clitic_forms = [u'י', u'ך', u'ו', u'ה', u'נו', u'כם', u'כן', u'ם', u'ן']
clitic_forms_special = [u'י', u'ך', u'ו', u'ה', u'נו', u'כם', u'כן', u'הם', u'הן']

def is_obstructor(word, state):
    return word.pos == 'punctuation' or word.prefix in (u'ש', u'וש')

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
    def __init__(self, predicate):
        self.predicate = predicate

class Once(PredicateModifier):
    def parse(self, index, sentence, state):
        matched = self.predicate(sentence.rich_words[index], state)
        if matched:
            index += 1
        return matched, index

class Repeated(PredicateModifier):
    unlimited = -1
    def __init__(self, predicate, at_least=0, at_most=unlimited):
        PredicateModifier.__init__(self, predicate)
        self.at_least = at_least
        self.at_most = at_most
    def parse(self, index, sentence, state):
        original_index = index
        while self.predicate(sentence.rich_words[index], state) and \
                (index - original_index <= self.at_most or \
                self.at_most == Repeated.unlimited):
            index += 1

        matched = index - original_index >= self.at_least
        return matched, index

class AnyNumberOf(Repeated):
    '''
    An alias for Repeated(0, unlimited), for clarity
    '''
    def __init__(self, predicate):
        Repeated.__init__(self, predicate, 0, Repeated.unlimited)

class GenericFilter(Filter):

    predicates = []
    private_variables = []

    def __init__(self):
        Filter.__init__(self)
        if len(self.predicates) == 0:
            raise NotImplementedError("Must provide at least one predicate")
        self.processed_predicates = []
        self.predicate_options = []
        for predicate in self.predicates:
            if type(predicate) != tuple:
                self.processed_predicates.append((self.wrap_in_modifier(predicate), {}))
            else:
                self.processed_predicates.append((self.wrap_in_modifier(predicate[0]), predicate[1]))

    def wrap_in_modifier(self, predicate):
        if not isinstance(predicate, PredicateModifier):
            return Once(predicate)
        else:
            return predicate

    def process(self, sentence):
        state = {}
        index = 0
        next_predicate = 0
        while index != len(sentence.rich_words):
            predicate, options = self.processed_predicates[next_predicate]
            old_index = index
            matched, index = predicate.parse(index, sentence, state)

            if matched:
                next_predicate += 1
                if options.get('highlight', False):
                    sentence.highlight = (old_index, index - 1)
            else:
                assert index == old_index, "Shouldn't change index if didn't match"
                index += 1
                next_predicate = 0
                state = {}

            if next_predicate == len(self.predicates):
                break

        if next_predicate == len(self.predicates):
            for key, value in state.items():
                if value not in self.private_variables:
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
        (bishvil, {'highlight': True}),
        not_conjunction
    ]

from dative import is_dative
from .tools.hspell import infinitives

lamed_fused_forms = [u'ל' + form for form in clitic_forms_special]
lamed_reflexive_fused_forms = [u'לעצמ' + form for form in clitic_forms]
lamed_quasi_pronouns = [u'לאנשים', u'לדברים', u'לזה']

def is_dative_wrapped(word, state):
    if is_dative(word):
        if word.word in lamed_fused_forms or word.word in lamed_reflexive_fused_forms:
            state['argument'] = 'pronoun'
        elif word.word in lamed_quasi_pronouns:
            state['argument'] = 'quasi'
        else:
            state['argument'] = 'lexical'
        return True

class YeshDative(GenericFilter):
    # Annotate by 'lemma' and 'argument'
    def yesh_or_ein(word, state):
        if word.word in (u'יש', u'אין'):
            state['lemma'] = word.word
            return True

    predicates = [
        OneOf('word', (u'יש', u'אין'), export_field='lemma'),
        (is_dative_wrapped, {'highlight': True})
    ]

class NatanDative(GenericFilter):
    # Annotate by 'argument'
    def noun(word, state):
        return word.pos == 'noun' and word.word not in infinitives

    def not_infinitive(word, state):
        return word.word not in infinitives

    predicates = [
            Equal('lemma', u'נתן'),
            (is_dative_wrapped, {'highlight': True}),
            AnyNumberOf(Equal('chunk', 'I-NP')),
            OneOf('chunk', ['B-NP', 'I-NP']),
            AnyNumberOf(Equal('chunk', 'I-NP')),
            not_infinitive
        ]

class PossessiveDative(GenericFilter):
    verbs = {
        u'אכל': u'את',
        u'הרס': u'את',
        u'הרים': u'את',
        u'הסתכל': u'על'
    }

    def is_the_expected_preposition(word, state):
        if word.prefix in (u'ש', u'וש'):
            return False

        expected_prepositions = PossessiveDative.verbs[state['verb']]
        if isinstance(expected_prepositions, basestring):
            expected_prepositions = (expected_prepositions,)
        return len(set((word.lemma, word.prefix)) & set(expected_prepositions)) > 0

    predicates = [
            OneOf('lemma', set(verbs.keys()), export_field='verb'),
            (is_dative_wrapped, {'highlight': True}),
            AnyNumberOf(Equal('chunk', 'I-NP')),
            is_the_expected_preposition
        ]

class DS(object):
    'Dummy Sentence'
    def __init__(self, words):
        self.rich_words = words
        self.metadata = {}

class Tests(unittest.TestCase):

    def test_repeated(self):
        sentence = DS(list('abbbccd'))
        class TestFilter(GenericFilter):
            predicates = [lambda x: x == 'a',
                    Repeated(lambda x: x == 'b', 3, 3),
                    lambda x: x == 'c']
        tf = TestFilter()
        self.assertTrue(tf.process(sentence))

    def test_anynumber(self):
        sentence = DS(list('abbbccd'))
        class TestFilter(GenericFilter):
            predicates = [
                    AnyNumberOf(lambda x: x == 'o'),
                    Repeated(lambda x: x == 'b', 1, 4),
                    lambda x: x == 'c']
        tf = TestFilter()
        self.assertTrue(tf.process(sentence))

    def runTest(self):
        self.test_repeated()
        self.test_anynumber()
