
MASKS = {'PREFIX':     0x756, # ^ 0x4,           # 0x756 ^ DEF
         'POS':        0x1F0000,           # bits 17-21
         'GENDER':     0x0000000000600000, # bits 22-23
         'NUMBER':     0x7000000,          # bits 25-27
         'PERSON':     0x38000000,         # bits 28-30
         'STATUS':     0x00000000c0000000, # bits 31-32
         'TENSE':      0xE00000000,        # bits 34-36
         'SUFFIX':     0x0000fdb000000000, # bits 37-38, 40-41, 43-48
         'SUFF_FUNC':  0x0000003000000000, # bits 37-38
         'SUFF_GEN':   0x0000018000000000, # bits 40-41

         'SUFF_NUM':   0x1c0000000000,     # bits 43-45
         'SUFF_PERS':  0xE00000000000,     # bits 46-48
         'CONT':       0x1000000000000,    # bits 49
         'POLARITY':   0x6000000000000,    # bits 50-51
         'BINYAN':     0x0038000000000000, # bits 52-54 base form BINYAN
         'CONJ_TYPE':  0x00c0000000000000, # bits 55-56 base form conjunction type
         'PRON_TYPE':  0x0700000000000000, # bits 57-59 base form pronoun type
         'NUM_TYPE':   0x0000000000007000, # bits 13-15 @NEW

         'INTEROGATOVE_TYPE' : 0x0001004000000020, # bits 6,39,49 @NEW
         'QUANTIFIER_TYPE'   : 0x0000000100800000, # bits 24,33 @NEW
         }

POS = {
      'ADJECTIVE':         0x0000000000010000,
      'ADVERB':            0x0000000000020000,
      'CONJUNCTION':       0x0000000000030000,
      'AT_PREP':           0x0000000000040000, # NOT IN MILA
      'NEGATION':          0x0000000000050000,
      'NOUN':              0x0000000000060000,
      'NUMERAL':           0x0000000000070000,
      'PREPOSITION':       0x00000000000080000,
      'PRONOUN':           0x0000000000090000,
      'PROPERNAME':        0x00000000000a0000,
      'PARTICLE':          0x00000000000b0000, # NOT USED
      #'AUXVERB':           0x00000000000c0000, # NOT USED
      'VERB':              0x00000000000d0000,
      'PUNCUATION':        0x00000000000e0000,
      'INTERROGATIVE':     0x00000000000f0000,
      'INTERJECTION':      0x0000000000100000,
      'UNKNOWN':           0x0000000000110000,
      'QUANTIFIER':        0x0000000000120000,
      'EXISTENTIAL':       0x0000000000130000,
      'MODAL':             0x0000000000140000,
      'PREFIX':            0x0000000000150000,
      'URL':               0x0000000000160000,
      'FOREIGN':           0x0000000000170000,
      'JUNK':              0x0000000000180000,
      #'IMPERSONAL':        0x0000000000190000, # NOT USED
      'PARTICIPLE':        0x00000000001a0000,
      'COPULA':            0x00000000001b0000,
      'NUMEXP':            0x00000000001c0000,
      'TITULA':            0x00000000001d0000,
      'SHEL_PREP':         0x00000000001e0000, # NOT IN MILA
      }

GENDER={
      'M':  0x0000000000200000,
      'F':0x0000000000400000,
      'MF':0x0000000000600000,
      }
NUMBER={
      'S':0x0000000001000000,
      'P':0x0000000002000000,
      'D':0x0000000003000000,
      'DP':0x0000000004000000,
      'SP':0x0000000005000000,
      }
PERSON={
'1':0x0000000008000000,
'2':0x0000000010000000,
'3':0x0000000018000000,
'A':0x0000000020000000,
}
STATUS={
      'ABS':0x0000000040000000,
      'CONST':0x0000000080000000,
      }
TENSE={
      'PAST':0x0000000200000000,
      'ALLTIME': 0x0000000400000000,  # @NEW
      'BEINONI':0x0000000600000000,
      'FUTURE':0x0000000800000000,
      'IMPERATIVE':0x0000000a00000000,
      'TOINFINITIVE':0x0000000c00000000,
      'BAREINFINITIVE':0x0000000e00000000,
      }
POLARITY={
      'POSITIVE':0x0002000000000000,
      'NEGATIVE':0x0004000000000000,
      }
BINYAN={
      'PAAL'    :0x0008000000000000,
      'NIFAL'   :0x0010000000000000,
      'HIFIL'   :0x0018000000000000,
      'HUFAL'   :0x0020000000000000,
      'PIEL'    :0x0028000000000000,
      'PUAL'    :0x0030000000000000,
      'HITPAEL' :0x0038000000000000,
}

CONJ_TYPE={
      'COORD': 0x0040000000000000,
      'SUB':   0x0080000000000000,
      'REL':   0x00c0000000000000
}
PRON_TYPE={
      'PERS': 0x0100000000000000, # PERSONAL
      'DEM':  0x0200000000000000, # DEMONSTRATIVE
      'IMP':  0x0300000000000000, # IMPERSONAL
      'REF':  0x0400000000000000, # REFLEXIVE @@@@
      #'INT':  0x0300000000000000, # INTEROGATIVE
      #'REL':  0x0400000000000000, # RELETIVIZER
}
NUM_TYPE={
   'ORDINAL' : 0x1000,
   'CARDINAL': 0x2000,
   'FRACTIONAL': 0x3000,
   'LITERAL': 0x4000,
   'GIMATRIA': 0x5000,
}
INTEROGATIVE_TYPE={
   'PRONOUN' : 0x20,
   'PROADVERB' : 0x0000004000000000,
   'PRODET'    : 0x0000004000000020,
   'YESNO'     : 0x0001000000000000,
}
QUANTIFIER_TYPE={
   'AMOUNT'    : 0x0000000000800000,
   'PARTITIVE' : 0x0000000100000000,
   'DETERMINER': 0x0000000100800000,
}

FEATURES = {}
for f in [GENDER,NUMBER,PERSON,STATUS,TENSE,POLARITY,BINYAN,CONJ_TYPE,PRON_TYPE]:
      FEATURES.update(f)



SUFFIX={
      'POSSESIVE':0x0000001000000000,
      'ACC-NOM':0x0000002000000000,    # This is the nominative
      'PRONOMIAL':0x0000003000000000,  # for ADVERBS and PREPS
      }
SHORTSUFFIX={
      'POSSESIVE':'S_PP',
      'PRONOMIAL': 'S_PRN',  # for ADVERBS and PREPS
      'ACC-NOM': 'S_ANP',    # This is the nominative
      '': None # NO suffix
      }
SUFF_GEN={
      'M':0x0000008000000000,
      'F':0x0000010000000000,
      'MF':0x0000018000000000,
      }
SUFF_NUM={
      'S':0x0000040000000000,
      'P':0x0000080000000000,
      'D':0x00000c0000000000,
      'DP':0x0000100000000000,
      'SP':0x0000140000000000,
      }
SUFF_PERS={
      '1':0x0000200000000000,
      '2':0x0000400000000000,
      '3':0x0000600000000000,
      'A':0x0000800000000000,
      }

SFEATURES = {}
for f in SUFF_PERS, SUFF_NUM, SUFF_GEN:
   SFEATURES.update(f)

PREFIX={
      'CONJ':0x0000000000000002, 
      'DEF':0x0000000000000004,  # used as a feature..
      'INTERROGATIVE':0x0000000000000010,
      'PREPOSITION':0x0000000000000040,
      'REL-SUBCONJ':0x00000000000000100,
      'TEMP-SUBCONJ':0x00000000000000200,
      'TENSEINV':0x0000000000000020,
      'ADVERB':0x00000000000000400,
      'PREPOSITION2':0x0000000000000080, #??
      }

#### map long POS name to short encoding
SHORTPOS = {
      'ADJECTIVE':         'JJ',
      'ADVERB':            'RB',
      'CONJUNCTION':       'CC',
      'AT_PREP':           'AT',
      'NEGATION':          'NEG',
      'NOUN':              'NN',
      'NUMERAL':           'CD',
      'PREPOSITION':       'IN',
      'PRONOUN':           'PRP',
      'PROPERNAME':        'NNP',
      'VERB':              'VB',
      'PUNCUATION':        'PUNC',
      'INTERROGATIVE':     'QW',
      'INTERJECTION':      'INTJ',
      'UNKNOWN':           'UNK',
      'QUANTIFIER':        'DT',
      'EXISTENTIAL':       'EX',
      'MODAL':             'MD',
      'PREFIX':            'P',
      'URL':               'URL',
      'FOREIGN':           'FW',
      'JUNK':              'JNK',
      'PARTICIPLE':        'BN',
      'COPULA':            'COP',
      'NUMEXP':            'NCD',
      'TITULA':            'TTL',
      'SHEL_PREP':         'POS',
      'PARTICLE':          'PRT',
      '' : '',
      }

__PREF_PRECEDENCE = {#{{{
      'CONJ' : 0,
      'REL-SUBCONJ' : 1,
      'TEMP-SUBCONJ' : 1,
      'PREPOSITION' : 2,
      'ADVERB' : 3,
      'TENSEINV' : 5, #@VERIFY...
      'DEF': 4,
      }
#}}}

def order_prefixes(prefs):#{{{
   prefs = [x for x in prefs if x]
   prefs = sorted(prefs, key=lambda p:__PREF_PRECEDENCE[p])
   return prefs
#}}}



def revdict(d):
   res = dict(((v,k) for (k,v) in d.iteritems()))
   return res
   
SHORT_TO_LONG_POS = revdict(SHORTPOS)
SHORT_TO_LONG_SUF = revdict(SHORTSUFFIX)

def _bminvlookup(mask,table,bm):
   bm = bm & MASKS[mask]
   res = []
   for k,v in table.items():
      if v == bm: res.append(k)
   res.sort()
   #if mask=='SUFFIX' and res: print "can't find",res
   #if mask=='SUFFIX' and bm and not res: print "bm: %x" % bm
   return " ".join(res)

def bm_is_definite(bm): return bm & MASKS['PREFIX'] == 0x04
def bm_get_pos(bm): return _bminvlookup('POS',POS,bm)
def bm_get_gender(bm): return _bminvlookup('GENDER',GENDER,bm)
def bm_get_number(bm): return _bminvlookup('NUMBER',NUMBER,bm)
def bm_get_person(bm): return _bminvlookup('PERSON',PERSON,bm)
def bm_get_status(bm): return _bminvlookup('STATUS',STATUS,bm)
def bm_get_tense(bm): return _bminvlookup('TENSE',TENSE,bm)
def bm_get_polarity(bm): return _bminvlookup('POLARITY',POLARITY,bm)

def bm_get_prntype(bm): return _bminvlookup('PRON_TYPE',PRON_TYPE ,bm)
def bm_get_cnjtype(bm): return _bminvlookup('CONJ_TYPE',CONJ_TYPE,bm)
def bm_get_numtype(bm): return _bminvlookup('NUM_TYPE',NUM_TYPE,bm)
def bm_get_inttype(bm): return _bminvlookup('INTEROGATIVE_TYPE',INTEROGATIVE_TYPE,bm)
def bm_get_qnttype(bm): return _bminvlookup('QUANTIFIER_TYPE',QUANTIFIER_TYPE,bm)
def bm_get_binyan(bm): return _bminvlookup('BINYAN',BINYAN,bm)
#def bm_get_prefixes(bm): return _bminvlookup('PREFIX',PREFIX,bm)
def bm_get_suff_func(bm): return _bminvlookup('SUFF_FUNC',SUFFIX,bm)
def bm_get_suff_gen(bm): return _bminvlookup('SUFF_GEN',SUFF_GEN,bm)
def bm_get_suff_num(bm): return _bminvlookup('SUFF_NUM',SUFF_NUM,bm)
def bm_get_suff_pers(bm): return _bminvlookup('SUFF_PERS',SUFF_PERS,bm)

def bm_get_definite(bm): 
   if bm_is_definite(bm): return "H"
   return ""

def bm_get_prefixes(bm):
   bm = bm & MASKS['PREFIX']
   res = []
   for k,v in PREFIX.items():
      if v & bm: res.append(k)
   #res.sort()
   #if mask=='SUFFIX' and res: print "can't find",res
   #if mask=='SUFFIX' and bm and not res: print "bm: %x" % bm
   return " ".join(res)

def tostring1(bm,nomods=False):
   prefs = bm_get_prefixes(bm).split()
   base  = bm_get_pos(bm)
   mods = [f(bm) for f in [bm_get_gender,
                           bm_get_number,
                           bm_get_person,
                           bm_get_status,
                           bm_get_tense,
                           bm_get_polarity]]
   mods = [m for m in mods if m]
   if nomods: mods = [m for m in mods if m.find('CONST') > -1]
   sfunc = bm_get_suff_func(bm)
   smods = [f(bm) for f in [bm_get_suff_gen,
                            bm_get_suff_num,
                            bm_get_suff_pers,
                            ]]
   smods = [m for m in smods if m]

   res =["+".join(prefs)]
   res.append(":")
   res.append(base)
   if mods:
      res.append("-")
      res.append(",".join(mods))
   res.append(":")
   if sfunc: res.append(sfunc)
   if smods: 
      res.append("-")
      res.append(",".join(smods))
   return "".join(res)


def bm2tag(bm,word=None,nofeats=False):#{{{
   prefs = bm_get_prefixes(bm).split()
   base  = SHORTPOS[bm_get_pos(bm)]
   #if not base: print "NOBASE"  # H
   feats = [f(bm) for f in [bm_get_gender,
                           bm_get_number,
                           bm_get_person,
                           bm_get_tense,
                           bm_get_polarity,
                           bm_get_binyan,
                           bm_get_prntype,
                           bm_get_cnjtype,
                           #bm_get_numtype,  @NOT USED
                           #bm_get_inttype,  @NOT USED
                           #bm_get_qnttype,  @NOT USED
                           ]]
   feats = [f for f in feats if f] # all existing modifiers
   if nofeats: feats = []
   sfunc = SHORTSUFFIX[bm_get_suff_func(bm)]
   sfeats = [f(bm) for f in [bm_get_suff_gen,
                            bm_get_suff_num,
                            bm_get_suff_pers,
                            ]]
   sfeats = [f for f in sfeats if f]

   # prefs
   #prefs = order_prefixes(prefs, bm, word)
   prefs = order_prefixes(prefs)
   pref_string = "+".join(prefs)
   # base
   if bm_get_status(bm).find('CONST') > -1:
      base = "%sT" % base
   feats_string = "-".join(feats) 
   if feats_string.strip():
      base_string = "%s-%s" % (base, feats_string)
   else:
      base_string = base
   # suffix
   if sfunc: suff_string = sfunc
   else: suff_string = ''
   if sfeats: 
      sfeats_string = "-".join(sfeats)
      suff_string = "%s-%s" % (suff_string, sfeats_string)
  
   return "%s:%s:%s" % (pref_string, base_string, suff_string)#}}}


def parse_kc_tag(kct):#{{{
   tag = {}
   if kct.find("^U^") > -1:
      pre,kct = kct.split("^U^")
      tag['prequote'] = pre.split(":")[0]
   prf,base,suf = kct.split(":")
   
   prfs = prf.split("+")
   tag['prfs'] = prfs
   
   try: bpos, bfeats = base.split("-",1)
   except ValueError: bpos, bfeats = base,''
   bfeats = bfeats.split("-")
   tag['pos'] = bpos
   tag['feats'] = bfeats

   tag['suf'] = suf
   tag['stype'] = suf.split("-")[0]
   tag['sfeats'] = suf.split("-")[1:]

   return tag
#}}}

def tag2bm(tag):
   """
   Note: returned bm will not reflect any "prequote" information 
   """
   tag = parse_kc_tag(tag)
   bm = 0
   # prefixes
   for p in tag['prfs']:
      if p:
         bm = bm | PREFIX[p]
   # base
   pos = tag['pos']
   if pos in ['JJT','NNT','CDT','DTT']:
      pos = pos[:-1]
   if pos:
      bm = bm | POS[SHORT_TO_LONG_POS[pos]]
   # features
   if tag['pos'] in ['JJT','NNT','CDT','DTT']:
      bm = bm | STATUS['CONST']
   elif tag['pos'] in ['JJ','NN','CD']:
      bm = bm | STATUS['ABS']

   for f in tag['feats']:
      if f == 'REL':
         if pos == 'PRP': bm = bm | PRON_TYPE[f]
         assert(pos == 'CC')
         bm = bm | CONJ_TYPE[f]
      else:
         if f in FEATURES:
            bm = bm | FEATURES[f]
         else:
            assert(not f),"unknown feature %s" % (f)
   # suffix
   suff = tag['stype']
   sfeat= tag['sfeats']
   if suff:
      bm = bm | SHORT_TO_LONG_SUF[SUFFIX[suff]]
      for f in sfeat:
         bm = bm | SFEATURES[f]

   return bm



##########
def find_pos(bm):
   bm=bm & MASKS['POS']
   for p,b in POS.items():
      if bm == b: return p
   return 'NONE'

def find_exts(bm):
   res=[]
   for m,b in MASKS.items():
      if m == 'POS': continue
      if b & bm:
         res.append(m)
   return res

from collections import defaultdict
count = 0
def collect_1(strm):
   global count
   cnt = defaultdict(set)
   for line in strm:
      line = line.strip().split()
      if not line:
         count+=1
         continue
      w,bm = line
      bm = int(bm)
      pos = find_pos(bm)
      exts = find_exts(bm)
      exts.sort()
      cnt[(pos," ".join(exts))].add(w)
   return cnt

def print_dict(strm):
   d = defaultdict(set)
   for line in strm:
      line = line.strip().split()
      if not line: 
         print
         continue
      w,bm = line
      bm = int(bm)
      pos = find_pos(bm)
      exts = find_exts(bm)
      exts.sort()
      d[w].add("%s / %s" % (pos," ".join(exts)))
      print w.encode("utf-8"),bm,"%s / %s" % (pos," ".join(exts))

   for w, anals in d.items():
      print w.encode("utf-8")
      for a in anals:
         print "\t",a
      print

def print_1(strm):
   c = collect_1(strm)
   for p in POS.keys():
      print p
      for (pos,mod),cnt in c.iteritems():
         if pos == p:
            print "\t",mod," ".join(list(cnt)[:5]).encode("utf-8")
      print
import codecs
import sys
if __name__ == '__main__':
   #print_1(codecs.open(sys.argv[1], encoding="utf-8"))
   #print_dict(codecs.open(sys.argv[1], encoding="utf-8"))
   #print count
   for line in codecs.open(sys.argv[1],encoding="utf-8"):
      line = line.strip().split()
      if not line: 
         print
         continue
      print line[0].encode("utf-8"),tostring1(int(line[1]))
