import glob, os
from pyExcelerator import parse_xls, Workbook, UnicodeUtils
from excel_alignments import left, center, right
UnicodeUtils.DEFAULT_ENCODING = 'utf8'

class AnnotationProcessor(object):

    def __init__(self, destinations=None, ignore_empty=False):
        self.destinations = destinations or {}
        self.ignore_empty = ignore_empty

    def transform_workbook(self, parsed_xls):

        workbook = Workbook()
        sheets = {}

        for sheet_name, values in parsed_xls:
            max_row = max(x[0] for x in values.keys())
            for row in range(0, max_row + 1):
                annotation = values.get((row, 0), '').upper()
                if annotation == '':
                    if self.ignore_empty:
                        continue
                    else:
                        target = sheet_name.encode('utf8')
                else:
                    target = self.destinations.get(annotation, annotation)

                if target not in sheets:
                    sheets[target] = [workbook.add_sheet(target), 0]
                
                sheet, sheet_row = sheets[target]
                sheet.col(1).width = 0x3000
                sheet.col(3).width = 0x3000
                sheet.write(sheet_row, 1, values.get((row, 1), ''), right)
                sheet.write(sheet_row, 2, values.get((row, 2), ''), center)
                sheet.write(sheet_row, 3, values.get((row, 3), ''), left)
                sheet.write(sheet_row, 4, values.get((row, 4), ''), left)
                sheet.write(sheet_row, 5, values.get((row, 5), ''), left)

                sheets[target][1] = sheet_row + 1

        return workbook

    def process_dir(self, input_dir, output_dir=None):
        if output_dir is None:
            output_dir = os.path.join(input_dir, 'processed')

        try:
            os.mkdir(output_dir)
        except OSError:
            pass

        files = glob.glob(os.path.join(input_dir, '*.xls'))
        if len(files) == 0:
            raise ValueError('No xls files in specified path')

        for filename in files:
            parsed = parse_xls(filename, 'utf8')
            transformed = self.transform_workbook(parsed)
            target_filename = os.path.join(output_dir, os.path.basename(filename))
            transformed.save(target_filename)
