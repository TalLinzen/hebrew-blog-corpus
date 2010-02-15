import sys, traceback
from transliterator import Transliterator

sqlobjectegg = '/Library/Frameworks/Python.framework/Versions/2.5/lib/python2.5/site-packages/SQLObject-0.10.2-py2.5.egg' 
if sqlobjectegg not in sys.path: 
    sys.path.append(sqlobjectegg) 
    sys.path.append('/Library/Frameworks/Python.framework/Versions/2.5/lib/python2.5/site-packages/FormEncode-1.0.1-py2.5.egg') 
    sys.path.append('/Library/Frameworks/Python.framework/Versions/2.5/lib/python2.5/site-packages/MySQL_python-1.2.2-py2.5-macosx-10.3-fat.egg') 
from sqlobject import * 

class WebPage(SQLObject):

    url = StringCol()
    clean_text = StringCol()
    raw = StringCol()
    accessed = DateTimeCol()
    site = StringCol()
    age = IntCol()
    user = StringCol()
    sex = StringCol()

class User(SQLObject):

    age = IntCol()
    number = StringCol(length=15)
    sex = StringCol(length=10)
    number_index = DatabaseIndex('number')

def setup_connection():

    connection_string = 'mysql://root:@localhost/corpus'
    connection = connectionForURI(connection_string)
    sqlhub.processConnection = connection

def insistent_db_op(func, *args, **kwargs):

    for i in range(10):
        try:
            return func(*args, **kwargs)
        except dberrors.ProgrammingError, exc:
            LOGGER.error(traceback.format_exc(exc))
            LOGGER.info('Reestablishing DB connection')
            setup_connection()

    LOGGER.critical('insistent_db_op: Giving up')
    raise exc
