from pyExcelerator import Workbook
from annotation import Annotation

class SubCatAnnotation(object):

    def create(self, subcat_filter_dict):

        dir = '/Users/tal/annotations'

        for lemma, sentences in subcat_filter_dict.items():
            workbook = Workbook()
            
            by_argument_type = {}
            for index, sentence in enumerate(sentences):
                l = by_argument_type.setdefault(sentence.argument, [])
                l.append((sentence, index))

            for argument_type, sentences_of_type in \
                    sorted(by_argument_type.items()):
                sheet = workbook.add_sheet(argument_type)
                sheet.col(1).width = 0x3000
                sheet.col(3).width = 0x3000
                for index, (sentence, original_index) in \
                        enumerate(sentences_of_type):
                    self.write_splitted(sentence, sentence.verb_index, sheet, index)
                
            workbook.save(os.path.join(dir, lemma + '.xls'))
