import os, json, re
from datetime import datetime
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
    '''
    Load manual annotations from Excel files and update the JSON file
    '''
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

    def __init__(self, description, sentences=None, custom_field=None):
        self.workbooks = {}
        self.description = description
        self.custom_field = custom_field
        if sentences:
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
        dir = os.path.join(os.path.expanduser('~/corpus/annotations'), dirname)
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
        
        sheet.write(row, 0, sentence.annotation, self.left)
        sheet.write(row, 1, after, self.right)
        sheet.write(row, 2, verb, self.center)
        sheet.write(row, 3, before, self.left)
        sheet.write(row, 4, all, self.left)
        sheet.write(row, 5, sentence.id, self.left)
        custom_data = ''
        if isinstance(self.custom_field, basestring):
            custom_data = sentence.metadata[self.custom_field]
        elif callable(self.custom_field):
            custom_data = self.custom_field(sentence)
        sheet.write(row, 6, custom_data, self.right)

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


def group_by_attributes(attributes, sentences):
    if isinstance(attributes, basestring):
        attributes = [attributes]
    by_attributes = {}
    for sentence in sentences:
        values = []
        for attribute in attributes:
            value = sentence.metadata.get(attribute, 'None')
            if value == None:
                value = 'None'
            values.append(value)
        by_attributes.setdefault('_'.join(values), []).append(sentence)
    return by_attributes

def mix_attributes(attributes, sentences, limit):
    result = []
    index = 0
    limit = min(limit, len(sentences))
    by_attributes = group_by_attributes(attributes, sentences)

    while len(result) < limit:
        for sentence_group in by_attributes.values():
            if len(result) == limit:
                break
            elif index < len(sentence_group):
                result.append(sentence_group[index])
        index += 1
        
    return result

class ByAttributeAnnotation(Annotation):

    def __init__(self, description, attributes, inner_attributes=None,
            single_workbook=False, single_workbook_name=None, min_tokens=2,
            max_tokens=3000, **options):
        '''
        single_workbook: if True, all attribute values will be on the same
            workbook, as sheets; otherwise create separate files for each value
        single_workbook_name: name to give single workbook, if applicable
        min_tokens: if attribute value has less than this number of occurences
            don't create a sheet for it
        max_tokens: stop writing sentences to sheet after this amount of
            tokens of this value have been written
        '''

        Annotation.__init__(self, description, **options)
        self.attributes = attributes
        if single_workbook and inner_attributes:
            raise ValueError("single_workbook and inner_attributes " \
                    "cannot both be set")
        self.single_workbook = single_workbook
        self.inner_attributes = inner_attributes
        self.single_workbook_name = single_workbook_name
        self.min_tokens = min_tokens
        self.max_tokens = max_tokens
        self.workbooks = {}

    def create_workbooks(self):
        by_attributes = group_by_attributes(self.attributes, self.sentences)
        d = {}
        for value, sentences in by_attributes.items():
            if self.inner_attributes is not None:
                by_inner = group_by_attributes(self.inner_attributes,
                        sentences)
                inner_d = {}
                for inner, inner_sentences in by_inner.items():
                    if len(inner_sentences) >= self.min_tokens:
                        inner_d[inner] = mix_attributes(
                                'user', inner_sentences, self.max_tokens)
                if len(inner_d) > 0:
                    self.workbooks[value] = inner_d
            else:
                if len(sentences) >= self.min_tokens:
                    d[value] = mix_attributes(
                            'user', sentences, self.max_tokens)

        if self.inner_attributes is None:
            if self.single_workbook:
                name = self.single_workbook_name or self.description
                self.workbooks = {name: d}
            else:
                self.workbooks = dict((value, {value: sentences}) for \
                        value, sentences in d.items())

class MixUsers(Annotation):
    def __init__(self, limit=10000, **options):
        Annotation.__init__(self, **options)
        self.limit = limit

    def create_workbooks(self):
        mixed = mix_attributes('user', self.sentences, self.limit)
        self.workbooks = {'mixed': {'Mixed': mixed}}
