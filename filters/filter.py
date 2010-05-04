#try:
#    import guppy
#except ImportError:
#    guppy = None

import hashlib

class Filter(object):

    def __init__(self, guppy_interval=None):
        self.sentences = []
        self.sentence_hashes = set()
        self.running = True

#        self.guppy_interval = guppy_interval
#        if guppy is not None:
#            self.hpy = guppy.hpy()

    def process_and_record(self, sentence):
        result = self.process(sentence)
        if result:
            unique = ''.join(sentence.words).encode('utf8') + \
                    sentence.metadata.get('user', '')
            digest = hashlib.sha1(unique).digest()
            if digest not in self.sentence_hashes:
                self.sentence_hashes.add(digest)
                self.sentences.append(sentence)

    def process_many(self, sentences, other_filters=None):
        filters = [self] if other_filters is None else [self] + other_filters
        for index, sentence in enumerate(sentences):
            some_still_running = False
            for filter in filters:
                if filter.running:
                    some_still_running = True
                filter.process_and_record(sentence)
            sentence.reduce_memory_footprint()
            if not some_still_running:
                break
