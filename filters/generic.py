# -*- coding: utf-8 -*-
from filter import Filter
from .tools.hspell import infinitives

class GenericFilter(Filter):

    predicates = []

    def __init__(self):
        Filter.__init__(self)
        if len(self.predicates) == 0:
            raise NotImplementedError("Must provide at least one predicate")
        self.processed_predicates = []
        self.predicate_options = []
        for predicate in self.predicates:
            if type(predicate) != tuple:
                self.processed_predicates.append((predicate, {}))
            else:
                self.processed_predicates.append(predicate)

    def is_obstructor(self, word):
        return word.pos == 'punctuation' or word.prefix in (u'ש', u'ו', u'וש')

    def process(self, sentence):
        metadatas = []
        for index, word in enumerate(sentence.rich_words):
            predicate, options = self.processed_predicates[len(metadatas)]
            new_metadata = predicate(word)
            if new_metadata is not None:
                if options.get('highlight', False):
                    # Currently supports only single word highlight
                    sentence.highlight = (index, index)
                metadatas.append(new_metadata)
            else:
                metadatas = []

            if len(metadatas) == len(self.predicates):
                break

        if len(metadatas) == len(self.predicates):
            for metadata in metadatas:
                sentence.metadata.update(metadata)
            return True
        else:
            return False


class Bishvil(GenericFilter):

    clitic_forms = [u'י', u'ך', u'ו', u'ה', u'נו', u'כם', u'כן', u'ם', u'ן']
    bishvil_fused = [u'בשביל' + c for c in clitic_forms]

    def bishvil(word):
        if word.word == u'בשביל':
            return {'argument': 'lexical'}
        elif word.word in Bishvil.bishvil_fused:
            return {'argument': 'pronoun'}

    def not_conjunction(word):
        good = word.tense != 'inf' and \
                (word.prefix is None or u'ש' not in word.prefix) and \
                word.word not in infinitives
        if good:
            return {}

    predicates = [
            (bishvil, {'highlight': True}),
            not_conjunction
        ]

