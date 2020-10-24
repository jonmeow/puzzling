#!/usr/bin/python3
"""
Prints all legal orderings of the rows so that the requested word
can be read vertically in the resulting output.

Assumes all rows are the same length.
"""

# Keep examples separate from __doc__, so they can be last in the help text.
EXAMPLES="""
Example: <script> -f rows.txt cat
  SFCSLFCLG
  XJNYJFAFD
  NSFNODTIE

Example: <script> -s -f rows.txt cat
  SFCSLFCLG
  XJNYJFAFD
  NSFNODTIE

      SFCSLFCLG
  XJNYJFAFD
  NSFNODTIE
"""
import argparse
import os
import sys
from pprint import PrettyPrinter


def pprintOnePerLine(content):
  PrettyPrinter(indent=2, width=1).pprint(content)

def load_rows_from(row_file):
  try:
    return [line.upper().strip() for line in open(row_file)]
  except FileNotFoundError as e:
    exit(e)


def printAlignmentVariations(word, rows_to_align, aligned_rows):
  if not rows_to_align:
    PrettyPrinter(indent=2, width=30).pprint(aligned_rows)
    print("")
    return

  # Indent enough to allow the first character of one line to
  # be above the last character of another line.
  line = rows_to_align[0]
  line_length = len(line)

  for i in range(line_length):
    if word[0] == line[i]:
      indent = ' ' * (line_length-i)
      printAlignmentVariations(word[1:], 
                               rows_to_align[1:], 
                               aligned_rows + [indent + line])

def printGridAlignedByWord(word, solution, unused_rows=None):
  print("solution")
  pprintOnePerLine(solution)

  if unused_rows:
    print("unused rows")
    pprintOnePerLine(unused_rows)
  print("")


def findGrids(orig_word, word, unused_rows, solution):
  if not word:
    printGridAlignedByWord(orig_word, solution, unused_rows)
    print("Alignment variations")
    printAlignmentVariations(orig_word, solution, [])
    return

  for i, row in enumerate(unused_rows):
     if word[0] in row:
       findGrids(orig_word, 
                 word[1:], 
                 unused_rows[:i] + unused_rows[i+1:], 
                 solution + [row])


def findAlignedGridAt(offset, orig_word, word, unused_rows, solution):
  if not word:
    printGridAlignedByWord(orig_word, solution, unused_rows)
    return
  for i, row in enumerate(unused_rows):
     if word[0] == row[offset]:           # TODO - force alignment
       findAlignedGridAt(offset, 
                         orig_word, 
                         word[1:], 
                         unused_rows[:i] + unused_rows[i+1:], 
                         solution + [row])

def findAlignedGrids(word, unused_rows):
  # Assuming all rows are the same length
  for i in range(len(unused_rows[0])):
    findAlignedGridAt(i, word, word, unused_rows, [])


def printSolutions(word, rows, allow_shifting):
  if allow_shifting:
    findGrids(word, word, rows, [])
  else:
    findAlignedGrids(word, rows)


def _ParseCommandLineArguments(argv):

    def _PrintHelpAndDie(error):
        print(error + "\n")
        parser.print_help()
        exit(1)

    parser = argparse.ArgumentParser(
        formatter_class = argparse.RawTextHelpFormatter,
        description = __doc__,
        epilog = EXAMPLES)

    parser.add_argument("word", nargs='*',
        help="The word to try and find vertically across the rows.")

    parser.add_argument("--file", "-f", 
        help="Name of File with the rows")

    parser.add_argument("--allow_shifting", "-s", action="store_true",
        help="Allow shifting rows horizontally.")

    if len(argv) < 3:
      _PrintHelpAndDie("Insufficient arguments")

    args = parser.parse_args()

    if not args.word:
      exit("Please specify the word to find.")
    args.word = args.word[0].upper()

    if not args.file:
      exit("Please specify the file with the rows.")

    return args

def main():
  args = _ParseCommandLineArguments(sys.argv)

  row_file = args.file
  word = args.word
  allow_shifting = args.allow_shifting

  rows = load_rows_from(row_file)
  if len(word) > len(rows):
    exit("Word length(%s) exceeds row length(%s)" % (len(word), len(rows)))

  printSolutions(word, rows, allow_shifting) 

if __name__ == '__main__':
  main()
