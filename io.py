from sqlobject.main import SQLObject
from StringIO import StringIO
import codecs, os
from datetime import datetime
from db import User

class BGUWord(object):
    
    special_values = {'_': None, 't': True, 'f': False}
    string_fields = set(['word', 'base', 'lemma'])

    @classmethod
    def from_tokenfeat(cls, declaration, line):
        word = cls()
        splitted_line = line.split()
        if len(declaration) < len(splitted_line):
            raise ValueError('Declaration too short to parse line: %s' % \
                    repr(line))
        for feature, value in map(None, declaration, splitted_line):
            if feature not in cls.string_fields:
                value = cls.special_values.get(value, value)
            setattr(word, feature, value)
        # Hack because of bug:    
        word.tense, word.person = word.person, word.tense
        return word

    @classmethod
    def from_bitmask(cls, word, analysis, lemma=None):
        word = cls()
        word.word = word
        word.lemma = lemma
        word.chunking = chunking
        for feature, mask in Masks.masks.items():
            relevant_bits = analysis & mask
            value = Masks.reverse_lookups[feature].get(relevant_bits)
            setattr(word, feature, value) 
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

    def __init__(self, file, bitmask=False):
        self.bitmask = bitmask
        self.file = file
        self.index = 0
        if not bitmask:
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
            if self.bitmask:
                word, analysis, lemma = line.split()
                analysis = int(analysis)
                words.append(BGUWord.from_bitmask(word, analysis, lemma))
            else:
                word = BGUWord.from_tokenfeat(self.declaration, line)
                if word is not None:
                    words.append(word)
            line = self.file.readline().strip()
        sentence = BGUSentence(words)
        sentence.metadata['index'] = self.index
        self.index += 1
        return sentence

def BGUFile(filename):

    handle = codecs.open(filename, encoding='utf8')
    return BGUAbstractFile(handle)

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
