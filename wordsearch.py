#!/usr/bin/python

# Assumption: Grid is rectangular (or filled to be rectangular)
DATA=\
[
"SNTIERSRSAWBHISF",
"SOAIKEIYITIRNDIO",
"IVNNAIEMEAIAKEER",
"AEGDDNRMRNIVLIRG",
"LMOIEDRERGAOINRE",
"FBKALIACAOLEMDAT",
"AEINTADHIAFNAIOI",
"VREMABEORGAOLAFT",
"SNTIERSRSAWBHISF",
"SOAIKEIYITIRNDIO",
"IVNNAIEMEAIAKEER",
"AEGDDNRMRNIVLIRG",
"LMOIEDRERGAOINRE",
"FBKALIACAOLEMDAT",
"AEINTADHIAFNAIOI",
"VREMABEORGAOLAFT"
]

import os
import sys

#DICT_FILE = "/usr/share/dict/words"
#DICT_FILE = "/usr/share/dict/american-english-huge"
DICT_FILE = "/usr/share/dict/american-english-insane"

def _LoadWordsFromDictFile(dict_file):
  return set(word.strip().lower() for word in open(dict_file).readlines())


def _PrintIfWordEitherDirection(direction, rev_direction, word, row, col, words):
    if word.lower() in words:
      print '%s at %02i, %02i, %s' % (word, row, col, direction)

    reversed_word = word[::-1]
    if reversed_word.lower() in words:
      # Give human friendly coordinates for reversed words
      word_len = len(word)
      if direction == "across":
        col = col + word_len - 1
      else:
        row = row + word_len - 1
        if direction == "down right":
          col = col + (word_len - 1)
        elif direction == "down left":
          col = col - (word_len -1)
      print '%s at %02i, %02i, %s' % (reversed_word, row, col, rev_direction)


def _PrintWordsInGrid(words, grid, nrows, ncols, min_len):

  def _Check(direction, rev_direction, word):
    _PrintIfWordEitherDirection(direction, rev_direction, word, row, col, words)

  # When searching check A and reverse(A) at the same time 
  max_dimension = max(nrows, ncols)
  for strlen in range(min_len, max_dimension):
    for row in xrange(nrows):
      for col in xrange(ncols):

        # Check horizontal
        if col + strlen <= ncols:
          _Check("across", "left", grid[row][col:col+strlen])

        # If there are not enough rows, rule out all down combinations
        if row + strlen > nrows:
          continue

        _Check("down", "up", "".join([grid[row+i][col] for i in range(strlen)]))

        if col + strlen <= ncols:
          _Check("down right", "up left",
                 "".join([grid[row+i][col+i] for i in range(strlen)]))

        if col + 1 >= strlen:
          _Check("down left", "up right",
                 "".join([grid[row+i][col-i] for i in range(strlen)]))
          
def Main():
  """
Usage: script <min_string_length>

Searches the grid for all words of length min_string_length or longer.
Output coordinates use 0,0 at the top left.

The grid to search needs to be entered in this script file.
  """
  if len(sys.argv) != 2:
    sys.exit(Main.__doc__)
  try:
    min_len = int(sys.argv[1])
  except ValueError as verr:
    print verr
    sys.exit(Main.__doc__)

  nrows=len(DATA)
  ncols=len(DATA[1])

  max_dimension = max(nrows, ncols)
  if (min_len > max_dimension):
    sys.exit('Minimum word length specified(%i) exceeds both row(%i)'
             ' and column(%i) size.' % (min_len, nrows, ncols))

  words = _LoadWordsFromDictFile(DICT_FILE)
  _PrintWordsInGrid(words, DATA, nrows, ncols, min_len)


if __name__ == '__main__':
  Main()
