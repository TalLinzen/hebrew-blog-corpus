try:
    import guppy
except ImportError:
    guppy = None

import sha1

class LeanWord(object):
    def __init__(self, word):
        self.word = word

class Filter(object):

    def __init__(self, guppy_interval=None):
        self.sentences = []
        self.sentence_hashes = set()
        self.running = True
        self.guppy_interval = guppy_interval
        if guppy is not None:
            self.hpy = guppy.hpy()

    def reduce_sentence_memory_footprint(self, sentence):
        sentence.words = [word.word for word in sentence.words]

    def process_and_record(self, sentence):
        result = self.process(sentence)
        if result:
            unique = ''.join(sentence.words) + sentence.metadata['user']
            digest = hashlib.sha1(unique).digest()
            if digest not in self.sentence_hashes:
                self.sentence_hashes.add(digest)
                self.sentences.append(sentence)

    def process_many(self, filters, sentences):
        if self not in filters:
            raise ValueError('self not in filters')
        for index, sentence in enumerate(sentences):
            for filter in filters:
                filter.process_and_record(sentence)
            self.reduce_sentence_memory_footprint(sentence)
