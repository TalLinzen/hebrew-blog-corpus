# -*- coding: utf-8 -*-
from whoosh.analysis import Filter, RegexTokenizer
from whoosh.fields import Schema, TEXT, STORED
from whoosh.query import Term
from whoosh.filedb.filestore import FileStorage

from datetime import datetime
import codecs, os

index_dir = '/Users/tal/corpus/index'

class CorpusIndex(object):

    declaration = 'word prefix base suffix lemma pos postype gender number construct polarity tense person def pconj pint pprep psub ptemp prb suftype sufgen sufnum sufperson chunk'

    def __init__(self):
        self.analyzer = (NewlineTokenizer() |
                LinguisticAnnotationFilter(self.declaration))
        self.schema = Schema(sentence_index=STORED, filename=STORED,
                text=TEXT(analyzer=self.analyzer))
        self.storage = FileStorage(index_dir)
        self.index = self.storage.create_index(self.schema)
        self.writer = self.index.writer(postlimit=256 * 1024 * 1024)

    def load_string(self, s, filename):
        pos = s.find(u'\n\n') + 2    # Skip first block: declaration
        nextpos = 0
        sentence_index = 0
        writer = self.writer

        while nextpos != len(s):
            nextpos = s.find(u'\n \n', pos)
            if nextpos == -1:
                nextpos = len(s)
            writer.add_document(filename=filename,
                    sentence_index=sentence_index, text=s[pos:nextpos])
            sentence_index = sentence_index + 1
            pos = nextpos + 2

    def load_file(self, filename):
        handle = codecs.open(filename, encoding='utf8')
        short_filename = os.path.basename(filename)
        self.load_string(handle.read(), short_filename)

    def load_dir(self, directory):
        print directory
        for filename in sorted(os.listdir(directory), key=int):
            full_filename = os.path.join(directory, filename)
            if os.path.isdir(full_filename):
                print datetime.now().ctime()
                print full_filename
                print '%s - Recursing into %s' % (datetime.now(), full_filename)
                self.load_dir(full_filename)
            elif filename[0] != '.':
                if int(filename) % 100 == 0:
                    print '   ', filename
                self.load_file(full_filename)

def NewlineTokenizer():
    return RegexTokenizer(r'\n', gaps=True)

class LinguisticAnnotationFilter(Filter):

    def __init__(self, declaration):
        self.declaration = declaration.split()

    def __call__(self, tokens):
        declaration = self.declaration
        newpos = None

        for token in tokens:
            
            if newpos is None:
                if token.positions:
                    newpos = token.pos
                else:
                    # Token doesn't have positions, just use 0
                    newpos = 0

            splitted_line = token.text.split()
            if len(declaration) < len(splitted_line):
                raise ValueError('Declaration too short to parse line: %s' % \
                        repr(token.text))

            for feature, value in map(None, declaration, splitted_line):
                # Consider adding other features in later stage
                if feature not in ('word', 'lemma', 'base'):
                    continue

                # Hack because of bug:    
                if feature == 'tense':
                    feature = 'person'
                elif feature == 'person':
                    feature = 'tense'

                token.text = '%s$%s' % (feature, value)
                token.pos = newpos
                yield token

            newpos += 1

def run():
    ix = CorpusIndex()
    #for i in range(5, 10):
    #    ix.load_dir('/Users/tal/corpus/analyzed/%d' % i)
    ix.load_dir('/Users/tal/corpus/analyzed')
    print 'Committing...'
    ix.writer.commit()
    print 'Commit done'
    print datetime.now().ctime()
    return ix

def search(index):
    searcher = index.searcher()
    s = u'lemma$אכל'
    return searcher.search(Term('text', s))

def load_index():
    storage = FileStorage(index_dir)
    return storage.open_index()
