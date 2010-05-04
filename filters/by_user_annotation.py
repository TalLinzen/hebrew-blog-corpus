from annotation import Annotation

def group_by_attributes(attributes, sentences):
    if isinstance(attributes, basestring):
        attributes = [attributes]
    by_attributes = {}
    for sentence in sentences:
        values = []
        for attribute in attributes:
            value = sentence.metadata.get(attribute, 'None')
            if value == None:
                value = 'None'
            values.append(value)
        by_attributes.setdefault('_'.join(values), []).append(sentence)
    return by_attributes

def mix_attributes(attributes, sentences, limit):
    result = []
    index = 0
    limit = min(limit, len(sentences))
    by_attributes = group_by_attributes(attributes, sentences)

    while len(result) < limit:
        for sentence_group in by_attributes.values():
            if len(result) == limit:
                break
            elif index < len(sentence_group):
                result.append(sentence_group[index])
        index += 1
        
    return result

class ByAttributeAnnotation(Annotation):

    def __init__(self, description, attributes, single_workbook=False,
            single_workbook_name='All', min_tokens=2, max_tokens=3000,
            **options):
        '''
        single_workbook: if True, all attribute values will be on the same
            workbook, as sheets; otherwise create separate files for each value
        single_file_name: name to give single workbook, if applicable
        min_tokens: if attribute value has less than this number of occurences
            don't create a sheet for it
        max_tokens: stop writing sentences to sheet after this amount of
            tokens of this value have been written
        '''

        Annotation.__init__(self, description, **options)
        self.attributes = attributes
        self.single_workbook = single_workbook
        self.single_workbook_name = single_workbook_name
        self.min_tokens = min_tokens
        self.max_tokens = max_tokens

    def create_workbooks(self):
        by_attributes = group_by_attributes(self.attributes, self.sentences)
        d = {}
        for value, sentences in by_attributes.items():
            if len(sentences) >= self.min_tokens:
                d[value] = mix_attributes('user', sentences, self.max_tokens)

        if self.single_workbook:
            self.workbooks = {self.single_workbook_name: by_attributes}
        else:
            self.workbooks = dict((value, {value: sentences}) for \
                    value, sentences in d.items())

class MixUsers(Annotation):
    def __init__(self, limit=10000, **options):
        Annotation.__init__(self, **options)
        self.limit = limit

    def create_workbooks(self):
        mixed = mix_attributes('user', self.sentences, self.limit)
        self.workbooks = {'mixed': {'Mixed': mixed}}
