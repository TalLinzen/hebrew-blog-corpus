class Filter(object):

    def __init__(self):
        self.sentences = []

    def process_many(self, bgufile):
        for sentence in bgufile:
            result = self.process(sentence)
            if result:
                self.sentences.append(sentence)
