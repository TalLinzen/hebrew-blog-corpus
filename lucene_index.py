# -*- coding: utf-8 -*-

import sys, os,  threading, time, codecs, lucene
from lucene import \
    Document, Field, TermAttribute, TermAttribute, PositionIncrementAttribute, \
    WhitespaceTokenizer, SimpleFSDirectory, IndexSearcher, StandardAnalyzer, \
    Version, File, QueryParser, initVM, PythonTokenFilter, PythonAnalyzer, \
    IndexWriter
from datetime import datetime
from db import WebPage, User

index_dir = '/Users/tal/corpus/index_4_to_10'

class IndexCorpus(object):

    def __init__(self, index_dir, analyzer):
        if not os.path.exists(index_dir):
            os.mkdir(index_dir)

        store = SimpleFSDirectory(File(index_dir))
        self.writer = IndexWriter(store, analyzer, True, 
                IndexWriter.MaxFieldLength.LIMITED)
        self.writer.setMaxFieldLength(1048576)

    def finalize(self):
        self.writer.optimize()
        self.writer.close()

    def index(self, directory):
        for filename in sorted(os.listdir(directory), key=int):
            path = os.path.join(directory, filename)
            if not filename.isdigit():
                continue
            if os.path.isdir(path):
                self.index(path)
            else:
                if int(filename) % 100 == 0:
                    print datetime.now().ctime(), filename
                try:
                    self.index_file(path)
                except Exception, e:
                    print "Indexing exception:", e

    def index_file(self, path):
        handle = codecs.open(path, encoding='utf8')
        filename = os.path.basename(path)
        user_number = WebPage.get(filename).user
        user_record = list(User.select(User.q.number == user_number))[0]
        gender = user_record.sex if user_record.sex is not None else "Unknown"
        birthyear = (str(user_record.birthyear) 
                if user_record.birthyear is not None else '0')

        s = handle.read()

        pos = s.find(u'\n\n') + 2    # Skip first block: declaration
        nextpos = 0
        sentence_index = 0

        YES = Field.Store.YES
        NO = Field.Store.NO
        NOT_ANALYZED = Field.Index.NOT_ANALYZED
        ANALYZED = Field.Index.ANALYZED

        while nextpos != len(s):
            nextpos = s.find(u'\n \n', pos)
            if nextpos == -1:
                nextpos = len(s)
            sentence_index = sentence_index + 1
            text = s[pos:nextpos]
            text = text.replace(u' ', u'@').strip()
            pos = nextpos + 2

            doc = Document()
            doc.add(Field("sentence_index", str(sentence_index), YES,
                NOT_ANALYZED))
            doc.add(Field("user", user_number, YES, NOT_ANALYZED))
            doc.add(Field("gender", gender, YES, NOT_ANALYZED))
            doc.add(Field("birthyear", birthyear, YES, NOT_ANALYZED))
            doc.add(Field("filename", filename, YES, NOT_ANALYZED))
            doc.add(Field("contents", text, NO, ANALYZED))
            self.writer.addDocument(doc)

class BlogCorpusFilter(PythonTokenFilter):
    too_long_count = 0

    def __init__(self, inStream):
        super(BlogCorpusFilter, self).__init__(inStream)
        self.featureStack = []
        self.termAttr = self.addAttribute(TermAttribute.class_)
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
            attr = self.save.addAttribute(TermAttribute.class_)
            attr.setTermBuffer(feature)
            attr = self.save.addAttribute(PositionIncrementAttribute.class_)
            attr.setPositionIncrement(0)
            self.featureStack.append(self.save.captureState())

class BlogCorpusAnalyzer(PythonAnalyzer):
    def tokenStream(self, fieldName, reader):
        tokenStream = WhitespaceTokenizer(reader)
        return BlogCorpusFilter(tokenStream)

def search():
    initVM()
    command = u'wלאכול'
    #command = u'lלא'
    directory = SimpleFSDirectory(File(index_dir))
    searcher = IndexSearcher(directory, True)
    analyzer = StandardAnalyzer(Version.LUCENE_CURRENT)
    query = QueryParser(Version.LUCENE_CURRENT, "contents",
                        analyzer).parse(command)
    res = searcher.search(query, 50)
    print 'Total hits:', res.totalHits
    return [searcher.doc(doc.doc) for doc in res.scoreDocs]

def test():
    initVM()
    print ',', lucene.VERSION
    start = datetime.now()
    try:
        #dir = '/Users/tal/corpus/analyzed/4'
        dir = '/Users/tal/corpus/analyzed'
        #dir = '/Users/tal/Dropbox/Hebrew-Blog-Corpus/experiments/t'
        analyzer = BlogCorpusAnalyzer()
        idx = IndexCorpus(index_dir, analyzer)
        idx.index(dir)
        for i in range(4, 10):
            idx.index_dir(dir % i)
        idx.finalize()
        end = datetime.now()
        print end - start
    except Exception, e:
        print "Failed: ", e
