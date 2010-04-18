try:
    import guppy
except ImportError:
    guppy = None


class LeanWord(object):
    def __init__(self, word):
        self.word = word

class Filter(object):

    def __init__(self, guppy_interval=None):
        self.sentences = []
        self.running = True
        self.guppy_interval = guppy_interval
        if guppy is not None:
            self.hpy = guppy.hpy()

    def reduce_sentence_memory_footprint(self, sentence):
        sentence.words = [word.word for word in sentence.words]

    def process_many(self, sentences):
        for index, sentence in enumerate(sentences):
            if self.guppy_interval is not None and \
                    index % self.guppy_interval == 0:
                print self.hpy.heap()
            result = self.process(sentence)
            if result:
                self.reduce_sentence_memory_footprint(sentence)
                self.sentences.append(sentence)
            if not self.running:
                break
