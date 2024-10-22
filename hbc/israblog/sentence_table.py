from datetime import datetime
import bsddb3
import codecs
import os

from hbc.db import Sentence

bsddb = bsddb3.hashopen('/Users/tal/corpus/bsddb/bsd.db')

def process_dir(directory):
    files = [x for x in os.listdir(directory) if x.isdigit()]
    for filename in sorted(files, key=int):
        path = os.path.join(directory, filename)
        if not filename.isdigit():
            continue
        if os.path.isdir(path):
            process_dir(path)
        else:
            if int(filename) % 100 == 0:
                print datetime.now().ctime(), filename
            process_file(path)

def process_file(path):
    filename = os.path.basename(path)
    handle = codecs.open(path, encoding='utf8')
    s = handle.read()
    pos = s.find(u'\n\n') + 2    # Skip first block: declaration
    nextpos = 0
    sentence_index = 0

    while nextpos != len(s):
        nextpos = s.find(u'\n \n', pos)
        if nextpos == -1:
            nextpos = len(s)
        text = s[pos:nextpos].strip().encode('utf8')
        pos = nextpos + 2

        if text != '':
            # Use mysql table:
            # Sentence(webpage_id=int(filename), sentence_id=sentence_index,
            #        data=text)

            # Use bsddb:
            bsddb['%s_%s' % (int(filename), sentence_index)] = text

        sentence_index += 1

def build_sentence_table():
    process_dir(os.environ['HBC_PATH'])
