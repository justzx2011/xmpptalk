import re
import io
import unicodedata
import hashlib
from functools import lru_cache
import builtins

import config

'''constants and simple functions'''

__version__ = 'pre-alpha'

# for i18n support
_ = lambda s: s

# install to builtin namespace
builtins.__version__ = __version__
builtins._ = _

PERM_USER = 1
PERM_GPADMIN = 2
PERM_SYSADMIN = 4

re_jid = re.compile(r'[^@ ]+@(?:\w+\.)+\w{2,4}')

def width(s, ambiwidth=2):
  if ambiwidth == 2:
    double = ('W', 'A')
  elif ambiwidth == 1:
    double = ('W',)
  else:
    raise ValueError('ambiwidth should be either 1 or 2')

  count = 0
  for i in s:
    if unicodedata.east_asian_width(i) in double:
      count += 2
      continue
    count += 1
  return count

@lru_cache()
def hashjid(jid):
  '''
  return a representation of the jid with least conflict but still keep
  confidential
  '''
  m = hashlib.md5()
  bare = '%s/%s' % (jid.local, jid.domain)
  m.update(bare.encode())
  m.update(config.salt)
  domain = m.hexdigest()[:6]
  return '%s@%s' % (jid.local[:config.nick_maxwidth-7], domain)

escape_map = {}

class Lex:
  def __init__(self, string):
    self.instream = io.StringIO(string)

  def get_token(self):
    ins = self.instream
    quote = None
    token = ''
    escaped = False
    while True:
      nextchar = ins.read(1)
      if not nextchar: # stream end
        return token
      elif escaped:
        token += escape_map.get(nextchar, nextchar)
        escaped = False
      elif nextchar == quote:
        return token
      elif nextchar in '\'"' and not quote:
        quote = nextchar
      elif nextchar == '\\':
        escaped = True
      elif nextchar.isspace():
        if quote:
          token += nextchar
        elif token:
          return token
      else:
        token += nextchar
