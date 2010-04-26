from annotation import Annotation

class ByAttributeAnnotation(Annotation):
    '''
    Separate file for each user
    '''
    def create_workbooks(self):
        for sentence in self.filter.sentences:
            value = sentence.metadata.get(self.attribute, 'None')
            workbook = self.workbooks.setdefault(value, {value: []})
            workbook[value].append(sentence)

class ByUserAnnotation(ByAttributeAnnotation):
    attribute = 'user'

class MixUsers(Annotation):
    def __init__(self, filter, limit):
        Annotation.__init__(self, filter)
        self.limit = limit

    def create_workbooks(self):
        by_user = {}
        for sentence in self.filter.sentences:
            user = sentence.metadata.get('user')
            if user is None:
                continue
            user_list = by_user.setdefault(user, [])
            user_list.append(sentence)

        self.workbooks = {'mixed': {'Mixed': []}}
        n_written = 0
        index = 0
        while n_written < self.limit:
            for sentences in by_user.values():
                if n_written == self.limit:
                    break
                else:
                    self.workbooks['mixed']['Mixed'].append(sentences[index])
                    n_written += 1  
            index += 1
