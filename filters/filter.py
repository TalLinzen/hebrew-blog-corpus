class Filter(object):

    def __init__(self):
        self.sentences = []

    def process_file(self, bgufile):
        for sentence in bgufile:
            result = self.process(sentence)
            if result:
                self.sentences.append(sentence)
