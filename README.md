Loading Database Dump
---------------------

Before the database dump can be loaded, the maximum packet size must be
increased.  Open a terminal, type `mysql` to get a mysql prompt, and issue
the following commands:

```
set global net_buffer_length=1000000; 
set global max_allowed_packet=1000000000;
create database corpus;
```

Then in another terminal window do:

```
mysql -h hostname -u user -p < filename
```


Dependencies
------------

Use `easy_install` to install the following packages:
* SQLObject
* MySQL-python
* lxml

For pylucene, follow the instruction at http://lucene.apache.org/pylucene/install.html.

You may have to link `libjcc.dylib` (in `/Library/Python2.7/site-packages/JCC`) to
`/usr/local/lib` if you get an "image not found" error.

To type Hebrew in ipython, `LC_TYPE` should be set to `en_IE.UTF-8`. Type raw strings rather than unicode strings (that is, don't use the u'...' prefix).
