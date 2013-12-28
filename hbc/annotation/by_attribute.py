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

    def __init__(self, description, attributes, inner_attributes=None,
            mode='split_workbooks', single_workbook_name=None,
            min_tokens=2, max_tokens=3000, **options):
        '''
        Classify sentences based on some of their attributes, and write
        them to XLS files. Lists of sentences will be taken from different
        users, distributed as evenly as possible (cf. MixUsers).

        sentences:
            list of sentences (same as Filter.sentences). [Inherited
            from Annotation base class]

        description:
            a textual description of the annotation. Will appear in a
            'meta' sheet of each workbook. Mandatory.

        attributes:
            a single attribute, or a tuple of attributes, by which
            the sentences will be classified into annotation files (the
            exact behavior depends on the mode)
            
        inner_attributes:
            only applicable for the split workbooks mode. Combinations of
            the inner attributes will form the names of sheets within
            each workbook

        mode:
            'single_workbook': one workbook with different sheet for each
                attribute combination
            'split_workbooks': separate workbook for each attribute combination
            'single_sheet': single workbook with a single sheet for all
                attribute combinations (but combination will appear in a
                dedicated spreadsheet column)

        single_workbook_name: 
            name of single workbook, if applicable

        min_tokens:
            if an attribute combination has less than this number of occurences
            discard this combination (do not write it to annotation files)

        max_tokens:
            stop writing sentences with any given attribute combination after
            this amount of tokens of this combination have been written

        Example:
        ByAttributeAnnotation("30 to 40 dative verbs, topicalized",
            sentences=sentences, attributes=['lemma', 'argument'])
        '''

        Annotation.__init__(self, description, **options)
        self.attributes = attributes

        if mode not in ('split_workbooks', 'single_workbook', 'single_sheet'):
            raise ValueError('unknown mode "%s"' % mode)

        if mode != 'split_workbooks' and inner_attributes:
            raise ValueError('inner_attributes can only be set when' \
                    'mode is "split_workbooks"')

        self.mode = mode
        self.inner_attributes = inner_attributes
        self.single_workbook_name = single_workbook_name
        self.min_tokens = min_tokens
        self.max_tokens = max_tokens
        self.workbooks = {}

    def create_workbooks(self):
        by_attributes = group_by_attributes(self.attributes, self.sentences)
        d = {}
        for value, sentences in by_attributes.items():
            if self.inner_attributes is not None:
                by_inner = group_by_attributes(self.inner_attributes,
                        sentences)
                inner_d = {}
                for inner, inner_sentences in by_inner.items():
                    if len(inner_sentences) >= self.min_tokens:
                        inner_d[inner] = mix_attributes(
                                'user', inner_sentences, self.max_tokens)
                if len(inner_d) > 0:
                    self.workbooks[value] = inner_d
            else:
                if len(sentences) >= self.min_tokens:
                    d[value] = mix_attributes(
                            'user', sentences, self.max_tokens)

        name = self.single_workbook_name or self.description
        if self.inner_attributes is None:
            if self.mode == 'single_workbook':
                self.workbooks = {name: d}
            elif self.mode == 'single_sheet':
                values = [x[1] for x in sorted(d.items())]
                values = reduce(lambda x, y: x + y, values)
                self.workbooks = {name: {name: values}}
            elif self.mode == 'split_workbooks':
                self.workbooks = dict((value, {value: sentences}) for \
                        value, sentences in d.items())
            else:
                assert 0, 'Invalid mode %s' % self.mode

class MixUsers(Annotation):

    def __init__(self, limit=10000, **options):
        Annotation.__init__(self, **options)
        self.limit = limit

    def create_workbooks(self):
        mixed = mix_attributes('user', self.sentences, self.limit)
        self.workbooks = {'mixed': {'Mixed': mixed}}
