from pyExcelerator import parse_xls, Workbook

class AnnotationProcessor(object):

    def __init__(self, destinations=None, ignore_empty=False):
        self.destinations = destinations or {}
        self.ignore_empty = ignore_empty

    def process(self, filename):
        workbook = Workbook()
        sheets = {}

        for sheet_name, values in parse_xls(filename, 'utf8'):
            n_rows = max(x[0] for x in values.keys())
            for row in range(1, n_rows + 1):
                annotation = values.get((row, 0), '')
                if annotation == '':
                    if self.ignore_empty:
                        continue
                    else:
                        target = sheet_name
                else:
                    target = self.destinations.get(annotation, annotation)

                if target not in sheets:
                    sheets[target] = [workbook.add_sheet(target), 0]
                
                sheet, sheet_row = sheets[target]
                for i in range(1, 5):
                    sheet.write(sheet_row, i, values.get((row, i), ''))

                sheets[target][1] = sheet_row + 1

        if filename.endswith('.xls'):
            filename = filename[:-4]

        workbook.save(filename + '.processed.xls')
