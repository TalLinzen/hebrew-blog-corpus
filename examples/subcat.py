# -*- coding: utf-8 -*-
import os

from hbc.annotation.subcat import SubcatAnnotation
from hbc.data.word_lists import einat_previous_experiment
from hbc.filters.subcat import SubcategorizationFrames
from hbc.io import BGUFile, BGUDir

def subcat_example():
    d = BGUDir(os.path.join(os.environ['HBC_PATH'], '5'))
    sf = SubcategorizationFrames(einat_previous_experiment, max_tokens=1000)
    sf.process_many(d)
    sa = SubcatAnnotation('Subcat example', sf)
    output = '/tmp/subcat_example'
    if not os.path.exists(output):
        os.mkdir(output)
    sa.write(output)
    return sa
