import os, json
from pyExcelerator import XFStyle, Alignment, UnicodeUtils, Workbook, parse_xls
from .io import BGUSentence

UnicodeUtils.DEFAULT_ENCODING = 'utf8'

def read_sentence_file(filename):
    sentences = []
    for sentence in json.load(open(filename)):
        obj = BGUSentence()
        obj.__dict__.update(sentence)
        sentences.append(obj)
    return sentences

def write_sentence_file(sentences, filename):
    f = open(filename, 'w')
    json.dump([obj.__dict__ for obj in sentences], f)

def update_annotation_directory(dirname):

    sentence_file_name = os.path.join(dirname, 'sentences.json')
    sentences = read_sentence_file(sentence_file_name)

    for file in os.listdir(dirname):
        if file.endswith('.xls'):
            filename = os.path.join(dirname, file)
            parsed = parse_xls(filename, 'utf8')
            for sheet_name, values in parsed:
                max_row = max(x[0] for x in values.keys())
                for row in range(0, max_row + 1):
                    annotation = values.get((row, 0), '')
                    id = values[(row, 5)]
                    sentences[id].annotation = annotation

    write_sentence_file(sentences, sentence_file_name)


class Annotation(object):

    left = XFStyle()
    left_alignment = Alignment()
    left_alignment.horz = Alignment.HORZ_LEFT
    left_alignment.dire = Alignment.DIRECTION_RL
    left.alignment = left_alignment

    right = XFStyle()
    right_alignment = Alignment()
    right_alignment.horz = Alignment.HORZ_RIGHT
    right_alignment.dire = Alignment.DIRECTION_RL
    right.alignment = right_alignment

    center = XFStyle()
    center_alignment = Alignment()
    center_alignment.horz = Alignment.HORZ_CENTER
    center_alignment.direction = Alignment.DIRECTION_RL
    center.alignment = center_alignment

    def __init__(self):
        self.workbooks = {}

    def set_sentences(self, sentences):
        if len(sentences) == 0:
            raise ValueError("Sentence list empty")
        self.sentences = sentences
        for index, sentence in enumerate(self.sentences):
            sentence.id = index
            sentence.annotation = ''

    def safe_mkdir(self, dirname):
        dir = os.path.join(os.path.expanduser('~/corpus/annotations'), dirname)
        try:
            os.mkdir(dir)
        except OSError:
            pass
        return dir

    def write_splitted(self, sentence, sheet, row):
        start, end = sentence.highlight
        words = [w if w else '' for w in sentence.words]
        # None words - where do they come from?

        before = ' '.join(words[:start])[-45:]
        verb = ' '.join(words[start:end+1])
        after = ' '.join(words[end+1:])[:45]
        all = ' '.join(words)
        
        sheet.write(row, 0, sentence.annotation, self.left)
        sheet.write(row, 1, after, self.right)
        sheet.write(row, 2, verb, self.center)
        sheet.write(row, 3, before, self.left)
        sheet.write(row, 4, all, self.left)
        sheet.write(row, 5, sentence.id, self.left)

    def write(self, dirname):

        self.create_workbooks()
        dir = self.safe_mkdir(dirname)

        for workbook_name, sheets in self.workbooks.items():

            print 'Adding workbook', workbook_name
            workbook = Workbook()

            for sheet_name, sentences in sorted(sheets.items()):
                sheet = workbook.add_sheet(sheet_name)
                sheet.col(1).width = 0x3000
                sheet.col(3).width = 0x3000

                for index, sentence in enumerate(sentences):
                    self.write_splitted(sentence, sheet, index)

            outfile = os.path.join(dir, '%s.xls' % workbook_name)
            workbook.save(outfile)

        sentence_file_name = os.path.join(dir, 'sentences.json')
        write_sentence_file(self.sentences, sentence_file_name)


    def get_highlight_area(self, sentence):
        raise NotImplementedError()

    def create_workbooks(self):
        raise NotImplementedError()
