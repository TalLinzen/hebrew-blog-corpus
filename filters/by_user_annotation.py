from annotation import Annotation

def group_by_attribute(attribute, sentences):
    by_attribute = {}
    for sentence in sentences:
        value = sentence.metadata.get(attribute, 'None')
        if value == None:
            value = 'None'
        by_attribute.setdefault(value, []).append(sentence)
    return by_attribute

def mix_attribute(attribute, sentences, limit):

    result = []
    index = 0
    limit = min(limit, len(sentences))
    by_attribute = group_by_attribute(attribute, sentences)

    while len(result) < limit:
        for sentence_group in by_attribute.values():
            if len(result) == limit:
                break
            elif index < len(sentence_group):
                result.append(sentence_group[index])
        index += 1
        
    return result

class ByAttributeAnnotation(Annotation):
    '''
    Separate file for each value of attribute
    '''
    def __init__(self, attribute, single_workbook=False, 
            min_tokens=2, max_tokens=1000):
        '''
        single_workbook: if True, all attribute values will be on the same
            workbook, as sheets; otherwise create separate files for each value
        min_tokens: if attribute value has less than this number of occurences
            don't create a sheet for it
        max_tokens: stop writing sentences to sheet after this amount of
            tokens of this value have been written
        '''

        Annotation.__init__(self)
        self.attribute = attribute
        self.single_workbook = single_workbook
        self.min_tokens = min_tokens
        self.max_tokens = max_tokens

    def create_workbooks(self):
        by_attribute = group_by_attribute(self.attribute, self.filter.sentences)
        d = {}
        for value, sentences in by_attribute.items():
            if len(sentences) >= self.min_tokens:
                d[value] = mix_attribute('user', sentences, self.max_tokens)

        if self.single_workbook:
            self.workbooks = {'All': by_attribute}
        else:
            self.workbooks = dict((value, {value: sentences}) for \
                    value, sentences in d.items())

class MixUsers(Annotation):
    def __init__(self, limit=10000):
        Annotation.__init__(self)
        self.limit = limit

    def create_workbooks(self):
        mixed = mix_attribute('user', self.filter.sentences, self.limit)
        self.workbooks = {'mixed': {'Mixed': mixed}}
