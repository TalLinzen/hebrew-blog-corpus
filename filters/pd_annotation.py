import os
from pyExcelerator import Workbook
from annotation import Annotation

class PDAnnotation(Annotation):

    def create(self, pd_filter):

        dir = os.path.expanduser('~/corpus/annotations')

        workbook = Workbook()
            
        sheet = workbook.add_sheet('Sheet')
        sheet.col(1).width = 0x3000
        sheet.col(3).width = 0x3000
        for index, sentence in enumerate(pd_filter.sentences):
            self.write_splitted(sentence, min(sentence.lamed_indices),
                    sheet, index)
                
        workbook.save(os.path.join(dir, 'pd.xls'))
