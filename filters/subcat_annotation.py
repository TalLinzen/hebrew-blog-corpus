from pyExcelerator import Workbook
from annotation import Annotation

class SubCatAnnotation(object):

    def split(self, sentence):
        words = [w.word if w.word else '' for w in sentence.words]
        # None words - where do they come from?
        index = sentence.verb_index
        strings = [' '.join(words[:index])[-45:],
                words[index],
                ' '.join(words[index+1:])[:45],
                ' '.join(words)]
        return tuple(x for x in strings)


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
                    before, verb, after, all = self.split(sentence)
                    sheet.write(index, 1, after, Annotation.right)
                    sheet.write(index, 2, verb, Annotation.center)
                    sheet.write(index, 3, before, Annotation.left)
                    sheet.write(index, 4, all, Annotation.left)
                    sheet.write(index, 5, original_index, Annotation.right)
                
            workbook.save(os.path.join(dir, lemma + '.xls'))
