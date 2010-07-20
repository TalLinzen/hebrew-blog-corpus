import sys, traceback
from sqlobject import * 

class WebPage(SQLObject):

    url = StringCol()
    clean_text = StringCol(sqlType='LONGTEXT') # UnicodeCol(dbEncoding='utf8')
    raw = StringCol() # UnicodeCol(dbEncoding='cp1255')
    accessed = DateTimeCol()
    site = StringCol()
    age = IntCol()
    birthyear = IntCol()
    user = StringCol()
    sex = StringCol()
    analyzed = StringCol(sqlType='LONGTEXT')

class User(SQLObject):

    age = IntCol()
    birthyear = IntCol()
    number = StringCol(length=15, alternateID=True)
    sex = StringCol(length=10)
    chars = IntCol()
    number_index = DatabaseIndex('number')

class Sentence(SQLObject):
    
    webpage_id = IntCol()
    sentence_id = IntCol()
    data = UnicodeCol(dbEncoding='utf8')   # dbEncoding does nothing? change this manually in DB
    filename_and_sentence_id_index = DatabaseIndex('webpage_id', 'sentence_id')

def setup_connection(password):

    connection_string = 'mysql://root:%s@localhost/corpus' % password
    connection = connectionForURI(connection_string)
    connection.dbEncoding = 'utf8'
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
