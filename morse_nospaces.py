#!/usr/bin/python
# The core of this code was found on stack overflow by David Cain 21 Mar 2014 
# Extended to: 
#    Handle command line input (vs in code string entry)
#    Output all solutions of min length by default (vs the single shortest)
#    Output all solutions of up to a given word count length
#    Filter results to only include commonly used words (vs. whole dictionary)
#    Use extremely long and verbose and long variable and method names 

from pprint import PrettyPrinter
import argparse, heapq, re, sys

# From: http://norvig.com/ngrams/count_1w.txt
DICT_BY_FREQ_FILE = "./google-books-common-words.txt"

DICT_FILE = "/usr/share/dict/words"
#DICT_FILE = "/usr/share/dict/american-english-huge"
#DICT_FILE = "/usr/share/dict/american-english-insane"

# Create dict ({'A': '.-', ...}
MORSE = dict(zip('ABCDEFGHIJKLMNOPQRSTUVWXYZ', [
    '.-', '-...', '-.-.', '-..', '.', '..-.', '--.', '....',
    '..', '.---', '-.-', '.-..', '--', '-.', '---', '.--.',
    '--.-', '.-.', '...', '-', '..-', '...-', '.--', '-..-',
    '-.--', '--..'
]))


####################################
# Methods for testing
def _ToMorseNoSpaces(msg):
    """Turn a message into timing-less morse code."""
    return "".join("".join(MORSE[c] for c in word) 
                   for word in msg.upper().split(' '))
####################################

def pprint(stuff):
    """Prettier output. Mostly used for debugging."""
    PrettyPrinter(indent=2).pprint(stuff)


def _LoadWords(dict_file):
    """Returns a set of all the words in the dict file."""
    words = set(word.strip().upper() for word in open(dict_file))

    # Remove all single letter words except A, I.
    for c in 'BCDEFGHJKLMNOPQRSTUVWXYZ':
        words.remove(c) 

    return words


def _LoadFreqWords(dict_file):
    """Returns a set of all the words in the dict file."""
    freq_map = {}
    for line in open(dict_file):
        word, freq = line.strip().split('\t')
        try:
            freq_map[word] = int(freq)
        except ValueError as verr:
            print "Non-integer frequency(%s) for word(%s) in file(%s)" \
                  % (freq, word, dict_file)

    return freq_map


def _AllStringsThatBecomeWords(words):
    """Returns a set of all strings that are a prefix for a word in words.

    e.g. the strings added for the word skill are: s, sk, ski, skil.
    """
    return set(word[:i+1] for word in words for i in xrange(len(word)))


def _CharacterTransitionMap(morse_msg):
    """Construct a map of possible char transitions.

    Return [{char starting there, index of start of next char}]
    e.g. '..' becomes [{'I': 2, 'E': 1}, {'E': 2}]
    """
    result = [{} for i in xrange(len(morse_msg))]
    for i in xrange(len(morse_msg)):
        for c, m in MORSE.iteritems():
            if morse_msg[i:i+len(m)] == m: 
              result[i][c] = i + len(m)
    return result


def _GenerateWords(words, prefixes, ctm, i, prefix=''):
    """Generate all possible words starting with prefix, and continuing from
    from position i in the char transition map (ctm).
    """
    if prefix in words:
        yield prefix, i
    if i == len(ctm): 
        return
    for c, j in ctm[i].iteritems():
        if prefix + c in prefixes:
            for w, j2 in _GenerateWords(words, prefixes, ctm, j, prefix + c):
                yield w, j2


def _WordTransitionMap(words, prefixes, morse_msg):
    """Construct a map of possible word transitions.

    Returns [{next_index: [words_ending_at_next_index-1]}]
    If no words start at next_index, no entry is created for key next_index.
    """

    # MorseChar[{char starting there, index of start of next char}]
    ctm = _CharacterTransitionMap(morse_msg)

    result = [{} for i in xrange(len(ctm))]
    for i_ in xrange(len(ctm)):
        i = len(ctm) - i_ - 1
        for w, j in _GenerateWords(words, prefixes, ctm, i):
            if j < len(result) and not result[j]:
                continue
            if j in result[i]:
                result[i][j].append(w)
            else:
                result[i][j] = [w]
    return result


def _nSentencesInWordMap(wtm):
    """Return the number of valid word sequence in wtm"""
    result = [0] * len(wtm) + [1]
    for i_ in xrange(len(wtm)):
        i = len(wtm) - i_ - 1
        for j in wtm[i].iterkeys():
            result[i] += result[j]
    return result[0]


def _nWordsInShortestSentence(wtm):
    """Return the length of the shortest sentence that solves the morse code"""

    min_to_index = [0] + [sys.maxsize] * len(wtm)

    for i in xrange(len(wtm)):
        for end_index, _ in wtm[i].iteritems():
            if min_to_index[end_index] > min_to_index[i] + 1:
                min_to_index[end_index] = min_to_index[i] + 1

    length = min_to_index[len(wtm)]
    return length if length != sys.maxsize else 0


def _SolutionsOfLength(num_words, words_by_freq, wtm, wtm_index=0):
    """Return all solutions in <wtm> of <num_words>, starting from <wtm_index>.
    """

    def _SortWordsByFreq(words_by_freq, words):
        def _Freq(word):
            return words_by_freq.get(word) or 0
        return sorted(words, key=_Freq, reverse=True)

    if num_words == 0 or wtm_index == len(wtm):
        return []

    results = [] 

    # Prefer solutions that consume more more chars at a time
    # -- This may be unecessary with "Most Likely Solutions"
    for end_index, words in reversed(sorted(wtm[wtm_index].items())):
        if end_index == len(wtm) and num_words == 1:
            results.append("%s" % _SortWordsByFreq(words_by_freq, words))
            continue

        for r in _SolutionsOfLength(num_words-1, words_by_freq, wtm, end_index):
            results.append("%s %s" % (_SortWordsByFreq(words_by_freq, words), r))
            # The following nested array structure, while nicer is 8x slower.
            # results.append([_SortWordsByFreq(words_by_freq, words), r])

    return results


def _MostLikelySolutions(sentences, number_to_print, words_by_freq):
    """Return the top <number_to_print solutions>, scored as the
       multiplicitive sum of word_freq(word in sentence).

       First pass impl: Return at most 1 sentence per complex sentence.

       Sample input line: ['NUMBERED'] ['IDS', 'INES', 'ERSE'] ['SOLUTION']
    """
    results = {}
    for complex_sentence in sentences:
        score = 1
        simple_sentence = ""
        for word_choice_set in complex_sentence[1:-1].split("] ["):
            # Words in each choice set are already sorted by frequency
            best_word = word_choice_set.split(", ")[0][1:-1]
            score *= words_by_freq.get(best_word) or 0 
            simple_sentence += best_word + " "
        results[simple_sentence.strip()] = score
    return heapq.nlargest(number_to_print, results, key=results.get)


def _ComplexSentenceAsFlatList(complex_sentence, prefix=""):
    """Expand complex_sentence into a flat list of strings

       e.g. ['NUMBERED'] ['IDS', 'INES'] ['SOLUTION']
       to ['NUMBERED ID SOLUTION', 'NUMBERED INES SOLUTION']
    """
    results = []

    next_start = complex_sentence[1:].find('[')
    if next_start == -1:
        if complex_sentence[0] == '[':
          results.append("%s" % (prefix + complex_sentence[1:-1]))
        else:
          results.append("%s" % (prefix + complex_sentence))
        return results

    choice_set = complex_sentence[:next_start]
    rest = complex_sentence[next_start+1:]

    for choice in choice_set[1:-1].split(", "):
        results.extend(_ComplexSentenceAsFlatList(rest, prefix+choice+" "))
    return results


def _PrintAllSolutions(solutions, print_as_flat_list=False):
    for s in solutions:
        s = s.replace("'","")
        if print_as_flat_list:
            pprint(_ComplexSentenceAsFlatList(s))
            print ""
        else:
            print "  " + s


def _ParseCommandLineArguments(argv):

    def _PrintHelpAndDie(error):
        print error + "\n"
        parser.print_help()
        exit(1)

    parser = argparse.ArgumentParser(
        prefix_chars='+',
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
        description="Takes a string of spaceless morse code and outputs"
                    " possible translations.\nArguments start with '+',"
                    " so the morse code can start with a '-'\n")

    parser.add_argument("morse", nargs='*',
        help="Morse code. Any spacing is ignored.")

    parser.add_argument("++allow_rare_words", "+r", action="store_true", 
        help="Allow rarer words in the solution.")

    parser.add_argument("++list", "+l", action="store_true",
        help="Print all solutions as a flat list (slow if max>6).")

    parser.add_argument("++max", "+m", type=int, default=0,
        help="Max # of words in solution. [0: Min # of word solutions]")

    parser.add_argument("++dict_file", "+d", default=DICT_FILE,
        help="Dictionary to use")

    parser.add_argument("++freq_file", "+f", default=DICT_BY_FREQ_FILE,
        help="Word Frequency file to use line format:word\tfreq")

    parser.add_argument("++test_msg", "+t",
        help="Text input that becomes spaceless morse."
             " It overrides the morse entered (still required though).")

    if len(argv) < 2:
      _PrintHelpAndDie("Let me tell you about the arguments ...")

    args = parser.parse_args()

    # Validate Morse  (Creating a custom validator seems overkill)
    if not args.morse:
        _PrintHelpAndDie("Did you forget the morse code?")
    args.morse = "".join(args.morse)
    non_morse_chars = re.sub("[-.]*", "", args.morse)
    if non_morse_chars and not args.test_msg:
        _PrintHelpAndDie("Morse string is bad: " + args.morse)

    return args


def Main():
    """Takes a string of morse code and outputs possible translations."""

    args = _ParseCommandLineArguments(sys.argv)
    morse_msg = _ToMorseNoSpaces(args.test_msg) if args.test_msg else args.morse
    max_solution_len = args.max

    dict_file = args.dict_file
    freq_file = args.freq_file
    use_full_dict = args.allow_rare_words

    print_as_flat_list = args.list

    words_by_freq = _LoadFreqWords(freq_file)
    words = _LoadWords(dict_file) 
    if not use_full_dict:
        words = set.intersection(words, words_by_freq.keys())
    prefixes = _AllStringsThatBecomeWords(words)
  
    print "input:", morse_msg 
    if use_full_dict:
        print "Using the full dictionary ('rare' words)."

    # MorseCharacter[{next_index: [words_ending_at_next_index-1]}]
    word_transition_map = _WordTransitionMap(words, prefixes, morse_msg)
  
    min_sentence_len = _nWordsInShortestSentence(word_transition_map)
    print "Shortest sentence length (%d); Number of possible sentences (%d) " \
         % (min_sentence_len, _nSentencesInWordMap(word_transition_map))

    # Print solutions for each length as we go. 7+ word solutions are slow
    if not max_solution_len:
        max_solution_len = min_sentence_len

    for i in xrange(min_sentence_len, max_solution_len+1):
        print "\nSolutions of length %d" % i
        solutions = _SolutionsOfLength(i, words_by_freq, word_transition_map)

        print " -- Most likely solutions\n  ",
        pprint(_MostLikelySolutions(solutions, 10, words_by_freq))

        print "\n -- All solutions"
        _PrintAllSolutions(solutions, print_as_flat_list)
  
if __name__ == '__main__':
    Main()
