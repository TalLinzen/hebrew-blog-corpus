import os
from pyExcelerator import Workbook
from annotation import Annotation

class SubcatAnnotation(Annotation):

    def __init__(self, subcat_filter, max_sentences=None):
        self.subcat_filter = subcat_filter
        self.max_sentences = max_sentences

    def write(self, dirname):
        dir = self.safe_mkdir(dirname)

        for lemma, sentences in self.subcat_filter.dict.items():
            if self.max_sentences != None:
                sentences = sentences[:self.max_sentences]

            workbook = Workbook()
            
            by_argument_type = {}
            for index, sentence in enumerate(sentences):
                l = by_argument_type.setdefault(
                        getattr(sentence, 'argument', 'NONE'), [])
                l.append((sentence, index))

            for argument_type, sentences_of_type in \
                    sorted(by_argument_type.items()):
                sheet = workbook.add_sheet(argument_type)
                sheet.col(1).width = 0x3000
                sheet.col(2).width = 0x1000
                sheet.col(3).width = 0x3000
                for index, (sentence, original_index) in \
                        enumerate(sentences_of_type):
                    highlight = (sentence.verb_index, sentence.verb_index)
                    self.write_splitted(sentence, highlight, sheet, index)
                
            workbook.save(os.path.join(dir, lemma + '.xls'))
