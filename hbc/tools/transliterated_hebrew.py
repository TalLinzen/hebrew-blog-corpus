import codecs

### Codec APIs

class Codec(codecs.Codec):

    def encode(self,input,errors='strict'):
        return codecs.charmap_encode(input,errors,encoding_table)

    def decode(self,input,errors='strict'):
        return codecs.charmap_decode(input,errors,decoding_table)

class IncrementalEncoder(codecs.IncrementalEncoder):
    def encode(self, input, final=False):
        return codecs.charmap_encode(input,self.errors,encoding_table)[0]

class IncrementalDecoder(codecs.IncrementalDecoder):
    def decode(self, input, final=False):
        return codecs.charmap_decode(input,self.errors,decoding_table)[0]

class StreamWriter(Codec,codecs.StreamWriter):
    pass

class StreamReader(Codec,codecs.StreamReader):
    pass

### encodings module API

def getregentry(arg):
    return codecs.CodecInfo(
        name='transliterated-hebrew',
        encode=Codec().encode,
        decode=Codec().decode,
        incrementalencoder=IncrementalEncoder,
        incrementaldecoder=IncrementalDecoder,
        streamreader=StreamReader,
        streamwriter=StreamWriter,
    )


### Decoding Table

decoding_table = (
    u'\x00'     #  0x00 -> NULL
    u'\x01'     #  0x01 -> START OF HEADING
    u'\x02'     #  0x02 -> START OF TEXT
    u'\x03'     #  0x03 -> END OF TEXT
    u'\x04'     #  0x04 -> END OF TRANSMISSION
    u'\x05'     #  0x05 -> ENQUIRY
    u'\x06'     #  0x06 -> ACKNOWLEDGE
    u'\x07'     #  0x07 -> BELL
    u'\x08'     #  0x08 -> BACKSPACE
    u'\t'       #  0x09 -> HORIZONTAL TABULATION
    u'\n'       #  0x0A -> LINE FEED
    u'\x0b'     #  0x0B -> VERTICAL TABULATION
    u'\x0c'     #  0x0C -> FORM FEED
    u'\r'       #  0x0D -> CARRIAGE RETURN
    u'\x0e'     #  0x0E -> SHIFT OUT
    u'\x0f'     #  0x0F -> SHIFT IN
    u'\x10'     #  0x10 -> DATA LINK ESCAPE
    u'\x11'     #  0x11 -> DEVICE CONTROL ONE
    u'\x12'     #  0x12 -> DEVICE CONTROL TWO
    u'\x13'     #  0x13 -> DEVICE CONTROL THREE
    u'\x14'     #  0x14 -> DEVICE CONTROL FOUR
    u'\x15'     #  0x15 -> NEGATIVE ACKNOWLEDGE
    u'\x16'     #  0x16 -> SYNCHRONOUS IDLE
    u'\x17'     #  0x17 -> END OF TRANSMISSION BLOCK
    u'\x18'     #  0x18 -> CANCEL
    u'\x19'     #  0x19 -> END OF MEDIUM
    u'\x1a'     #  0x1A -> SUBSTITUTE
    u'\x1b'     #  0x1B -> ESCAPE
    u'\x1c'     #  0x1C -> FILE SEPARATOR
    u'\x1d'     #  0x1D -> GROUP SEPARATOR
    u'\x1e'     #  0x1E -> RECORD SEPARATOR
    u'\x1f'     #  0x1F -> UNIT SEPARATOR
    u' '        #  0x20 -> SPACE
    u'!'        #  0x21 -> EXCLAMATION MARK
    u'"'        #  0x22 -> QUOTATION MARK
    u'#'        #  0x23 -> NUMBER SIGN
    u'$'        #  0x24 -> DOLLAR SIGN
    u'%'        #  0x25 -> PERCENT SIGN
    u'&'        #  0x26 -> AMPERSAND
    u"'"        #  0x27 -> APOSTROPHE
    u'('        #  0x28 -> LEFT PARENTHESIS
    u')'        #  0x29 -> RIGHT PARENTHESIS
    u'*'        #  0x2A -> ASTERISK
    u'+'        #  0x2B -> PLUS SIGN
    u','        #  0x2C -> COMMA
    u'-'        #  0x2D -> HYPHEN-MINUS
    u'.'        #  0x2E -> FULL STOP
    u'/'        #  0x2F -> SOLIDUS
    u'0'        #  0x30 -> DIGIT ZERO
    u'1'        #  0x31 -> DIGIT ONE
    u'2'        #  0x32 -> DIGIT TWO
    u'3'        #  0x33 -> DIGIT THREE
    u'4'        #  0x34 -> DIGIT FOUR
    u'5'        #  0x35 -> DIGIT FIVE
    u'6'        #  0x36 -> DIGIT SIX
    u'7'        #  0x37 -> DIGIT SEVEN
    u'8'        #  0x38 -> DIGIT EIGHT
    u'9'        #  0x39 -> DIGIT NINE
    u':'        #  0x3A -> COLON
    u';'        #  0x3B -> SEMICOLON
    u'<'        #  0x3C -> LESS-THAN SIGN
    u'='        #  0x3D -> EQUALS SIGN
    u'>'        #  0x3E -> GREATER-THAN SIGN
    u'?'        #  0x3F -> QUESTION MARK
    u'@'        #  0x40 -> COMMERCIAL AT
    u'\ufffe'   #  0x41 -> UNDEFINED
    u'\ufffe'   #  0x42 -> UNDEFINED
    u'\u05e5'   #  0x43 -> HEBREW LETTER FINAL TSADI
    u'\ufffe'   #  0x44 -> UNDEFINED
    u'\ufffe'   #  0x45 -> UNDEFINED
    u'\ufffe'   #  0x46 -> UNDEFINED
    u'\ufffe'   #  0x47 -> UNDEFINED
    u'\ufffe'   #  0x48 -> UNDEFINED
    u'\ufffe'   #  0x49 -> UNDEFINED
    u'\ufffe'   #  0x4A -> UNDEFINED
    u'\u05da'   #  0x4B -> HEBREW LETTER FINAL KAF
    u'\ufffe'   #  0x4C -> UNDEFINED
    u'\u05dd'   #  0x4D -> HEBREW LETTER FINAL MEM
    u'\u05df'   #  0x4E -> HEBREW LETTER FINAL NUN
    u'\ufffe'   #  0x4F -> UNDEFINED
    u'\u05e3'   #  0x50 -> HEBREW LETTER FINAL PE
    u'\ufffe'   #  0x51 -> UNDEFINED
    u'\ufffe'   #  0x52 -> UNDEFINED
    u'\u05e9'   #  0x53 -> HEBREW LETTER SHIN
    u'\u05d8'   #  0x54 -> HEBREW LETTER TET
    u'\ufffe'   #  0x55 -> UNDEFINED
    u'\ufffe'   #  0x56 -> UNDEFINED
    u'\ufffe'   #  0x57 -> UNDEFINED
    u'\ufffe'   #  0x58 -> UNDEFINED
    u'\ufffe'   #  0x59 -> UNDEFINED
    u'\ufffe'   #  0x5A -> UNDEFINED
    u'\ufffe'   #  0x5B -> UNDEFINED
    u'\ufffe'   #  0x5C -> UNDEFINED
    u'\ufffe'   #  0x5D -> UNDEFINED
    u'\ufffe'   #  0x5E -> UNDEFINED
    u'\ufffe'   #  0x5F -> UNDEFINED
    u'\u05e2'   #  0x60 -> HEBREW LETTER AYIN
    u'\u05d0'   #  0x61 -> HEBREW LETTER ALEF
    u'\u05d1'   #  0x62 -> HEBREW LETTER BET
    u'\u05e6'   #  0x63 -> HEBREW LETTER TSADI
    u'\u05d3'   #  0x64 -> HEBREW LETTER DALET
    u'\ufffe'   #  0x65 -> UNDEFINED
    u'\ufffe'   #  0x66 -> UNDEFINED
    u'\u05d2'   #  0x67 -> HEBREW LETTER GIMEL
    u'\u05d4'   #  0x68 -> HEBREW LETTER HE
    u'\u05d9'   #  0x69 -> HEBREW LETTER YOD
    u'\ufffe'   #  0x6A -> UNDEFINED
    u'\u05db'   #  0x6B -> HEBREW LETTER KAF
    u'\u05dc'   #  0x6C -> HEBREW LETTER LAMED
    u'\u05de'   #  0x6D -> HEBREW LETTER MEM
    u'\u05e0'   #  0x6E -> HEBREW LETTER NUN
    u'\ufffe'   #  0x6F -> UNDEFINED
    u'\u05e4'   #  0x70 -> HEBREW LETTER PE
    u'\u05e7'   #  0x71 -> HEBREW LETTER QOF
    u'\u05e8'   #  0x72 -> HEBREW LETTER RESH
    u'\u05e1'   #  0x73 -> HEBREW LETTER SAMEKH
    u'\u05ea'   #  0x74 -> HEBREW LETTER TAV
    u'\ufffe'   #  0x75 -> UNDEFINED
    u'\ufffe'   #  0x76 -> UNDEFINED
    u'\u05d5'   #  0x77 -> HEBREW LETTER VAV
    u'\u05d7'   #  0x78 -> HEBREW LETTER HET
    u'\ufffe'   #  0x79 -> UNDEFINED
    u'\u05d6'   #  0x7A -> HEBREW LETTER ZAYIN
    u'\ufffe'   #  0x7B -> UNDEFINED
    u'\ufffe'   #  0x7C -> UNDEFINED
    u'\ufffe'   #  0x7D -> UNDEFINED
    u'\ufffe'   #  0x7E -> UNDEFINED
    u'\x7f'     #  0x7F -> CONTROL CHARACTER
    u'\ufffe'   
    u'\ufffe'   
    u'\ufffe'   
    u'\ufffe'   
    u'\ufffe'   
    u'\ufffe'   
    u'\ufffe'   
    u'\ufffe'   
    u'\ufffe'   
    u'\ufffe'   
    u'\ufffe'   
    u'\ufffe'   
    u'\ufffe'   
    u'\ufffe'   
    u'\ufffe'   
    u'\ufffe'   
    u'\ufffe'   
    u'\ufffe'   
    u'\ufffe'   
    u'\ufffe'   
    u'\ufffe'   
    u'\ufffe'   
    u'\ufffe'   
    u'\ufffe'   
    u'\ufffe'   
    u'\ufffe'   
    u'\ufffe'   
    u'\ufffe'   
    u'\ufffe'   
    u'\ufffe'   
    u'\ufffe'   
    u'\ufffe'   
    u'\ufffe'   
    u'\ufffe'   
    u'\ufffe'   
    u'\ufffe'   
    u'\ufffe'   
    u'\ufffe'   
    u'\ufffe'   
    u'\ufffe'   
    u'\ufffe'   
    u'\ufffe'   
    u'\ufffe'   
    u'\ufffe'   
    u'\ufffe'   
    u'\ufffe'   
    u'\ufffe'   
    u'\ufffe'   
    u'\ufffe'   
    u'\ufffe'   
    u'\ufffe'   
    u'\ufffe'   
    u'\ufffe'   
    u'\ufffe'   
    u'\ufffe'   
    u'\ufffe'   
    u'\ufffe'   
    u'\ufffe'   
    u'\ufffe'   
    u'\ufffe'   
    u'\ufffe'   
    u'\ufffe'   
    u'\ufffe'   
    u'\ufffe'   
    u'\ufffe'   
    u'\ufffe'   
    u'\ufffe'   
    u'\ufffe'   
    u'\ufffe'   
    u'\ufffe'   
    u'\ufffe'   
    u'\ufffe'   
    u'\ufffe'   
    u'\ufffe'   
    u'\ufffe'   
    u'\ufffe'   
    u'\ufffe'   
    u'\ufffe'   
    u'\ufffe'   
    u'\ufffe'   
    u'\ufffe'   
    u'\ufffe'   
    u'\ufffe'   
    u'\ufffe'   
    u'\ufffe'   
    u'\ufffe'   
    u'\ufffe'   
    u'\ufffe'   
    u'\ufffe'   
    u'\ufffe'   
    u'\ufffe'   
    u'\ufffe'   
    u'\ufffe'   
    u'\ufffe'   
    u'\ufffe'   
    u'\ufffe'   
    u'\ufffe'   
    u'\ufffe'   
    u'\ufffe'   
    u'\ufffe'   
    u'\ufffe'   
    u'\ufffe'   
    u'\ufffe'   
    u'\ufffe'   
    u'\ufffe'   
    u'\ufffe'   
    u'\ufffe'   
    u'\ufffe'   
    u'\ufffe'   
    u'\ufffe'   
    u'\ufffe'   
    u'\ufffe'   
    u'\ufffe'   
    u'\ufffe'   
    u'\ufffe'   
    u'\ufffe'   
    u'\ufffe'   
    u'\ufffe'   
    u'\ufffe'   
    u'\ufffe'   
    u'\ufffe'   
    u'\ufffe'   
    u'\ufffe'   
    u'\ufffe'   
    u'\ufffe'   
    u'\ufffe'   
    u'\ufffe'   
    u'\ufffe'   
)

### Encoding table
encoding_table = codecs.charmap_build(decoding_table)

codecs.register(getregentry)

