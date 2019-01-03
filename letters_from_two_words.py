#!/usr/bin/python
#
# Given six letters that are three letters each from two words, give back possible word combinations.

import sys

def _LoadWords():
  """Loads the words from the dict file."""
  words = set()
  with open('/usr/share/dict/words') as f:
    for l in f.readlines():
      l = l.strip().lower()
      words.add(l)
  return words

def Main():
  letters = sys.argv[1]
  if len(letters) != 6:
    sys.exit('Syntax: <script> ABCDEFG')

  words = _LoadWords()

  for word in words:
    if len(word) != 6:
      continue
    for x in xrange(0, 4):
      if word[x] != letters[x]:
        continue
      for y in xrange(x+1, 5):
        if word[y] != letters[y]:
          continue
        for z in xrange(y+1, 6):
          if word[z] != letters[z]:
            continue
          print word
          indices = set(range(6))
          indices.remove(x)
          indices.remove(y)
          indices.remove(z)
          indices = sorted(list(indices))
          other = [' '] * 6
          other[x] = word[indices[0]]
          other[y] = word[indices[1]]
          other[z] = word[indices[2]]
          for i in indices:
            other[i] = letters[i]
          other = ''.join(other)
          if other not in words:
            continue
          
          print '%s -> %s: %s' % (word, other,
                  ''.join([word[x] for x in indices]))
              

if __name__ == '__main__':
  Main()
