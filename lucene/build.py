# -*- coding: utf-8 -*-
# profile.run('execfile("lucene_index.py"); execfile("run.py"); setup_connection(""); build_index()')
# initVM(); from AnalyzerUtils import AnalyzerUtils; AnalyzerUtils.displayTokensWithFullDetails(BlogCorpusAnalyzer(), open('/Users/tal/Dropbox/Hebrew-Blog-Corpus/experiments/t/1').read().replace(' ', '@'))
import sys, os,  threading, time, codecs, lucene, zlib
from lucene import \
    Document, Field, TermAttribute, TermAttribute, PositionIncrementAttribute, \
    WhitespaceTokenizer, SimpleFSDirectory, IndexSearcher, StandardAnalyzer, \
    Version, File, QueryParser, initVM, PythonTokenFilter, PythonAnalyzer, \
    IndexReader, IndexWriter, FieldCache
from common import BlogCorpusAnalyzer, BlogCorpusFilter
from datetime import datetime
from db import WebPage, User
from static_lz import trained_short_string_compressor

index_dir = '/Users/tal/corpus/lucene_index_full'

class IndexCorpus(object):

    def __init__(self, index_dir, analyzer):
        self.metadata = True
        if not os.path.exists(index_dir):
            os.mkdir(index_dir)

        store = SimpleFSDirectory(File(index_dir))
        self.writer = IndexWriter(store, analyzer, True, 
                IndexWriter.MaxFieldLength.LIMITED)
        self.writer.setMaxFieldLength(1048576)
        self.compressor = self.get_compressor()
        
    def get_compressor(self):
        path = '/Users/tal/corpus/analyzed/5/5344'
        training_data = codecs.open(path, encoding='utf8').read()
        return trained_short_string_compressor(training_data.encode('utf8'))

    def finalize(self):
        self.writer.optimize()
        self.writer.close()

    def index(self, directory):
        files = [x for x in os.listdir(directory) if x.isdigit()]
        for filename in sorted(files, key=int):
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
        print path
        YES = Field.Store.YES
        NO = Field.Store.NO
        NOT_ANALYZED = Field.Index.NOT_ANALYZED
        ANALYZED = Field.Index.ANALYZED
        metadata = self.metadata

        handle = codecs.open(path, encoding='utf8')
        filename = os.path.basename(path)
        if metadata:
            user_number = WebPage.get(filename).user
            user_record = list(User.select(User.q.number == user_number))[0]
            gender = (user_record.sex if user_record.sex is not None 
                    else "Unknown")
            birthyear = (str(user_record.birthyear) 
                    if user_record.birthyear is not None else '0')

        s = handle.read()

        pos = s.find(u'\n\n') + 2    # Skip first block: declaration
        nextpos = 0
        sentence_index = 0

        doc = Document()
        sentence_index_field = Field("sentence_index", str(sentence_index), YES,
            NOT_ANALYZED)
        user_field = Field("user", '', YES, NOT_ANALYZED)
        gender_field = Field("gender", '', YES, NOT_ANALYZED)
        birthyear_field = Field("birthyear", '', YES, NOT_ANALYZED)
        filename_field = Field("filename", '', YES, NOT_ANALYZED)
        contents_field = Field("contents", '', NO, ANALYZED)
        # change this to Field('compressed', '', NO)? Second argument needs to
        # be bytes, so maybe '\xfe'
        compressed_field = Field("compressed", '', YES, NOT_ANALYZED)
        doc.add(sentence_index_field)
        if metadata:
            doc.add(user_field)
            doc.add(gender_field)
            doc.add(birthyear_field)
            doc.add(filename_field)
        doc.add(contents_field)
        doc.add(compressed_field)

        while nextpos != len(s):
            nextpos = s.find(u'\n \n', pos)
            if nextpos == -1:
                nextpos = len(s)
            text = s[pos:nextpos]
            text = text.replace(u' ', u'@')
            pos = nextpos + 2

            sentence_index_field.setValue(str(sentence_index))
            if metadata:
                user_field.setValue(user_number)
                gender_field.setValue(gender)
                birthyear_field.setValue(birthyear)
                filename_field.setValue(filename)

            contents_field.setValue(text)
            # todo:
            # remove header and checksum added by zlib
            # make sure what gets stored is binary rather than unicode
            compressed = self.compressor.compress(text.encode('utf8'))
            compressed_field.setValue(compressed)
            self.writer.addDocument(doc)
            sentence_index = sentence_index + 1

command1 = u'wלאכול'
command2 = u'"lשלום lקורא"'
command3 = u'wלא'

#initVM(maxheap='512m')
#reader = IndexReader.open(SimpleFSDirectory(File(index_dir)))
#print 'Building filename cache'
#filename_cache = FieldCache.DEFAULT.getInts(reader, 'filename')
#print 'Building sentence index cache'
#sentence_index_cache = FieldCache.DEFAULT.getInts(reader, 'sentence_index')
#print 'Done'

def search(command=command1):
    searcher = IndexSearcher(reader)
    analyzer = StandardAnalyzer(Version.LUCENE_CURRENT)
    query = QueryParser(Version.LUCENE_CURRENT, "contents",
                        analyzer).parse(command)
    res = searcher.search(query, 1000000)
    print 'Total hits:', res.totalHits
#    return searcher, res
    return [searcher.doc(doc.doc) for doc in res.scoreDocs[:20]]

def build_index(where=None):
    if where is not None:
        index_dir = where
    start = datetime.now()
    #try:
    dir = '/Users/tal/corpus/analyzed'
    #dir = '/Users/tal/Dropbox/Hebrew-Blog-Corpus/experiments/t'
    analyzer = BlogCorpusAnalyzer()
    idx = IndexCorpus(index_dir, analyzer)
    idx.index(dir)
    #for i in range(4, 5):
    #    idx.index(dir + '/%d' % i)
    idx.finalize()
    end = datetime.now()
    print end - start
    #except Exception, e:
    #    print "Failed: ", e

#build_index('/Users/tal/corpus/lucene_index_compressed')
