import logging
import os

root = os.path.dirname(os.path.abspath(__file__))
hspell_dir = os.path.join(root, 'data', 'hspell')
annotation_dir = os.path.join(root, 'annotations')
data_dir = os.path.join(root, 'data')
analyzed_corpus_dir = os.path.expanduser('~/corpus/analyzed')
lucene_index_dir = os.path.expanduser('~/corpus/lucene_index_full')

log_format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
logging.basicConfig(format=log_format, level=logging.INFO)
