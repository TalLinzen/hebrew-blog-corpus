# b = BGUTagger('0.hr', FromNumberedSet, {'numbers': create_set('ht0_pd_at')})
# b.load_file()

try:
    from pyExcelerator import *
except ImportError:
    pass

import os

from transliterator import Transliterator
from parse_hspell import parse_hspell

class SentenceGroup(object):
    def __init__(self):
        self.sentences = []

class Sentence(object):

    attributes_for_pickle = ['index', 'hebrew_repr', 'relevant_verb_indices']

    def __init__(self, index):
        self.index = index
        self.words = []
        self.relevant_verb_indices = []
        self.count_all_verbs = True
        self.good_sentence = False
        self.hebrew_repr = ''
        self.selecting_l = False
        self.last_verb_pos = 0

    def feed_word(self, index, word):
        self.words.append(word)

    def post_process(self):
        pass

    def __getstate__(self):
        return dict((attr, getattr(self, attr)) for attr in self.attributes_for_pickle)

    def to_string(self, highlight_index=None):
        ttt = []
        for i, w in enumerate(self.words):
            trans = Transliterator().reverse_translate(w[0])
            if trans != '' and w[0][-1] in 'kmnpc':
                trans = trans[:-1] + chr(ord(trans[-1]) - 1)
            if i == highlight_index:
                trans = '$$$' + trans
            ttt.append(trans)
        return ' '.join(ttt).decode('iso8859-8', 'replace').encode('utf8', 'replace')

    def check_if_verb(self, index, word, specific_root=False):

        lemma, analysis, named_entity, np_chunk = word
        if analysis[1][:2] in ('VB', 'MD'):
            if analysis[0] in ('REL-SUBCONJ', 'CONJ'):
                verb_form = lemma[1:]
            elif analysis[0] == 'TMP-SUBCONJ':
                verb_form = lemma[2:]
            else:
                verb_form = lemma
            return verb_form
        else:
            return None

class AcceptAll(Sentence):

    def feed_word(self, index, word):
        Sentence.feed_word(self, index, word)
        self.good_sentence = True

class TenseCounter(Sentence):

    interesting_verbs = set([
        ('qrh', 'kara', 'happen'), 
        ('ASh', 'asa', 'do'), 
        ('bkh', 'baxa', 'cry'),
        ('npl', 'nafal', 'fall'),
        ('akl', 'axal', 'eat'),
        ('xSb', r'xa\v{s}av', 'think'),
        ('rch', 'raca', 'want'),
        ('hrs', 'haras', 'destroy'),
        ('Sbr', r'\v{s}avar', 'break'),
        ('nicx', 'niceax', 'win'),
        ('ahb', 'ahav', 'love'),
        ('mca', 'maca', 'find'),
        ('xipS', 'xipes', 'look for'),
        ('hlk', 'halax', 'walk'),
        ('iSb', r'ya\v{s}av', 'sit'),
        ('hgiA', 'higia', 'arrive'),
        ('Sth', r'\v{s}ata', 'drink'),
        ('ird', 'yarad', 'go down'),
        ('gmr', 'gamar', 'finish'),
        ('ntn', 'natan', 'give'),
        ('qpc', 'kafac', 'jump'),
        ('hkin', 'hexin', 'make'),
        ('hbia', 'hevi', 'bring')])

    count = {}

    def feed_word(self, index, word):

        lemma, analysis, named_entity, np_chunk = word
        if analysis[1][:2] in ('VB', 'BN'):
            for verb in self.interesting_verbs:
                if lemma in self.conjugations[verb[0]]:
                    subanalysis = analysis[1].split('-')
                    d = self.count.setdefault(verb, {})
                    try:
                        d[subanalysis[-1]] += 1
                    except KeyError:
                        d[subanalysis[-1]] = 1
                    

def count_lemmas(lemmas):

    class LemmaCounter(Sentence):

        count = dict((lemma, 0) for lemma in lemmas)
        total_count = 0

        def feed_word(self, index, word):
            self.__class__.total_count += 1
            lemma, analysis, base_form, named_entity, np_chunk = word
            if lemma in self.count:
                self.count[lemma] += 1

    b = BGUTagger('', LemmaCounter, with_roots=True)
    b.load_all_files()
    #b.load_file()
    return (LemmaCounter.count, LemmaCounter.total_count)

def count_lemmas_from_file(filename):
        
    t = Transliterator()
    words = [t.translate(x) for x in open(filename).read().split('\r\n')]
    count, total_count = count_lemmas(words)
    print total_count
    wc = open('word_count.txt', 'w')
    for key, value in sorted(count.items()):
        wc.write('%s %s %s\n' % (key, t.reverse_translate(key), value))
    wc.close()

class FromNumberedSet(Sentence):

    def __init__(self, index, numbers):
        Sentence.__init__(self, index)
        if index in numbers:
            self.good_sentence = True

    def feed_word(self, index, word):
        Sentence.feed_word(self, index, word)
        self.check_if_verb(index, word)
            
def create_set(filename, directory=annotations):
    lines = open(os.path.join(directory, filename)).readlines()
    numbers = [int(x.split(':')[0]) for x in lines if x]
    return numbers


class GeneralPossessive(Sentence):

    def feed_word(self, index, word):
        
        Sentence.feed_word(self, index, word)
        lemma, analysis, named_entity, np_chunk = word
        self.check_if_verb(index, word)

        if analysis[1] == 'POS':
            self.good_sentence = True
            self.relevant_verb_indices.append(self.last_verb_pos)

class PossessiveSentence(Sentence):

    def __init__(self, index):
        Sentence.__init__(self, index)
        self.at_started = False
        self.at_pos = 0
        self.relevant_shel = []
        self.relevant_et = []

    def feed_word(self, index, word):

        Sentence.feed_word(self, index, word)
        lemma, analysis, named_entity, np_chunk = word

        self.check_if_verb(index, word)

        if analysis[1] == 'AT' and self.last_verb_pos >= index - 2:
            self.relevant_et.append(index)
            self.at_started = True
            self.at_pos = index

        elif self.at_started:
            if analysis[1] == 'POS' and self.at_pos >= index - 2:
                self.good_sentence = True
                self.relevant_verb_indices.append(self.last_verb_pos)
                self.relevant_shel.append(index)
            elif np_chunk != 'I-NP':
                self.at_started = False


class PossessiveDativeSentence(Sentence):

    def __init__(self, index):
        Sentence.__init__(self, index)
        self.lamed_phrase_pos = []
        self.verb_indices = []

    def feed_word(self, index, word):

        Sentence.feed_word(self, index, word)
        lemma, analysis, named_entity, np_chunk = word

        prep_with_pronoun = analysis[1] == 'IN' and analysis[2] != ''
        prep_with_noun = analysis[0] == 'PREPOSITION'

        if len(lemma) > 0 and lemma[0] == 'l' and lemma not in self.infinitives \
                and (prep_with_pronoun or prep_with_noun):
            self.lamed_phrase_pos.append(index)
           
        if self.check_if_verb(index, word):
            self.verb_indices.append(index)

    def post_process(self):
        self.relevant_verb_indices = []
        for verb_index in self.verb_indices:
            if set(range(verb_index - 2, verb_index + 3)).intersection(set(self.lamed_phrase_pos)):
                self.relevant_verb_indices.append(verb_index)
        self.good_sentence = self.relevant_verb_indices != []

class BGUTagger(object):

    d = '/Users/tal/University/PD/israblog_disambiguated/'

    def __init__(self, f, filter_class, filter_class_kwargs = None, with_roots = False):
        self.f = f
        self.with_roots = with_roots
        self.filter_class = filter_class
        self.make_verbs_selecting_l_list()
        self.t = Transliterator()
        self.sentence_group = SentenceGroup()
        self.sentence_group.filename = f
        self.sentence_counter = 0
            
        self.filter_class_kwargs = filter_class_kwargs or {}

    def make_verbs_selecting_l_list(self):
      
        self.infinitives, self.conjugations = parse_hspell()
        roots_selecting_l = ['ntn', 'hih', 'hrah', 'hsbir', 'gilh', 'qrh', 'ba', 'amr', 'trm', 'hciA', 'hpnh', 'nAnh', 'htrgl', 'xikh', 'qnh', 'htgiis', 'hrSh', 'hAbir', 'xdr', 'hrSh', 'sipr', 'Azr', 'hgid', 'hxzir', 'biSr', 'xsr', 'nmas', 'hamin', 'hpriA', 'Anh', 'nwtr', 'hwdiA', 'dag', 'grm', 'hbTix', 'hzkir', 'ndmh', 'nrah',
                             'msr', 'sirb']
        roots_selecting_l += ['hgiA', 'lqx', 'ica', 'ASh', 'Slx', 'hbia', 'hAniq', 'hbhir', 'hmxiS']
        boomba = reduce(lambda x, y: x + y, [self.conjugations[r] for r in roots_selecting_l]) + ['ain', 'iS', 'kdai', 'nxwc']
        self.verbs_selecting_l = boomba


    def load_all_files(self):
        if self.with_roots:
            files = ['60000.hr_roots', '80000.hr_roots', '100000.hr_roots', '120000.hr_roots']
        else:
            files = ['0.hr', '20000.hr', '40000.hr', '60000.hr', '80000.hr', '100000.hr', '120000.hr']

        for f in files:
            print f
            self.f = f
            self.load_file()

        self.f = 'all'

    def load_file(self, limit=None, only_set=None):
        file_contents = open(self.d + self.f).read()
        self.limit = limit

        if file_contents[0] == ' ':
            file_sentences = file_contents[4:].split('\n   \n')
        else:
            file_sentences = file_contents.split('\n\n')

        if only_set is None:
            self.load_sentences(file_sentences)
        else:
            self.load_sentences([file_sentences[x] for x in sorted(only_set)])


    def load_sentences(self, sentences):
        for sentence_index, sentence in enumerate(sentences):

            self.sentence_counter += 1
            if sentence_index == self.limit:
                return

            if sentence_index % 10000 == 0:
                print sentence_index

            this_sentence = self.filter_class(sentence_index, **self.filter_class_kwargs)
            this_sentence.verbs_selecting_l = self.verbs_selecting_l
            this_sentence.conjugations = self.conjugations
            this_sentence.infinitives = self.infinitives

            words = sentence.split('\n')

            for index, word in enumerate(words):
                if len(word) == 0:
                    continue

                if self.with_roots:
                    lemma, analysis, base_form, named_entity, np_chunk = word.split()
                else:
                    lemma, analysis, named_entity, np_chunk = word.split()

                lemma = self.t.translate(lemma.decode('utf_8').encode('cp1255'))
                analysis = analysis.split(':')

                if self.with_roots:
                    base_form = self.t.translate(base_form.decode('utf_8').encode('cp1255'))
                    this_sentence.feed_word(index, (lemma, analysis, base_form, named_entity, np_chunk)) 
                else:
                    this_sentence.feed_word(index, (lemma, analysis, named_entity, np_chunk))

            this_sentence.post_process()

            if this_sentence.good_sentence:
                self.sentence_group.sentences.append(this_sentence)


    def write_to_file(self,  start=0, end=-1, title='DefaultTitle'):

        f = open('/tmp/for_annotation', 'w')
        self.sentence_group.title = title
        self.sentence_group.sentences = self.sentence_group.sentences[start:end]
        for sentence in self.sentence_group.sentences:
            ttt = []
            for w in sentence.words:
                trans = self.t.reverse_translate(w[0])
                if trans != '' and w[0][-1] in 'kmnpc':
                    trans = trans[:-1] + chr(ord(trans[-1]) - 1)
                ttt.append(trans)
            sentence.hebrew_repr = ' '.join(ttt) + '\n'
        cPickle.dump(self.sentence_group, f)

def write_to_file2(sentences, filename='annotation.xls'):

    t = Transliterator()

    def translate(words):
        ttt = []
        for w in words:
            trans = t.reverse_translate(w[0])
            if trans != '' and w[0][-1] in 'kmnpc':
                trans = trans[:-1] + chr(ord(trans[-1]) - 1)
            ttt.append(trans)
        joined = ' '.join(ttt)
        return joined

    w = Workbook()
    UnicodeUtils.DEFAULT_ENCODING = 'cp1255'
    ws = w.add_sheet('Annotation')
    ws.col(1).width = 0x3000
    ws.col(3).width = 0x3000
    style = XFStyle()
    right = Alignment()
    right.horz = Alignment.HORZ_RIGHT
    right.direction = Alignment.DIRECTION_RL
    left = Alignment()
    left.horz = Alignment.HORZ_LEFT
    left.direction = Alignment.DIRECTION_RL
    center = Alignment()
    center.horz = Alignment.HORZ_CENTER
    center.direction = Alignment.DIRECTION_RL

    for i, sentence in enumerate(sentences):
        try:
            index = sentence.relevant_verb_indices[0]
        except IndexError:
            index = 0
        window = 3
        left_end = max(0, index-window)
        # after verb
        style.alignment = right
        ws.write(i, 1, translate(sentence.words[index+window:])[:45], style)
        # verb
        style.alignment = center
        ws.write(i, 2, translate(sentence.words[left_end:index+window]), style)
        # before verb
        style.alignment = left
        ws.write(i, 3, translate(sentence.words[:left_end])[-45:], style)
        # whole sentence
        style.alignment = right
        ws.write(i, 4, translate(sentence.words), style)
        # sentence index
        ws.write(i, 5, str(sentence.index))

    w.save(filename)

def count_to_latex(count):

    s = []
    for key in sorted(count.keys()):
        d = count[key]
        past, beinoni, future = [d.get(x, 0) for x in ('PAST', 'A', 'FUTURE')]
        s.append(r"\textsl{%s} `%s' & %d & %d & %d & %.1f\%% & %.1f\%%\\" % (key[1], key[2], past, beinoni, future, 100 * float(beinoni) / (beinoni + past), 100 * float(beinoni) / (beinoni + past + future)))
    return '\n'.join(s)


def word_after_verb(bgutagger):
    return [s.words[s.relevant_verb_indices[0]+1][0] for s in bgutagger.sentence_group.sentences]

def possessive_shel(bgutagger):
    ret = []
    for s in bgutagger.sentence_group.sentences:
        if s.words[s.relevant_shel[0]][0] == 'Sl':
            ret.append(s.words[s.relevant_shel[0]+1][0])
        else:
            ret.append(s.words[s.relevant_shel[0]][0])
    return ret

def possessive_et(bgutagger):
    return [s.words[s.relevant_et[0]+1][0] for s in bgutagger.sentence_group.sentences]

l_pronouns = ['li', 'lk', 'lw', 'lh', 'lnw', 'lhm', 'lhn', 'lkn', 'lkm']
shel_pronouns = ['S' + x for x in l_pronouns]

def count_body_parts(l):
    from tools import mifkad
    bp = ['id', 'idiim', 'rgl', 'rgliim', 'raS', 'Ain', 'Ainiim', 'awzn', 'awzniim', 'bTn', 'acbA', 'acbAwt', 'lb', 'mwx', 'gwp', 'pnim', 'siAr', 'siArwt']
    #bp += ['tht', 'zin', 'cicim', 'xzh', 'Sdiim']
    bp = set(bp + ['h' + q for q in bp])
    bp_count = 0
    for key, value in mifkad(l).items():
        if key in bp:
            bp_count += value
    return bp_count 
