from sqlobject.main import SQLObject
from StringIO import StringIO
import codecs, os
from datetime import datetime

class Masks(object):

    pos = {
        'adjective':         0X0000000000010000,
        'adverb':            0X0000000000020000,
        'conjunction':       0X0000000000030000,
        'at_prep':           0X0000000000040000, # not in mila
        'negation':          0X0000000000050000,
        'noun':              0X0000000000060000,
        'numeral':           0X0000000000070000,
        'preposition':       0X00000000000080000,
        'pronoun':           0X0000000000090000,
        'propername':        0X00000000000A0000,
        'particle':          0X00000000000B0000, # not used
        #'auxverb':           0X00000000000C0000, # not used
        'verb':              0X00000000000D0000,
        'punctuation':       0X00000000000E0000,
        'interrogative':     0X00000000000F0000,
        'interjection':      0X0000000000100000,
        'unknown':           0X0000000000110000,
        'quantifier':        0X0000000000120000,
        'existential':       0X0000000000130000,
        'modal':             0X0000000000140000,
        'prefix':            0X0000000000150000,
        'url':               0X0000000000160000,
        'foreign':           0X0000000000170000,
        'junk':              0X0000000000180000,
        #'impersonal':        0X0000000000190000, # not used
        'participle':        0X00000000001A0000,
        'copula':            0X00000000001B0000,
        'numexp':            0X00000000001C0000,
        'titula':            0X00000000001D0000,
        'shel_prep':         0X00000000001E0000, # not in mila
    }

    gender = {
        'm':  0X0000000000200000,
        'f':0X0000000000400000,
        'mf':0X0000000000600000,
    }

    number = {
        's':0X0000000001000000,
        'p':0X0000000002000000,
        'd':0X0000000003000000,
        'dp':0X0000000004000000,
        'sp':0X0000000005000000,
    }

    person = {
        '1':0X0000000008000000,
        '2':0X0000000010000000,
        '3':0X0000000018000000,
        'a':0X0000000020000000,
    }

    status = {
        'abs':0X0000000040000000,
        'const':0X0000000080000000,
    }

    tense = {
        'past':0X0000000200000000,
        'alltime': 0X0000000400000000,  # @new
        'beinoni':0X0000000600000000,
        'future':0X0000000800000000,
        'imperative':0X0000000A00000000,
        'toinfinitive':0X0000000C00000000,
        'bareinfinitive':0X0000000E00000000,
    }

    polarity = {
        'positive':0X0002000000000000,
        'negative':0X0004000000000000,
    }

    binyan = {
        'paal'    :0X0008000000000000,
        'nifal'   :0X0010000000000000,
        'hifil'   :0X0018000000000000,
        'hufal'   :0X0020000000000000,
        'piel'    :0X0028000000000000,
        'pual'    :0X0030000000000000,
        'hitpael' :0X0038000000000000,
    }

    conj_type = {
        'coord': 0X0040000000000000,
        'sub':   0X0080000000000000,
        'rel':   0X00C0000000000000
    }

    pron_type = {
        'pers': 0X0100000000000000, # personal
        'dem':  0X0200000000000000, # demonstrative
        'imp':  0X0300000000000000, # impersonal
        'ref':  0X0400000000000000, # reflexive @@@@
        #'int':  0X0300000000000000, # interogative
        #'rel':  0X0400000000000000, # reletivizer
    }

    num_type = {
        'ordinal' : 0X1000,
        'cardinal': 0X2000,
        'fractional': 0X3000,
        'literal': 0X4000,
        'gimatria': 0X5000,
    }

    interrogative_type = {
        'pronoun' : 0X20,
        'proadverb' : 0X0000004000000000,
        'prodet'    : 0X0000004000000020,
        'yesno'     : 0X0001000000000000,
    }

    quantifier_type = {
        'amount'    : 0X0000000000800000,
        'partitive' : 0X0000000100000000,
        'determiner': 0X0000000100800000,
    }

    suff_func = {
        'possesive':0X0000001000000000,
        'acc-nom':0X0000002000000000,    # tHIS IS THE NOMINATIVE
        'pronomial':0X0000003000000000,  # FOR adverbs AND preps
    }

    suff_gen = {
        'm':0X0000008000000000,
        'f':0X0000010000000000,
        'mf':0X0000018000000000,
    }

    suff_num = {
          's':0X0000040000000000,
          'p':0X0000080000000000,
          'd':0X00000C0000000000,
          'dp':0X0000100000000000,
          'sp':0X0000140000000000,
          }

    suff_pers = {
        '1':0X0000200000000000,
        '2':0X0000400000000000,
        '3':0X0000600000000000,
        'a':0X0000800000000000,
    }

    prefix = {
        'conj':0X0000000000000002, 
        'def':0X0000000000000004,  # USED AS A FEATURE..
        'interrogative':0X0000000000000010,
        'preposition':0X0000000000000040,
        'rel-subconj':0X00000000000000100,
        'temp-subconj':0X00000000000000200,
        'tenseinv':0X0000000000000020,
        'adverb':0X00000000000000400,
        'preposition2':0X0000000000000080, #??
    }

    masks = {
        'prefix':     0X756, # ^ 0X4,           # 0X756 ^ def
        'pos':        0X1f0000,           # BITS 17-21
        'gender':     0X0000000000600000, # BITS 22-23
        'number':     0X7000000,          # BITS 25-27
        'person':     0X38000000,         # BITS 28-30
        'status':     0X00000000C0000000, # BITS 31-32
        'tense':      0Xe00000000,        # BITS 34-36
        'suff_func':  0X0000003000000000, # BITS 37-38
        'suff_gen':   0X0000018000000000, # BITS 40-41

        'suff_num':   0X1C0000000000,     # BITS 43-45
        'suff_pers':  0Xe00000000000,     # BITS 46-48
        #'cont':       0X1000000000000,    # BITS 49   (What is this? - Tal)
        'polarity':   0X6000000000000,    # BITS 50-51
        'binyan':     0X0038000000000000, # BITS 52-54 BASE FORM binyan
        'conj_type':  0X00C0000000000000, # BITS 55-56 BASE FORM CONJUNCTION TYPE
        'pron_type':  0X0700000000000000, # BITS 57-59 BASE FORM PRONOUN TYPE
        'num_type':   0X0000000000007000, # BITS 13-15 @new

        'interrogative_type' : 0X0001004000000020, # BITS 6,39,49 @new
        'quantifier_type'   : 0X0000000100800000, # BITS 24,33 @new
    }

    @classmethod
    def create_reverse_lookups(cls):
        cls.reverse_lookups = {}
        for field in cls.masks.keys():
            cls.reverse_lookups[field] = dict((y, x) for x, y in \
                    getattr(cls, field).items())

Masks.create_reverse_lookups()


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

    def __init__(self, words):
        self.words = words
        self.metadata = {}

    def pprint(self, reverse=False):
        if reverse:
            reversed_words = []
            for word in self.words:
                if word.word:
                    reversed_words.append(''.join(reversed(word.word)))
            if reversed_words:
                print ' '.join(reversed(reversed_words)).encode('utf8')
            else:
                print
        else:
            if self.words:
                print ' '.join(w.word for w in self.words).encode('utf8')
            else:
                print

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
            yield sentence
