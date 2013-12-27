import lucene

class BlogCorpusFilter(lucene.PythonTokenFilter):
    too_long_count = 0

    def __init__(self, inStream):
        super(BlogCorpusFilter, self).__init__(inStream)
        self.inStream = inStream
        self.featureStack = []
        self.termAttr = self.addAttribute(lucene.TermAttribute.class_)
        self.posAttr = self.addAttribute(
                lucene.PositionIncrementAttribute.class_)
        self.n_features = 5
        self.feature_index = self.n_features
        self.token_count = 0

    def incrementToken(self):
        if self.feature_index < self.n_features:
            if self.feature_index == 1:
                self.posAttr.setPositionIncrement(0)
            self.termAttr.setTermBuffer(self.features[self.feature_index])
            self.feature_index += 1
            return True
        else:
            self.token_count += 1
            if not self.inStream.incrementToken():
                return False
            self.getFeatures(self.termAttr.term())
            self.termAttr.setTermBuffer(self.features[0])
            self.feature_index = 1
            return True

    def getFeatures(self, arg):
        if len(arg) == 0:
            self.features = ['dummy0000', 'dummy0000']
        elif len(arg) == 255:
            # Lucene CharTokenizer silly limitation, should find a workaround
            self.__class__.too_long_count += 1
            print 'Too long count: %d' % self.__class__.too_long_count
            self.features = ['dummy1212'] * self.n_features
        else:
            if arg[0] == '@':
                arg = arg[1:]
            try:
                word, prefix, base, suffix, lemma, pos, rest = arg.split('@', 6)
            except ValueError:
                print 'Problem:', repr(arg)
                self.features = ['dummy3434'] * self.n_features
            else:
                self.features = ['w%s' % word, 'l%s' % lemma, 'b%s' % base,
                        'pos%s' % pos, 'prf%s' % prefix]


class BlogCorpusAnalyzer(lucene.PythonAnalyzer):
    def tokenStream(self, fieldName, reader):
        tokenStream = lucene.WhitespaceTokenizer(reader)
        return BlogCorpusFilter(tokenStream)

