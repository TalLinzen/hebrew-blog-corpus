# -*- coding: utf-8 -*-
from filter import Filter
from .tools.hspell import infinitives
import unittest

builtin_predicates = ['is_obstructor', 'anything']

predicate_factories = ['equal', 'not_equal', 'one_of', 'not_one_of', 'store',
        'remove']

predicate_modifiers = ['Once', 'And', 'Or', 'ZeroWidth', 'Conditional',
        'Repeated', 'AnyNumberOf', 'Optional']

__all__ = builtin_predicates + predicate_factories + predicate_modifiers + \
        ['GenericFilter']

clitic_forms = [u'י', u'ך', u'ו', u'ה', u'נו', u'כם', u'כן', u'ם', u'ן']
clitic_forms_special = [u'י', u'ך', u'ו', u'ה', u'נו', u'כם', u'כן', u'הם', u'הן']
debug = False

########
# State
########

class State(dict):
    
    def __init__(self, *args, **kwargs):
        dict.__init__(self, *args, **kwargs)
        self.lookahead = False

    def __setitem__(self, attr, value):
        if not self.lookahead:
            dict.__setitem__(self, attr, value)

    def __getitem__(self, attr):
        if attr in self or not self.lookahead:
            return dict.__getitem__(self, attr)
        else:
            return None


#############################################
# Builtin predicates and predicate factories
#############################################

def is_obstructor(word, state):
    return word.pos == 'punctuation' or word.prefix in (u'ש', u'וש')

def anything(word, state):
    return True

def equal(field, value):
    def predicate(word, state):
        return getattr(word, field) == value
    return predicate

def not_equal(field, value):
    def predicate(word, state):
        return getattr(word, field) != value
    return predicate

def one_of(field, values, export_field=None):
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

def not_one_of(field, values):
    def predicate(word, state):
        return getattr(word, field) not in values
    return predicate

def store(field, as_variable):
    def predicate(word, state):
        state[as_variable] = getattr(word, field)
    return predicate

def remove(variable):
    def predicate(word, state):
        del state[variable]
    return predicate

######################
# Predicate Modifiers
######################

class PredicateModifier(object):

    def __init__(self, predicate=None, **options):
        if predicate is not None and not callable(predicate):
            raise ValueError("Predicate must be callable")
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

class PredicateCombination(PredicateModifier):
    def __init__(self, *predicates, **options):
        PredicateModifier.__init__(self, **options)
        self.predicates = predicates

class And(PredicateCombination):

    def parse(self, index, sentence, state):
        matched = True
        for predicate in self.predicates:
            if not predicate(sentence.rich_words[index], state):
                matched = False
                break
        if matched:
            index += 1
        return matched, index
        
class Or(PredicateCombination):

    def parse(self, index, sentence, state):
        matched = False
        for predicate in self.predicates:
            if predicate(sentence.rich_words[index], state):
                matched = True
                break
        if matched:
            index += 1
        return matched, index
        
class ZeroWidth(PredicateModifier):
    '''
    Match word without moving to next word. Can be used to manipulate state.
    '''
    def parse(self, index, sentence, state):
        matched = self.predicate(sentence.rich_words[index], state)
        return matched, index

    def is_zero_length(self):
        return True

class Conditional(Once):
    '''
    If condition obtains, match against predicate and move to the
    next word, as in Once; otherwise do nothing
    '''
    def __init__(self, predicate, condition, **options):
        Once.__init__(self, predicate, **options)
        self.condition = condition

    def parse(self, index, sentence, state):
        if self.condition(state):
            return Once.parse(self, index, sentence, state)
        else:
            return True, index


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
                if next_predicate.lookahead(index, sentence, state) \
                        and index - original_index >= self.at_least:
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

class Optional(Repeated):
    def __init__(self, predicate, **options):
        Repeated.__init__(self, predicate, greedy=True,
                at_least=0, at_most=1, **options)


#################
# Generic Filter
#################

class GenericFilter(Filter):

    predicates = []
    internal = ['next_predicate']
    private = []
    counted_features = []

    def __init__(self):
        Filter.__init__(self)
        self.predicates = self.predicates or self.build_predicate_list()
        if len(self.predicates) == 0:
            raise NotImplementedError("Must provide at least one predicate")
        self.normalize_predicates()
        self.normalize_counted_features()
        self.setup_counts()

    def normalize_counted_features(self):
        normalized = []
        for feature in self.counted_features:
            if isinstance(feature, basestring):
                normalized.append(((feature,), None))
            else: # tuple
                features, limit = feature
                if isinstance(features, basestring):
                    features = (features,)
                normalized.append((features, limit))
        self.counted_features = normalized

    def setup_counts(self):
        self.counts = {}
        for features, limit in self.counted_features:
            self.counts[features] = {}

    def normalize_predicates(self):
        normalized = []
        for predicate in self.predicates:
            if not isinstance(predicate, PredicateModifier):
                normalized.append(Once(predicate))
            else:
                normalized.append(predicate)
        self.predicates = normalized

    def process(self, sentence):
        state = State()
        index = 0
        predicate_index = 0
        last_index_outside_match = 0
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
                #print '%d: %d -> %d' % (predicate_index, old_index, index)
                predicate_index += 1
                if predicate.options.get('highlight', False):
                    state['highlight'] = (old_index, index - 1)
                on_match = predicate.options.get('on_match')
                if on_match:
                    on_match(sentence.rich_words[index - 1], state)
            else:
                #print
                last_index_outside_match += 1   # Rudimentary backtracking
                index = last_index_outside_match
                predicate_index = 0
                state = State()

            if predicate_index == len(self.predicates):
                break

        rest_are_zero = all(p.is_zero_length() for \
                p in self.predicates[predicate_index:]) 
        if predicate_index == len(self.predicates) or rest_are_zero:
            keep_sentence = self.update_counts(state)
            self.post_process(sentence)
            for key, value in state.items():
                if key not in self.private + self.internal:
                    sentence.metadata[key] = state[key]
            return keep_sentence
        else:
            return False

    def update_counts(self, state):
        keep_sentence = False
        for features, limit in self.counted_features:
            value = tuple(state[f] for f in features)
            count = self.counts[features]
            count[value] = count.get(value, 0) + 1
            if limit is None or count[value] <= limit:
                keep_sentence = True
        if len(self.counted_features) == 0:
            keep_sentence = True
        return keep_sentence

    def post_process(self, sentence):
        pass


########
# Tests
########

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

    def test_simple_backtracking(self):
        self.t([eq('c'), eq('d')])

    def test_conditional(self):
        class TestFilter(GenericFilter):
            def set_state(x, s):
                s['b_after_2b'] = x == 'b'
                return True
            predicates = [Repeated(eq('b'), 1, 1),
                    ZeroWidth(set_state),
                    Once(anything),
                    Conditional(lambda x, s: x == 'c', 
                        lambda s: s['b_after_2b'])]
        self.assertTrue(TestFilter().process(self.sentence))

    def test_optional_no(self):
        self.t([Repeated(eq('b'), 3, 3), Optional(eq('q')), eq('c')])

    def test_optional_yes(self):
        self.t([eq('b'), Optional(eq('c')), Optional(eq('c')), eq('d')])

    def runTest(self):
        self.test_repeated()
        self.test_anynumber()
        self.test_anynumber_at_end()
        self.test_repeat_at_end()
        self.test_notgreedy()
        self.test_greedy()
        self.test_notgreedy2()
        self.test_anything()
        self.test_simple_backtracking()
        self.test_conditional()
        self.test_optional_no()
        self.test_optional_yes()
