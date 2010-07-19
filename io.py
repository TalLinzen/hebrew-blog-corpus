# -*- coding: utf-8 -*-
from sqlobject.main import SQLObject
from StringIO import StringIO
import codecs, os
from datetime import datetime
from db import User

declaration = 'word prefix base suffix lemma pos postype gender number construct polarity tense person def pconj pint pprep psub ptemp prb suftype sufgen sufnum sufperson chunk'.split()

class BGUWord(object):
    
    special_values = {'_': None, 't': True, 'f': False}
    string_fields = set(['word', 'base', 'lemma'])

    @classmethod
    def from_tokenfeat(cls, declaration, line, sep=' '):
        word = cls()
        splitted_line = line.split(sep)
        if len(declaration) < len(splitted_line):
            raise ValueError('Declaration too short to parse line: %s' % \
                    repr(line))
        for feature, value in map(None, declaration, splitted_line):
            if feature != 'word' and feature != 'base' and feature != 'lemma':
                if value == '_':
                    value = None
                elif value == 't':
                    value = True
                elif value == 'f':
                    value = False
            setattr(word, feature, value)
        # Hack because of bug:    
        word.tense, word.person = word.person, word.tense
        return word

    def __repr__(self):
        return "<word='%s' pos='%s' prefix='%s' lemma='%s' base='%s' chunk='%s'>" % \
                tuple([x.encode('utf8') if x is not None else '' for x in \
                (self.word, self.pos, self.prefix, self.lemma,
                    self.base, self.chunk)])

class BGUSentence(object):

    def __init__(self, rich_words=None):
        self.metadata = {}
        if rich_words is not None:
            self.rich_words = rich_words
            self.words = [word.word for word in self.rich_words]

    def reduce_memory_footprint(self):
        del self.rich_words

    def clone(self):
        cloned = self.__class__(rich_words=None)
        cloned.rich_words = self.rich_words
        cloned.words = self.words
        cloned.metadata.update(self.metadata)
        return cloned

    def pprint(self, reverse=False):
        if reverse:
            reversed_words = []
            for word in self.words:
                reversed_words.append(''.join(reversed(word)))
            print ' '.join(reversed(reversed_words)).encode('utf8')
        else:
            print ' '.join(self.words).encode('utf8')


class BGUAbstractFile(object):

    def __init__(self, file, sentence_indexes=None):
        '''
        If sentence_indexes is specified, yield only the sentences with this
        index; e.g. [0, 1, 3] will yield the first, second and fourth sentences
        of the file
        '''
        self.file = file
        self.index = 0
        self.declaration = self.file.readline().split()
        self.file.readline()   # Empty line

    def __iter__(self):
        return self

    def next(self):
        words = []
        line = self.file.readline()
        if line == '':
            raise StopIteration
        line = line.strip()
        while line != '':
            word = BGUWord.from_tokenfeat(self.declaration, line)
            if word is not None:
                words.append(word)
            line = self.file.readline().strip()
        sentence = BGUSentence(words)
        sentence.metadata['index'] = self.index
        self.index += 1
        return sentence

def BGUFile(filename, *args):

    handle = codecs.open(filename, encoding='utf8')
    return BGUAbstractFile(handle, *args)

def BGUString(string):

    if string is None or len(string) == 0:
        return []
    if string[-1] == '\xd7':
        string = string[:-1]
    return BGUAbstractFile(StringIO(string.decode('utf8')))


def BGUDir(directory):

    for filename in sorted(os.listdir(directory), key=int):
        full_filename = os.path.join(directory, filename)

        generator = None
        if os.path.isdir(full_filename):
            print '%s - Recursing into %s' % (datetime.now(), full_filename)
            generator = BGUDir(full_filename)
        elif filename[0] != '.':
            generator = BGUFile(full_filename)

        if generator:
            for sentence in generator:
                sentence.metadata.setdefault('filename', []).append(filename)
                yield sentence

def BGUQuery(sqlobject_query):

    if isinstance(sqlobject_query, SQLObject):
        sqlobject_query = [sqlobject_query]

    for result in sqlobject_query:
        for sentence in BGUString(result.analyzed):
            sentence.metadata['webpage_id'] = result.id
            sentence.metadata['user'] = result.user
            user = User.byNumber(result.user)
            sentence.metadata['age'] = user.age
            sentence.metadata['sex'] = user.sex
            yield sentence

def BGUQueries(sqlobject_queries, limit=None, distribute=False):
    '''
    limit: If set, stop after this number of sentences
    distribute: If True, take an equal number of sentences from
        each query (if available). Only meaningful in conjunction with limit
    '''
    global_sentence_index = 0
    n_queries = len(sqlobject_queries)
    if limit and distribute:
        query_limit = limit / n_queries
    for query_index, query in enumerate(sqlobject_queries):
        print '%d out of %d' % (query_index, n_queries)
        for sentence_index, sentence in enumerate(BGUQuery(query)):
            yield sentence
            if limit and global_sentence_index == limit - 1:
                return
            if limit and distribute and sentence_index == query_limit - 1:
                break
            global_sentence_index += 1

def BGULuceneSearch(query_string):
    '''
    E.g. BGULuceneSearch('wאבוקדו'))
    '''
    from lucene_index import search
    from conf import lucene_index_dir

    searcher, results = search(command=query_string, d=lucene_index_dir)
    for result in results.scoreDocs:
        doc = searcher.doc(result.doc)
        contents = doc.getField('contents').stringValue()
        words = []
        for line in contents.split('\n'):
            word = BGUWord.from_tokenfeat(declaration, line)
            if word is not None:
                words.append(word)
        yield BGUSentence(words)
