# -*- coding: utf-8 -*-
import codecs, lucene
from common import BlogCorpusAnalyzer, BlogCorpusFilter
from static_lz import trained_short_string_compressor

# test search strings
command1 = u'wלאכול'
command2 = u'"lשלום lקורא"'
command3 = u'wלא'

class CorpusSearch(object):

    def __init__(self, index_dir, compressed=False, training_file=None):
        env = lucene.getVMEnv()
        if env is None:
            lucene.initVM(maxheap='512m')
        else:
            env.attachCurrentThread()

        self.index_dir = index_dir
        self.training_file = training_file
        directory = lucene.SimpleFSDirectory(lucene.File(self.index_dir))
        self.reader = lucene.IndexReader.open(directory)
        self.compressor = self.get_compressor() if compressed else None
        self.searcher = lucene.IndexSearcher(self.reader)
        version = lucene.Version.LUCENE_CURRENT
        self.analyzer = lucene.StandardAnalyzer(version)
        self.parser = lucene.QueryParser(version, 'contents', self.analyzer)

    def get_compressor(self):
        training_data = codecs.open(self.training_file, encoding='utf8').read()
        as_utf8 = training_data.encode('utf8')
        return trained_short_string_compressor(as_utf8)

    def search(self, command):
        query = self.parser.parse(command)
        results = self.searcher.search(query, 1000000)
        return SearchResults(results, self.searcher, self.compressor, query)

class Result(object):

    clip_by = 6
    def __init__(self, words, start, end):
        self.before = ' '.join(words[:start] if start > 0 else [])
        clipped_start = max(start - self.clip_by, 0)
        clipped_end = min(end + self.clip_by, len(words))
        self.clipped_before = ' '.join(words[clipped_start:start] if 
                start > 0 else [])
        self.clipped_after = ' '.join(words[end+1:clipped_end])
        if clipped_end != len(words):
            self.clipped_after += '...'
        if clipped_start != 0:
            self.clipped_before = '...' + self.clipped_before
        self.highlighted = ' '.join(words[start:end+1])
        self.after = ' '.join(words[end+1:])

class SearchResults(object):

    def __init__(self, lucene_results, searcher, compressor, query):
        self.lucene_results = lucene_results
        self.searcher = searcher
        self.compressor = compressor
        scorer = lucene.QueryScorer(query)
        self.highlighter = lucene.Highlighter(scorer)
        self.analyzer = BlogCorpusAnalyzer()
        fragmenter = lucene.SimpleFragmenter(10000)
        self.highlighter.setTextFragmenter(fragmenter)
        self.nhits = self.lucene_results.totalHits

    def __len__(self):
        return self.nhits

    def uncompress_contents(self, doc):
        unicode_str = doc.getField('compressed').stringValue()
        # hack, because not indexed as a binary field. fix that
        normal_str = ''.join(chr(ord(x)) for x in unicode_str)
        return self.compressor.decompress(normal_str)

    def get_doc(self, number):

        scoredoc = self.lucene_results.scoreDocs[number]
        doc = self.searcher.doc(scoredoc.doc)
        if self.compressor is not None:
            contents = self.uncompress_contents(doc)
        else:
            contents = doc.getField('contents').stringValue()

        tokenStream = self.analyzer.tokenStream('f', 
                lucene.StringReader(contents))
        highlighted = self.highlighter.getBestFragment(tokenStream, contents)

        words = highlighted.split()
        actual_words = []
        highlighted_words = []
        for index, word in enumerate(words):
            splitted = word.split('@')
            wordform = (splitted[0] if splitted[0] != '' and 
                    splitted[0] != '<B>' else splitted[1])
            if word.startswith('<B>'):
                highlighted_words.append(index)
            actual_words.append(wordform.replace('<B>', ''))

        # Take only first continguous strech of highlighted words
        for i in range(0, len(highlighted_words) - 1):
            if highlighted_words[i+1] - highlighted_words[i] > 1:
                highlighted_words = highlighted_words[:i+1]
                break

        start = highlighted_words[0]
        end = highlighted_words[-1]
        assert len(highlighted_words) == end - start + 1 # Make sure highlighted words are contiguous
        return Result(actual_words, start, end)

    def __getitem__(self, item):

        if isinstance(item, slice):
            return [self.get_doc(self.nhits - i - 1) 
                    for i in range(item.start, item.stop)]
        else:
            return self.get_doc(item)

