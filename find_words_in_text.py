#!/usr/bin/python

import re
import sys

MIN = 4

def _LoadWords():
  """Loads the words from the dict file."""
  words = dict()
  with open('/usr/share/dict/words') as f:
    for w in f.readlines():
      w = w.strip()
      l = len(w)
      if l < MIN:
        continue
      if l not in words:
        words[l] = set()
      words[l].add(w)
  return words

def Main():
  args = sys.argv[1:]
  if len(args) < 1:
    sys.exit('Syntax: <script> <words ...>')
  args = [''.join(re.findall('[a-z]', word.lower())) for word in args]
  input_words = set(args)

  words = _LoadWords()

  blob = ''.join(args)
  print blob

  for x in xrange(len(blob)):
    for y in xrange(x+MIN, len(blob) + 1):
      w = blob[x:y]
      if w not in input_words and len(w) in words and w in words[len(w)]:
        print w

if __name__ == '__main__':
  Main()
