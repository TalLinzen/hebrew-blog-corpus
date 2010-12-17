# -*- coding: utf-8 -*-
import codecs, lucene
from static_lz import trained_short_string_compressor

# test search strings
command1 = u'wלאכול'
command2 = u'"lשלום lקורא"'
command3 = u'wלא'

class CorpusSearch(object):

    index_dir = '/home/tallinzen/webapps/django/frames/lucene_index'
    training_file = '/home/tallinzen/webapps/django/frames/lucene_index/5344'

    def __init__(self):
        lucene.initVM(maxheap='512m')
        directory = lucene.SimpleFSDirectory(lucene.File(self.index_dir))
        self.reader = lucene.IndexReader.open(directory)
        self.compressor = self.get_compressor()
        self.searcher = lucene.IndexSearcher(self.reader)
        version = lucene.Version.LUCENE_CURRENT
        self.analyzer = lucene.StandardAnalyzer(version)
        self.parser = lucene.QueryParser(version, 'contents', self.analyzer)

    def get_compressor(self):
        training_data = codecs.open(self.training_file, encoding='utf8').read()
        as_utf8 = training_data.encode('utf8')
        self.compressor = trained_short_string_compressor(as_utf8)

    def search(command):
        query = self.parser.parse(command)
        results = self.searcher.search(query, 1000000)
        return SearchResults(results)


class SearchResults(object):

    def __init__(self, lucene_results):
        self.lucene_results = lucene_results

    def total_hits(self):
        return self.lucene_results.totalHits

    def uncompress_contents(doc):
        unicode_str = doc.getField('compressed').stringValue()
        # hack, because not indexed as a binary field. fix that
        normal_str = ''.join(chr(ord(x)) for x in unicode_str)
        return self.compressor.decompress(normal_str)

    def get(self, start, end):
        ret = []
        for doc in results.scoreDocs:
            ret.append(self.uncompress_contents(searcher.doc(doc.doc)))
        return ret

