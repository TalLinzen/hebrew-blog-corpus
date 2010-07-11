# -*- coding: utf-8 -*-

import sys, os, lucene, threading, time, codecs
from datetime import datetime

index_dir = '/Users/tal/corpus/lucene_index'

class Ticker(object):

    def __init__(self):
        self.tick = True

    def run(self):
        while self.tick:
            sys.stdout.write('.')
            sys.stdout.flush()
            time.sleep(1.0)

class IndexCorpus(object):

    def __init__(self, index_dir, analyzer):

        if not os.path.exists(index_dir):
            os.mkdir(index_dir)

        store = lucene.SimpleFSDirectory(lucene.File(index_dir))
        self.writer = lucene.IndexWriter(store, analyzer, True, 
                lucene.IndexWriter.MaxFieldLength.LIMITED)
        self.writer.setMaxFieldLength(1048576)

    def finalize(self):
        ticker = Ticker()
        print 'optimizing index',
        threading.Thread(target=ticker.run).start()
        self.writer.optimize()
        self.writer.close()
        ticker.tick = False
        print 'done'

    def index(self, directory):
        for filename in sorted(os.listdir(directory), key=int):
            path = os.path.join(root, filename)
            if not filename.isdigit():
                continue
            if os.path.isdir(path):
                self.index_dir(directory)
            else:
                if int(filename) % 100 == 0:
                    print datetime.now().ctime(), filename
                try:
                    self.index_file(path)
                except Exception, e:
                    print "Indexing exception:", e

    def index_file(self, path):
        handle = codecs.open(path, encoding='utf8')
        s = handle.read()

        pos = s.find(u'\n\n') + 2    # Skip first block: declaration
        nextpos = 0
        sentence_index = 0

        while nextpos != len(s):
            nextpos = s.find(u'\n \n', pos)
            if nextpos == -1:
                nextpos = len(s)
            sentence_index = sentence_index + 1
            text = s[pos:nextpos]
            text = text.replace(u' ', u'@').strip()
            pos = nextpos + 2

            doc = lucene.Document()
            doc.add(lucene.Field("sentence_index", 
                str(sentence_index),
                lucene.Field.Store.YES,
                lucene.Field.Index.NOT_ANALYZED))
            doc.add(lucene.Field("filename", 
                filename, 
                lucene.Field.Store.YES, 
                lucene.Field.Index.NOT_ANALYZED))
            doc.add(lucene.Field("contents",
                text, 
                lucene.Field.Store.NO,
                lucene.Field.Index.ANALYZED))
            self.writer.addDocument(doc)

class BlogCorpusFilter(lucene.PythonTokenFilter):
    too_long_count = 0

    def __init__(self, inStream):
        super(BlogCorpusFilter, self).__init__(inStream)
        self.featureStack = []
        self.termAttr = self.addAttribute(lucene.TermAttribute.class_)
        self.save = inStream.cloneAttributes()
        self.inStream = inStream

    def incrementToken(self):
        if len(self.featureStack) > 0:
            syn = self.featureStack.pop()
            self.restoreState(syn)
            return True

        if not self.inStream.incrementToken():
            return False

        self.addAliasesToStack()
        return True

    declaration = 'word prefix base suffix lemma pos postype gender number construct polarity tense person def pconj pint pprep psub ptemp prb suftype sufgen sufnum sufperson chunk'.split()

    def getFeatures(self, arg):
        if len(arg) == 255:
            # Lucene CharTokenizer silly limitation, should find a workaround
            self.__class__.too_long_count += 1
            print 'Too long count: %d' % self.__class__.too_long_count
            return ['dummy1212']
        else:
            if arg[0] == '@':
                arg = arg[1:]
            try:
                word, prefix, base, suffix, lemma, pos, rest = arg.split('@', 6)
            except ValueError:
                print 'Problem:', repr(arg)
                return ['dummy343434']
            else:
                ret = ['w%s' % word, 'l%s' % lemma]
        #ret = ['%d|%s' % (i, x) for i, x in enumerate(arg.strip().split()) if i < 3]
        return ret

    def addAliasesToStack(self):
        features = self.getFeatures(self.termAttr.term())
        if features is None:
            return

        current = self.captureState()

        for feature in features:
            self.save.restoreState(current)
            attr = self.save.addAttribute(lucene.TermAttribute.class_)
            attr.setTermBuffer(feature)
            attr = self.save.addAttribute(lucene.PositionIncrementAttribute.class_)
            attr.setPositionIncrement(0)
            self.featureStack.append(self.save.captureState())

class BlogCorpusAnalyzer(lucene.PythonAnalyzer):
    def tokenStream(self, fieldName, reader):
        tokenStream = lucene.WhitespaceTokenizer(reader)
        return BlogCorpusFilter(tokenStream)

class NewlineTokenizer(lucene.PythonCharTokenizer):
    'Not used because slow'
    def isTokenChar(self, c):
        return c != u'\n'

def search():
    lucene.initVM()
    command = u'wלאכול'
    #command = u'lלא'
    directory = lucene.SimpleFSDirectory(lucene.File(index_dir))
    searcher = lucene.IndexSearcher(directory, True)
    analyzer = lucene.StandardAnalyzer(lucene.Version.LUCENE_CURRENT)
    query = lucene.QueryParser(lucene.Version.LUCENE_CURRENT, "contents",
                        analyzer).parse(command)
    res = searcher.search(query, 50)
    print 'Total hits:', res.totalHits
    return [searcher.doc(doc.doc) for doc in res.scoreDocs]

def test():
    lucene.initVM()
    print 'lucene', lucene.VERSION
    start = datetime.now()
    try:
        #dir = '/Users/tal/corpus/analyzed/5'
        dir = '/Users/tal/corpus/analyzed'
        #dir = '/Users/tal/Dropbox/Hebrew-Blog-Corpus/experiments/t'
        analyzer = BlogCorpusAnalyzer()
        idx = IndexCorpus(index_dir, analyzer)
        idx.indexDocs(dir)
        #for i in range(5, 6):
        #    idx.indexDocs(dir % i)
        idx.finalize()
        end = datetime.now()
        print end - start
    except Exception, e:
        print "Failed: ", e
