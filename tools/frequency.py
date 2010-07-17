import codecs, os, shelve
from datetime import datetime
import xlwt
from .conf import analyzed_corpus_dir, data_dir

def freq_txt_to_xls(filename):

    shelf = shelve.open(os.path.join(data_dir, 'word_frequency.db'))
    handle = codecs.open(filename, encoding='cp1255')
    values = [x.strip() for x in handle.readlines()]
    base = os.path.splitext(filename)[0]
    out_filename = base + '.xls'
    wb = xlwt.Workbook()
    sheet = wb.add_sheet('Count')
    for row, value in enumerate(values):
        sheet.write(row, 0, value)
        sheet.write(row, 1, shelf.get(value.encode('utf8'), 0))
    wb.save(out_filename)

def fast_frequency_index():
    
    words = {}
    lemmas = {}

    for subdir in sorted(os.listdir(analyzed_corpus_dir), key=int):
        print datetime.now().ctime(), subdir
        subdir_full = os.path.join(analyzed_corpus_dir, subdir)
        for f in os.listdir(subdir_full):
            handle = open(os.path.join(subdir_full, f))
            handle.readline()
            for line in handle.readlines():
                line = line.strip()
                if line != '':
                    word, prefix, base, suffix, lemma, rest = line.split(' ', 5)
                    words[word] = words.get(word, 0) + 1
                    lemmas[lemma] = lemmas.get(lemma, 0) + 1
                    #r.incr('w|' + word)
                    #r.incr('l|' + lemma)

    print datetime.now().ctime(), "Dumping word frequency shelf"
    words_shelf = shelve.open(os.path.join(data_dir, 'word_frequency'))
    words_shelf.update(words)
    print datetime.now().ctime(), "Dumping lemma frequency shelf"
    lemmas_shelf = shelve.open(os.path.join(data_dir, 'lemma_frequency'))
