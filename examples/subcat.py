# -*- coding: utf-8 -*-
from filters.subcat import SubcategorizationFrames
from filters.subcat_annotation import SubcatAnnotation
from data.word_lists import einat_previous_experiment
from io import BGUFile, BGUDir
import os

def subcat_example():
    d = BGUDir('/Users/tal/corpus/analyzed/4')
    sf = SubcategorizationFrames(einat_previous_experiment, max_tokens=1000)
    sf.process_many(d)
    sa = SubcatAnnotation('Whole corpus for Einats revision', sf)
    output = '/tmp/einat_previous_experiment'
    if not os.path.exists(output):
        os.mkdir(output)
    sa.write(output)
