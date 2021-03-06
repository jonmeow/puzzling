#!/usr/bin/python3
# Usage: script [-l <min_string_length>] 
#               [-d dict_file] 
#               [-p] # print the input grid
#               [-r] # use insane dict
#               [-s first_row_number] # output coords sn spreadsheet format
#               <grid_file> 
"""
Searches the grid for all words of length min_string_length or longer.
Output coordinates use 0,0 at the top left.

The grid file format is:
ABCDEFG
HIGHEED
...
The grid is assumed to be rectangular.
Any non-alphanumeric characters will be stripped. (So A B C is fine.)
"""

import argparse
import os
import sys
from pprint import PrettyPrinter

#DICT_FILE = "/usr/share/dict/words"
HUGE_DICT_FILE = "/usr/share/dict/american-english-huge"
RARE_DICT_FILE = "/usr/share/dict/american-english-insane"

def _LoadGridFromFile(f):
  """Returns an array of the contents of the file."""
  try:
    return ["".join(filter(str.isalnum,line.upper())) for line in open(f)]
  except FileNotFoundError as e:
    exit(e)


def _LoadWordsFromDictFile(dict_file):
  return set(word.strip().upper() for word in open(dict_file).readlines())


def _FindWordsInGrid(words, grid, nrows, ncols, min_len):
  words_found = list()

  def _SaveIfWord(direction, word):
    if word in words:
      words_found.append((word, row, col, direction))

  def _Reverse(word):
    return word[::-1]

  def _CanGoRight():
    return col + strlen <= ncols

  def _CanGoLeft():
    return col >= strlen-1

  def _CanGoUp():
    return row >= strlen-1

  def _CanGoDown():
    return row + strlen <= nrows

  # The output is easier to use if it is sorted by wordlen and then row, col.
  #
  # Being efficent and checkng A and reverse(A) at the same time, means
  # saving all the results and resorting them prior to printing.  I'm lazy.
  #
  max_dimension = max(nrows, ncols)
  for strlen in range(min_len, max_dimension):
    for row in range(nrows):
      for col in range(ncols):

        # This ordering is for the ease of human parsing, not efficiency
        if _CanGoRight():
          _SaveIfWord("R", grid[row][col:col+strlen])

        if _CanGoLeft():
          _SaveIfWord("L", _Reverse(grid[row][col-strlen+1:col+1]))

        if _CanGoDown():
          _SaveIfWord("D", "".join([grid[row+i][col] for i in range(strlen)]))

          if _CanGoRight():
            _SaveIfWord("DR",
                         "".join([grid[row+i][col+i] for i in range(strlen)]))

          if _CanGoLeft():
            _SaveIfWord("DL",
                         "".join([grid[row+i][col-i] for i in range(strlen)]))

        if _CanGoUp():
          _SaveIfWord("U", "".join([grid[row-i][col] for i in range(strlen)]))

          if _CanGoRight():
            _SaveIfWord("UR",
                         "".join([grid[row-i][col+i] for i in range(strlen)]))

          if _CanGoLeft():
            _SaveIfWord("UL",
                         "".join([grid[row-i][col-i] for i in range(strlen)]))

  return words_found

          
def _ParseCommandLineArguments(argv):

    def _PrintHelpAndDie(error):
        print(error + "\n")
        parser.print_help()
        exit(1)

    parser = argparse.ArgumentParser(
        formatter_class = argparse.RawTextHelpFormatter,
        description = __doc__)

    parser.add_argument("grid_file", nargs=1,
        help="The file containing the grid to search.")

    parser.add_argument("-l", "--min_length", type=int, default=4,
        help="The minimum length of word to find. Default 4.\n ")
        # The trailing "\n " creates a separator in the help output

    parser.add_argument("-d", "--dict_file", default=HUGE_DICT_FILE, 
        metavar="file", help="Dictionary to use.\nDefault: %s" % HUGE_DICT_FILE)

    parser.add_argument("-r", "--find_rare_words", action="store_true",
        help="Find rarer words in the solution (bigger dictionary)."
             "\nThis overrides --dict_file\n ")

    parser.add_argument("-p", "--print_grid", action="store_true",
        help="Print the grid to be searched.")

    parser.add_argument("-s", "--spreadsheet_numbering", nargs=2, metavar="s",
        help="Print the found coords as row(#), col(letter)."
             "\nstarting the row and letter given, e.g. -s 1 A.")

    args = parser.parse_args()
    if args.find_rare_words:
      args.dict_file = RARE_DICT_FILE

    if not args.spreadsheet_numbering:
      args.spreadsheet_numbering = [0,0]

    return args

def  _PrintWordsFound(words_found, top_left_row_number, top_left_col_letter):
  """If top_left entries are specified, use spreadsheet coords, e.g. 1A.
     If the letter gets past Z, start over at AA.
     If the letter goes past AZ, print crap.
  """
  if not (top_left_row_number or top_left_col_letter):
    for word, row, col, dir in words_found:
      print('%s at %02i, %02i, %s' % (word, row, col, dir))
    return

  def _ModRow(r):
    return r + int(top_left_row_number)

  def _ModCol(c):
    new_ord = ord(top_left_col_letter) + c
    if new_ord <= ord('Z'):
      return chr(new_ord)
    return "A" + chr(new_ord-26)

  for word, row, col, dir in words_found:
    print('%s at %02i, %2s, %s' % (word, _ModRow(row), _ModCol(col), dir))


def Main():
  args = _ParseCommandLineArguments(sys.argv)
  min_len = args.min_length
  dict_file = args.dict_file
  grid_file = args.grid_file[0]
  print_grid_file = args.print_grid
  top_left_row_number = args.spreadsheet_numbering[0]
  top_left_col_letter = args.spreadsheet_numbering[1]

  grid = _LoadGridFromFile(grid_file)
  if print_grid_file:
    PrettyPrinter(indent=2).pprint(grid)

  nrows=len(grid)
  ncols=len(grid[1])
  max_dimension = max(nrows, ncols)
  if (min_len > max_dimension):
    sys.exit('Minimum word length specified(%i) exceeds both row(%i)'
             ' and column(%i) size.' % (min_len, nrows, ncols))

  words = _LoadWordsFromDictFile(dict_file)

  words_found = _FindWordsInGrid(words, grid, nrows, ncols, min_len)
  _PrintWordsFound(words_found, top_left_row_number, top_left_col_letter)


if __name__ == '__main__':
  Main()
