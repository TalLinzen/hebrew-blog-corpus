from db import setup_connection, WebPage, User
from israblog.clean import IsrablogCleaner, ExtractText
from pdb import pm
setup_connection()
cleaner = IsrablogCleaner()

def pheb(s):
    print s.decode('cp1255').encode('utf8')
