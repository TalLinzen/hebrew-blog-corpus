import os
from pyExcelerator import Workbook
from annotation import Annotation

class ByUserAnnotation(Annotation):

    def __init__(self, filter):
        Annotation.__init__(self)
        self.filter = filter

    def write(self, dirname):

        dir = self.safe_mkdir(dirname)

        by_user = {}
        for sentence in self.filter.sentences:
            l = by_user.setdefault(sentence.metadata.get('user', 'NoUser'), [])
            l.append(sentence)

        for user, user_sentences in by_user.items():

            print 'Creating annotation spreadsheet for user %s' % user
            workbook = Workbook()
            sheet = workbook.add_sheet(str(user))
            sheet.col(1).width = 0x3000
            sheet.col(3).width = 0x3000
            for index, sentence in enumerate(user_sentences):
                highlight_area = self.get_highlight_area(sentence)
                self.write_splitted(sentence, highlight_area, sheet, index)
            outfile = os.path.join(dir, '%s.xls' % user)
            workbook.save(outfile)

    def get_highlight_area(self, sentence):
        raise NotImplementedError()


