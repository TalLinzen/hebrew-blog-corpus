import hashlib, copy

class Filter(object):

    def __init__(self):
        self.sentences = []
        self.sentence_hashes = set()
        self.running = True

    def process_and_record(self, sentence):
        result = self.process(sentence)
        if result:
            # This is strong: remove all duplicate sentences
            unique = ''.join(sentence.words).encode('utf8')
            digest = hashlib.sha1(unique).digest()
            if digest not in self.sentence_hashes:
                self.sentence_hashes.add(digest)
                self.sentences.append(sentence)

    def process_many(self, sentences, other_filters=None):
        filters = [self] if other_filters is None else [self] + other_filters
        for index, sentence in enumerate(sentences):
            some_still_running = False
            for filter in filters:
                # Same words, but possibly eventually different metadata
                sentence_copy = sentence.clone()
                if filter.running:
                    some_still_running = True
                filter.process_and_record(sentence_copy)
                sentence_copy.reduce_memory_footprint()
            if not some_still_running:
                break
