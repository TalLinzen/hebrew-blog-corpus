try:
    from pyExcelerator import *
except ImportError:
    pass

import os

from transliterator import Transliterator

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
