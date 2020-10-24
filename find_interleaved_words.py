#! /usr/bin/python
import os
import pprint
import sys
from collections import defaultdict
from collections import Counter

#DICT_FILE = "/usr/share/dict/words"
#DICT_FILE = "/usr/share/dict/american-english-huge"
DICT_FILE = "/usr/share/dict/american-english-insane"

def load_words_from(dict_file):
    known_words =  defaultdict(list)
    with open(dict_file) as f:
        for line in f:
            word = line.strip().lower()
            known_words[len(word)].append(word)
    return known_words


def interleaved_words_by_len(dictionary, string_to_search, substring_lengths):
  """Returns {length, set(matching words of length)}"""
  interleaved_words_by_len = {}
  for l in substring_lengths:
    if not l in interleaved_words_by_len:
      interleaved_words_by_len[l] = interleaved_words(dictionary[l], 
                                                      string_to_search)
  return interleaved_words_by_len

def interleaved_words(dictionary, string):
  """Returns the set words in dictionary that, when considered in isolation, 
     can be de-interleaved from string."""
  matching_words = set()
  for word in dictionary:
    if checkword(string, word):
      matching_words.add(word)
  return matching_words

def checkword(string, word):
  """Returns true if word, is interleaved in string."""
  max_len = len(string)
  i=0
  for c in word:
    while i < max_len:
      i = i+1
      if c == string[i-1]:
        break 
    else:
      return False
  return True


def valid_word_sets_by_letter_count(words_by_length, string_to_search, 
                                    substring_lengths):
  """Returns dict{used_letters, set(words), where string_to_search contains 
     the letters necessary to interleave all of set(words).  
     The check whether there are valid interleaves is NOT done."""
  letter_counts = Counter(string_to_search)
  return _valid_word_sets_by_letter_count(words_by_length, letter_counts, 
                                          substring_lengths)

def _valid_word_sets_by_letter_count(words_by_length, remaining_letters, 
                                     substring_lengths, first_word=None):
  # Avoid duplicate results, e.g. [A,B] and [B,A]
  #   Assumption: substring_lengths is sorted (longest first)
  #   Assumption: words lists in words_by_length are sorted (not needed?)
  #   Solution: Only accept a word of similar length if it is equal or later
  #             in the alphabet than the word higher in the recursion tree
  results = [] if len(substring_lengths) == 1 else {}

  for word in words_by_length[substring_lengths[0]]:
    if word < first_word:
      continue

    letters_in_word = Counter(word)
    if letters_in_word - remaining_letters:
      continue

    if len(substring_lengths) == 1:
        results.append(word)
    else:
      r = _valid_word_sets_by_letter_count( 
            words_by_length, 
            remaining_letters - letters_in_word, 
            substring_lengths[1:],
            word if substring_lengths[0] == substring_lengths[1] else None)
      if r:
        results[word] = r

  if len(substring_lengths) == 1:
    results.sort()

  return results


def main():
  """
Usage: %s <stringToSearch> <substringLengths>...

  Example: %s ieaqorbscuitguouilsstatehcteraeelles 11 9 6 5 5

  If you need a bigger dictionary, uncomment the appropriate line in the code
  """
  def usage():
    scriptname = os.path.basename(sys.argv[0])
    print main.__doc__ % (scriptname, scriptname)
    exit(1)
 
  if len(sys.argv) < 3:
    usage()

  string_to_search = sys.argv[1].lower()
  substring_lengths_as_chars = sys.argv[2:]

  # Convert substring lengths to ints
  substring_lengths = []
  try:
    substring_lengths = [int(x) for x in substring_lengths_as_chars]
    total_substring_lengths = sum(substring_lengths)
  except ValueError as verr:
    print verr
    usage()

  # Verify args
  if total_substring_lengths < 2:
    print "Error: Requested substring length(%d) must >= 2" \
          % (find_interleaved_substring_of_length)
    usage()
  elif total_substring_lengths > len(string_to_search):
    print "Error: Requested substring lengths(%d) is longer than the input string(%d)" \
          % (total_substring_lengths, len(string_to_search))
    usage()

  # Cache dictionary
  dictionary = load_words_from(DICT_FILE)
  words_by_length = interleaved_words_by_len(dictionary, string_to_search, 
                                             substring_lengths)

  # Exection is much faster if the longer words are handled first
  substring_lengths.sort()
  substring_lengths.reverse()
  word_sets_by_letter_count = valid_word_sets_by_letter_count(
      words_by_length, string_to_search, substring_lengths)

  pprint.PrettyPrinter(indent=2).pprint(word_sets_by_letter_count)


if __name__ == '__main__':
  main()
