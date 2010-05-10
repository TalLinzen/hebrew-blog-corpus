import hashlib, copy

class Filter(object):
    '''
    Base class for filters.

    To create a filter, inherit from this class and implement the 'process'
    method. This method should gets a single arguent, the sentence to process,
    and return a boolean value: sentence passed or did not pass the filter.
    In addition it can modify the sentence's metadata dictionary.
    '''

    def __init__(self, remove_duplicates=True):
        '''
        If remove_duplicates is set, remove all duplicate sentences. This
        is strong -- another conceivable option would be to remove duplicates
        only if they are from the same user, etc.
        '''

        self.sentences = []
        self.running = True
        self.remove_duplicates = remove_duplicates
        self.sentence_hashes = set()

    def process_and_record(self, sentence):
        result = self.process(sentence)
        if result:
            if self.remove_duplicates:
                unique = ''.join(sentence.words).encode('utf8')
                digest = hashlib.sha1(unique).digest()
                if digest not in self.sentence_hashes:
                    self.sentence_hashes.add(digest)
                    self.sentences.append(sentence)
            else:
                self.sentences.append(sentences)

    def process_many(self, sentences, other_filters=None):
        '''
        Gets an iterator over sentences, and optionally a list of additional
        filters that will process (copies of) the same sentences. The current
        filter will process the sentences no matter if it is in this list.
        '''

        filters = set([self])
        if other_filters is not None: 
            filters |= set(other_filters)

        for index, sentence in enumerate(sentences):
            some_still_running = False
            for filt in filters:
                # Same words, but possibly eventually different metadata
                sentence_copy = sentence.clone()
                if filt.running:
                    some_still_running = True
                filt.process_and_record(sentence_copy)
                sentence_copy.reduce_memory_footprint()
            if not some_still_running:
                break

    def process(self, sentence):
        raise NotImplementedError("The 'process' method must be implemented")
