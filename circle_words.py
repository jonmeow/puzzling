#!/usr/bin/python

import sys

def _LoadWords():
  """Loads the words from the dict file."""
  words = set()
  with open('/usr/share/dict/words') as f:
    for l in f.readlines():
      l = l.strip()
      words.add(l)
  return words

def _TestRange(label, letters, words, results):
  for offset in xrange(26):
    test = ''.join([chr(ord('a') + (x - 1 + offset) % 26) for x in letters])
    print '%s %02s: %s' % (label, offset, test)
    if test in words:
      results.append((label, offset, test))

def Main():
  letters = [int(x) for x in sys.argv[1:]]
  if len(letters) < 1:
    sys.exit('Syntax: <script> <#> <#> <#>')

  words = _LoadWords()

  results = []
  _TestRange('f', letters, words, results)
  _TestRange('r', list(reversed(letters)), words, results)

  if results:
    print ''
    for l, o, w in sorted(results):
      print '%s %02s: %s' % (l, o, w)

if __name__ == '__main__':
  Main()
