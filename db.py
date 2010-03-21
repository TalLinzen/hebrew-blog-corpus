import sys, traceback
from tools.transliterator import Transliterator

sqlobjectegg = '/Library/Frameworks/Python.framework/Versions/2.5/lib/python2.5/site-packages/SQLObject-0.10.2-py2.5.egg' 
if sqlobjectegg not in sys.path: 
    sys.path.append(sqlobjectegg) 
    sys.path.append('/Library/Frameworks/Python.framework/Versions/2.5/lib/python2.5/site-packages/FormEncode-1.0.1-py2.5.egg') 
    sys.path.append('/Library/Frameworks/Python.framework/Versions/2.5/lib/python2.5/site-packages/MySQL_python-1.2.2-py2.5-macosx-10.3-fat.egg') 
from sqlobject import * 

class WebPage(SQLObject):

    url = StringCol()
    clean_text = StringCol(sqlType='LONGTEXT') # UnicodeCol(dbEncoding='utf8')
    raw = StringCol() # UnicodeCol(dbEncoding='cp1255')
    accessed = DateTimeCol()
    site = StringCol()
    age = IntCol()
    user = StringCol()
    sex = StringCol()
    analyzed = StringCol(sqlType='LONGTEXT')

class User(SQLObject):

    age = IntCol()
    number = StringCol(length=15)
    sex = StringCol(length=10)
    number_index = DatabaseIndex('number')

def setup_connection(password):

    connection_string = 'mysql://root:%s@localhost/corpus' % password
    connection = connectionForURI(connection_string)
    #connection.dbEncoding = 'utf8'
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
