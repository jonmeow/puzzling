#!/usr/bin/python3.7
# Ngram solver.  The Following __doc__ shows in the help text.
"""
Finds an ordering of the given ngrams that make a series of words.
If enumerations are given, they are used as constraints.
"""

# Keep examples separate from __doc__, so they can be last in the help text.
EXAMPLES = """
Examples:
$ ngrams.py ate thi st sis
[far too many to list here]

$ ngrams.py DIE EVE ODY RGO RYB SGA SKI YLE ES -l 9 4 8 5
['EVERYBODY DIES GARGOYLE SKIES']

$ ngrams.py -s DIE EVE ODY RGO RYB SGA SKI YLE ES -l 9 4 8
['EVERYBODY DIES GARGOYLE', 'EVERYBODY SKIS GARGOYLE']
"""

""" Developer specific examples:
$ ngrams.py -t this is a test -l 4 2 1 4
['THIS IS A TEST', 'THIS TS I SATE']
"""

# TODO Consider starting with searches for words of 9+ (10+) before running
# the full algorithm.  If any ngrams are found in all of the solutions and
# fully consumed, pull them out. Put them back at the front of the ngram list
# when we get to that enum. This probably won't matter unless we can pull
# 2+ ngrams (usually trigrams)
from dataclasses import dataclass
from pprint import PrettyPrinter
from textwrap import wrap
from typing import NamedTuple

import argparse, copy, random, sys

DEBUG = False
DICT_FILE = "/usr/share/dict/words"
HUGE_DICT_FILE = "/usr/share/dict/american-english-huge"
INSANE_DICT_FILE = "/usr/share/dict/american-english-insane"

@dataclass
class Dicts:
    words: set
    prefixes: set

@dataclass
class Preferences:
    # User settings
    allow_mid_ngram: bool = False
    dict_file: str = DICT_FILE
    print_as_you_go: bool = False

    # Internal settings
    ngram_separator: str = ""
    word_separator: str = " "

# More of a pain than it is worth?  Deep copies are needed.
@dataclass
class State:
    unused_ngrams: set
    unused_enums: set
    new_word: str = ""
    next_ngram: str = ""
    soln: str = ""

def pprint(stuff):
    """Prettier output. Mostly used for debugging."""
    PrettyPrinter(indent=2).pprint(stuff)


def _LoadWords(dict_file):
    """Returns a set of all the words in dict_file."""
    words = set(word.strip().upper().replace("'","") for word in open(dict_file))

    # Remove all single letter words except A, I, O. (O is used in older quotes)
    for c in 'BCDEFGHJKLMNPQRSTUVWXYZ':
        words.remove(c)

    return words

def _WordPrefixes(words):
    """Returns a set with all the strings that can become longer words."""
    word_prefixes =  set()
    for word in words:
        for i in range(len(word)-1):
          word_prefixes.add(word[:i+1])
    return word_prefixes


def _FindCommonNgrams(ngrams, solutions):
    pass


def _ExtractLongWords(ngrams, lengths, preferences, dicts):
    """Return dict{length, set of extracted ngrams}

       For each length of 10+ found in lengths, set aside any ngrams that must
       be used to construct a word of that length.
    """
    length_to_ngrams = {}
    for length in lengths:
        if length in length_to_ngrams:
            continue
            solutions = set()
            _FindEnumeratedSeq(new_word="", next_ngram="",
                               unused_enums=lengths, soln="",
                               preferences=preferences, dicts=dicts,
                               solutions=solutions)
            length_to_ngrams[length] = _FindCommonNgrams(ngrams, solutions)

    return length_to_ngrams


def _FindSequences(ngrams, lengths, preferences):

    words  = _LoadWords(preferences.dict_file)
    dicts = Dicts(words=words, prefixes=_WordPrefixes(words))

    solutions = set()

    if lengths:
        if preferences.allow_mid_ngram:
            _FindPossiblyOffsetSeq(ngrams, lengths, preferences, dicts,
                                   solutions)
        else:
            extracted_ngrams = _ExtractLongWords(ngrams, lengths,
                                                 preferences, dicts)
            _FindEnumeratedSeq(new_word="", next_ngram="", unused_ngrams=ngrams,
                               unused_enums=lengths, soln="",
                               preferences=preferences, dicts=dicts,
                               solutions=solutions)
    else:
        _FindSeq(new_word="", next_ngram="", unused_ngrams=ngrams, soln="",
                 preferences=preferences, dicts=dicts, solutions=solutions)
    return solutions

def _FindPossiblyOffsetSeq(ngrams, lengths, preferences, dicts, solutions):
    # Partial solution might start mid-ngram

    def _LongestNgram():
        return max(len(ngram) for ngram in ngrams)

    for c in range(_LongestNgram()):
        for ngram in ngrams:
            if len(ngram) < c:
                continue
            mod_ngrams = ngrams.copy()
            mod_ngrams.remove(ngram)
            mod_ngrams.add(ngram[c:])

            _FindEnumeratedSeq(new_word="", next_ngram="",
                               unused_ngrams=mod_ngrams,
                               unused_enums=lengths,
                               soln="",
                               preferences=preferences, dicts=dicts,
                               solutions=solutions)

def _FindEnumeratedSeq(new_word, next_ngram, unused_ngrams, unused_enums,
        soln, preferences, dicts, solutions):
    """Complete new_word using some/all of next_ngram and then continue
       finding a solution using all the unused_ngrams. All of next_ngram
       must be consumed before taking another unused_ngram.

       new_word:       the next word being constructed
       next_ngram:     the next ngram to use
       unused_ngrams:  a set of ngrams, all of which must be used
       unused_enums:   an ordered list of word length enumerations
       soln:           the solution string thus far

       words:          all the words in the dictionary
       word_prefixes:  all character strings that can be extended to make a word
    """
    if not unused_enums:
        solutions.add(soln[1:]) # Eliminate leading word separator
        if preferences.print_as_you_go:
            print(soln)
        return

    next_word_len = unused_enums[0] # convenience

    if next_ngram:
        if len(new_word) + len(next_ngram) < next_word_len:
            # Extend new_word by all of next_ngram
            if not new_word+next_ngram in dicts.prefixes:
                return
            new_word += preferences.ngram_separator + next_ngram
            _FindEnumeratedSeq(new_word, "", unused_ngrams, unused_enums, soln,
                               preferences, dicts, solutions)
        else:
            # Complete new_word with some or all of next_ngram
            n_letters = next_word_len - len(new_word)
            word = (new_word + preferences.ngram_separator 
                    + next_ngram[:n_letters])
            if not word in dicts.words:
                return
            _FindEnumeratedSeq("", next_ngram[n_letters:],
                               unused_ngrams, unused_enums[1:],
                               soln + preferences.word_separator + word, 
                               preferences, dicts, solutions)
    else:
        for ngram in unused_ngrams:
            ngrams = unused_ngrams.copy()
            ngrams.remove(ngram)
            _FindEnumeratedSeq(new_word, ngram, ngrams, unused_enums, soln,
                               preferences, dicts, solutions)


# This finds too many solutions.  Enumerations are usually necessary.
def _FindSeq(new_word, next_ngram, unused_ngrams, soln, preferences, dicts,
             solutions):
    """Complete new_word using some/all of next_ngram and then continue
       finding a solution using all the unused_ngrams. All of next_ngram
       must be consumed before taking another unused_ngram.

       new_word:       the next word being constructed
       next_ngram:     the next ngram to use
       unused_ngrams:  a set of ngrams, all of which must be used
       soln:           the solution string thus far

       words:          all the words in the dictionary
       word_prefixes:  all character strings that can be extended to make a word
    """
    if next_ngram:
        # Try to create a new _partial_ word by extending new_word by next_ngram
        if new_word + next_ngram in dicts.prefixes:
            _FindSeq(new_word + preferences.ngram_separator + next_ngram, 
                     "", unused_ngrams, soln, preferences, dicts, solutions)

        # Find a word made from new_word and some leading piece of next_ngram
        for i in range(len(next_ngram)):
            word = new_word + next_ngram[:i+1]
            if word in dicts.words:
                _FindSeq("", next_ngram[i+1:], unused_ngrams, 
                         soln + preferences.word_separator + word,
                         preferences, dicts, solutions)
        # Fail
        return

    if not unused_ngrams:
        if not new_word:
            solutions.add(soln[1:]) # Eliminate leading word separator
            if preferences.print_as_you_go:
                print("Solution:", soln)
        return

    for ngram in unused_ngrams:
        ngrams = unused_ngrams.copy()
        ngrams.remove(ngram)
        _FindSeq(new_word, ngram, ngrams, soln, preferences, dicts, solutions)


def _VerifyNgramAndEnumLengthsOrDie(ngrams, lengths, allow_shorter_lengths):
    if not lengths:
        return
    enum_total = sum(lengths)
    ngram_lengths = len("".join(ngrams))
    if enum_total > ngram_lengths:
        exit("Enum total %d, is greater than ngram lengths %d" %
             (enum_total, ngram_lengths))
    if enum_total < ngram_lengths and not allow_shorter_lengths:
        exit("Enum total %d, does not equal ngram lengths %d" %
             (enum_total, ngram_lengths))

def _CreateNgrams(text):
    ngrams = wrap("".join(text),3)
    random.shuffle(ngrams)
    return ngrams

def _ParseCommandLineArguments(argv):

    def _PrintHelpAndDie(error):
        print(error + "\n")
        parser.print_help()
        exit(1)

    parser = argparse.ArgumentParser(
        formatter_class = argparse.RawTextHelpFormatter,
        description = __doc__,
        epilog = EXAMPLES)

    parser.add_argument("ngrams", nargs='*',
        help="A space separated list of ngrams. e.g. abc dsf asd")

    parser.add_argument("--lengths", "-l", nargs='*', type=int,
        help="A space separated list of enumeration lengths, e.g. 3 6."
             "\nFor apostrophes, merge the two elements. e.g. 5'1 -> 6")

    parser.add_argument("--subset", "-s", action="store_true",
        help="Allow sum(enumerations) < sum(ngram lengths)."
             "\nPartial solutions will start at the beginning of"
             "\nan ngram unless --allow_mid_ngram (-m) is used.")

    parser.add_argument("--allow_mid_ngram", "-m", action="store_true",
        help="Allow the solution to start mid-ngram."
             "\nImplies --subset (-s)."
             "\nThis is (# ngrams * len(ngram)-1) times slower.")

    parser.add_argument("--allow_rare_words", "-r", action="store_true",
        help="Allow rarer words in the solution (bigger dictionary)."
             "\nThis overrides --dict_file")

    parser.add_argument("--dict_file", "-d", default=DICT_FILE,
        help="Dictionary to use. Default: %s" % DICT_FILE)

    parser.add_argument("--print_as_you_go", "-p", action="store_true",
        help="Print solutions as they are found (can be noisy).")

    parser.add_argument("--test_msg", "-t", nargs='*',
        help="Testing: Make trigrams of this string; randomize order."
             "\nThis overrides any ngrams entered.")

    if len(argv) < 2:
      _PrintHelpAndDie("Let me tell you about the arguments ...")

    args = parser.parse_args()

    if not args.ngrams and not args.test_msg:
        exit("Did you forget the letter sequence")

    if args.subset and not args.lengths:
        exit("Subset searches are only implemented if lengths are given.")

    if args.allow_mid_ngram:
      args.subset = True

    if args.allow_rare_words:
        args.dict_file = INSANE_DICT_FILE

    return args


def Main():
    args = _ParseCommandLineArguments(sys.argv)

    # Determine which input ngrams to use (input or test)
    ngram = args.ngrams if not args.test_msg else _CreateNgrams(args.test_msg)
    ngram_set = [x.upper() for x in ngram]

    print("input:", ngram, "enumerations:", args.lengths)

    # Verify lengths after showing input so users can see what doesn't match.
    _VerifyNgramAndEnumLengthsOrDie(ngram_set, args.lengths, args.subset)

    if args.allow_rare_words:
        print("Using insane size dictionary.")

    if not args.lengths:
        print("For anything non-trivial, there can be gigs of solutions."
              "Use enumerations.")

    preferences = Preferences(
                     allow_mid_ngram = args.allow_mid_ngram,
                     dict_file = args.dict_file,
                     print_as_you_go = args.print_as_you_go)

    solutions = _FindSequences(ngram_set, args.lengths, preferences)

    if not solutions and not(args.dict_file == INSANE_DICT_FILE):
        print("No solution found. Retrying with insane size dictionary.")
        preferences.dict_file = INSANE_DICT_FILE
        solutions = _FindSequences(ngram_set, args.lengths, preferences)

    if not args.print_as_you_go:
        print("Solutions:")
        pprint(sorted(sorted(solutions), key=len)) # shortest -> fewest words'

    return

if __name__ == '__main__':
  Main()
