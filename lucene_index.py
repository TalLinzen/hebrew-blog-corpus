# -*- coding: utf-8 -*-
# profile.run('execfile("lucene_index.py"); execfile("run.py"); setup_connection(""); test()')
import sys, os,  threading, time, codecs, lucene
from lucene import \
    Document, Field, TermAttribute, TermAttribute, PositionIncrementAttribute, \
    WhitespaceTokenizer, SimpleFSDirectory, IndexSearcher, StandardAnalyzer, \
    Version, File, QueryParser, initVM, PythonTokenFilter, PythonAnalyzer, \
    IndexWriter
from datetime import datetime
from db import WebPage, User

index_dir = '/Users/tal/corpus/lucene_index'

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

        doc = Document()
        sentence_index_field = Field("sentence_index", str(sentence_index), YES,
            NOT_ANALYZED)
        user_field = Field("user", '', YES, NOT_ANALYZED)
        gender_field = Field("gender", '', YES, NOT_ANALYZED)
        birthyear_field = Field("birthyear", '', YES, NOT_ANALYZED)
        filename_field = Field("filename", '', YES, NOT_ANALYZED)
        contents_field = Field("contents", '', NO, ANALYZED)
        doc.add(sentence_index_field)
        doc.add(user_field)
        doc.add(gender_field)
        doc.add(birthyear_field)
        doc.add(filename_field)
        doc.add(contents_field)

        while nextpos != len(s):
            nextpos = s.find(u'\n \n', pos)
            if nextpos == -1:
                nextpos = len(s)
            sentence_index = sentence_index + 1
            text = s[pos:nextpos]
            text = text.strip().replace(u' ', u'@')
            pos = nextpos + 2

            sentence_index_field.setValue(str(sentence_index))
            user_field.setValue(user_number)
            gender_field.setValue(gender)
            birthyear_field.setValue(birthyear)
            filename_field.setValue(filename)
            contents_field.setValue(text)
            self.writer.addDocument(doc)

class BlogCorpusFilter(PythonTokenFilter):
    too_long_count = 0

    def __init__(self, inStream):
        super(BlogCorpusFilter, self).__init__(inStream)
        self.inStream = inStream
        self.featureStack = []
        self.termAttr = self.addAttribute(TermAttribute.class_)
        self.posAttr = self.addAttribute(PositionIncrementAttribute.class_)
        self.n_features = 2
        self.feature_index = self.n_features
        self.features = [''] * self.n_features

    def incrementToken(self):
        if self.feature_index < self.n_features:
            self.termAttr.setTermBuffer(self.features[self.feature_index])
            self.feature_index += 1
            return True
        else:
            self.feature_index = 0
            if not self.inStream.incrementToken():
                return False

            self.posAttr.setPositionIncrement(0)
            self.getFeatures(self.termAttr.term())
            return True

    declaration = 'word prefix base suffix lemma pos postype gender number construct polarity tense person def pconj pint pprep psub ptemp prb suftype sufgen sufnum sufperson chunk'.split()

    def getFeatures(self, arg):
        if len(arg) == 255:
            # Lucene CharTokenizer silly limitation, should find a workaround
            self.__class__.too_long_count += 1
            print 'Too long count: %d' % self.__class__.too_long_count
            self.features ['dummy1212'] * self.n_features
        else:
            try:
                word, prefix, base, suffix, lemma, pos, rest = arg.split('@', 6)
            except ValueError:
                print 'Problem:', repr(arg)
                self.features = ['dummy3434'] * self.n_features
            else:
                self.features = ['w%s' % word, 'l%s' % lemma]


class BlogCorpusAnalyzer(PythonAnalyzer):
    def tokenStream(self, fieldName, reader):
        tokenStream = WhitespaceTokenizer(reader)
        return BlogCorpusFilter(tokenStream)

def search(d=index_dir):
    initVM()
    command = u'wלאכול'
    command = u'"lשלום lקורא"'
    directory = SimpleFSDirectory(File(d))
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
        dir = '/Users/tal/corpus/analyzed/4'
        #dir = '/Users/tal/corpus/analyzed'
        #dir = '/Users/tal/Dropbox/Hebrew-Blog-Corpus/experiments/t'
        analyzer = BlogCorpusAnalyzer()
        idx = IndexCorpus(index_dir, analyzer)
        idx.index(dir)
        #for i in range(4, 10):
        #    idx.index_dir(dir % i)
        idx.finalize()
        end = datetime.now()
        print end - start
    except Exception, e:
        print "Failed: ", e
