from xlwt import parse_xls, Workbook

class ExcelCounter(object):

    def __init__(self, source, columns):
        self.source = source
        self.columns = columns
        self.counters = {}
        self.count()

    def count(self):
        for sheet_name, values in parse_xls(self.source, 'utf8'):
            for row_idx, col_idx in sorted(values.keys()):
                if col_idx in self.columns:
                    value = values[(row_idx, col_idx)]
                    self.counters[value] = self.counters.get(value, 0) + 1

    def save(self, where='/tmp/count.xls'):
        wb = Workbook()
        sheet = wb.add_sheet('Count')
        for i, (key, value) in enumerate(sorted(self.counters.items())):
            sheet.write(i, 0, key)
            sheet.write(i, 1, value)
        wb.save(where)

        
