from datetime import datetime
import json
import os
import re

from xlwt import XFStyle, Alignment, UnicodeUtils, Workbook

from hbc.conf import annotation_dir
from hbc.io import BGUSentence
from hbc.tools import excel_alignments

UnicodeUtils.DEFAULT_ENCODING = 'utf8'

def read_sentence_file(filename):
    sentences = []
    for sentence in json.load(open(filename)):
        obj = BGUSentence()
        obj.__dict__.update(sentence)
        sentences.append(obj)
    return sentences

def write_sentence_file(sentences, filename):
    if json is None:
        return
    f = open(filename, 'w')
    json.dump([obj.__dict__ for obj in sentences], f)

def update_annotation_directory(dirname):
    '''
    Load manual annotations from Excel files and update the JSON file
    '''
    sentence_file_name = os.path.join(dirname, 'sentences.json')
    sentences = read_sentence_file(sentence_file_name)

    for file in os.listdir(dirname):
        if file.endswith('.xls'):
            filename = os.path.join(dirname, file)
            # FIXME: xlwt doesn't have parse_xls
            parsed = parse_xls(filename, 'utf8')
            for sheet_name, values in parsed:
                max_row = max(x[0] for x in values.keys())
                for row in range(0, max_row + 1):
                    annotation = values.get((row, 0), '')
                    id = values[(row, 5)]
                    sentences[id].annotation = annotation

    write_sentence_file(sentences, sentence_file_name)


class Annotation(object):

    def __init__(self, description, sentences=None, custom_fields=None):
        self.workbooks = {}
        self.description = description
        self.custom_fields = custom_fields
        if sentences is not None:
            self.set_sentences(sentences)

    def set_sentences(self, sentences):
        if len(sentences) == 0:
            raise ValueError("Sentence list empty")
        self.sentences = sentences
        for index, sentence in enumerate(self.sentences):
            sentence.id = index
            if not hasattr(sentence, 'annotation'):
                sentence.annotation = ''

    def safe_mkdir(self, dirname):
        dir = os.path.join(os.path.expanduser(annotation_dir), dirname)
        try:
            os.mkdir(dir)
        except OSError:
            pass
        return dir

    def write_splitted(self, sentence, sheet, row):
        start, end = sentence.metadata.get('highlight', (0, 0))
        words = [w if w else '' for w in sentence.words]
        # None words - where do they come from?

        before = ' '.join(words[:start])[-45:]
        verb = ' '.join(words[start:end+1])
        after = ' '.join(words[end+1:])[:45]
        all = ' '.join(words)
        
        sheet.write(row, 0, sentence.annotation, excel_alignments.left)
        sheet.write(row, 1, after, excel_alignments.right)
        sheet.write(row, 2, verb, excel_alignments.center)
        sheet.write(row, 3, before, excel_alignments.left)
        sheet.write(row, 4, all, excel_alignments.left)
        sheet.write(row, 5, sentence.id, excel_alignments.left)

        col_index = 6
        if self.custom_fields is not None:
            for field in self.custom_fields:
                custom_data = ''
                if isinstance(field, basestring):
                    custom_data = sentence.metadata[field]
                elif callable(field):
                    custom_data = field(sentence)
                else:
                    raise TypeError("Can't handle custom field %s" % field)
                sheet.write(row, col_index, custom_data, 
                            excel_alignments.right)
                col_index += 1

    def escape_name(self, name):
        safe_name = re.sub(r'[/\?\*]', '_', name)
        if safe_name != name:
            print 'Renamed "%s" to "%s"' % (name, safe_name)
        return safe_name

    def write(self, dirname=None):

        if dirname is None:
            dirname = self.description

        self.create_workbooks()
        dir = self.safe_mkdir(dirname)

        print 'Saving annotation in directory %s' % dir
        for workbook_name, sheets in self.workbooks.items():

            workbook_name = self.escape_name(workbook_name)
            workbook = Workbook()

            for sheet_name, sentences in sorted(sheets.items()):
                sheet_name = self.escape_name(sheet_name)
                sheet = workbook.add_sheet(sheet_name)
                sheet.col(1).width = 0x3000
                sheet.col(3).width = 0x3000

                for index, sentence in enumerate(sentences):
                    self.write_splitted(sentence, sheet, index)

            meta_sheet = workbook.add_sheet('meta')
            meta_sheet.write(0, 0, self.description)
            meta_sheet.write(1, 0, str(datetime.now()))

            outfile = os.path.join(dir, '%s.xls' % workbook_name)
            workbook.save(outfile)

        sentence_file_name = os.path.join(dir, 'sentences.json')
        write_sentence_file(self.sentences, sentence_file_name)

    def create_workbooks(self):
        raise NotImplementedError()
