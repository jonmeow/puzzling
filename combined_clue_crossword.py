#!/usr/bin/python
#
# A crossword where each clue is split in two, added into values.
#   CLUES - Clue numbers.  Note that [1,2,3] can be abbreviated range(1,4).
#   GRID - The sum values in the grid.
#   SOLVED - Tuples of solved (grid, clue1, clue2) values.


import decimal
import textwrap

CLUES = (
  [11,16,19,20,22,23,25,26,27,30,33,34,35] +
  range(38,49) +
  range(50,65) +
  range(66,87) +
  [88] +
  range(90,95) +
  [96,97] +
  range(99,103) +
  range(104,112) +
  range(113,118) +
  [119,120] +
  range(124,128) +
  [130,131] +
  range(134,141))

GRID = [
  129,167,78,157,202,242,242,202,236,
  128,31,
  130,150,
  96,
  207,244,189,
  216,
  265,208,234,164,
  101,
  150,110,110,80,265,105,
  85,169,150,
  69,165,174,120,
  161,
  144,
  113,100,170,170,120,184,70,135,
  180,173,
  176,118]

SOLVED = [
  (70, 23, 47),  # Not in
  (173, 71, 102),
  (31, 11, 20),
  (128, 44, 84),
  (69, 26, 43),
  (78, 30, 48),
  (85, 19, 66),
  (100, 33, 67),
  (105, 45, 60),
  (110, 16, 94),
  (110, 38, 72),
  (113, 39, 74),
  (120, 52, 68),
  (120, 50, 70),
  (129, 22, 107),
  (135, 56, 79),
  (144, 62, 82),
  (165, 25, 140),
  (169, 64, 105),
  (174, 35, 139),
  (176, 63, 113),
  (180, 46, 134),
  (184, 78, 106),
  (189, 85, 104),
  (202, 88, 114),
  (216, 101, 115),
  (234, 97, 137),
  (244, 120, 124),
]


def Validate():
  assert len(CLUES) == len(set(CLUES))
  assert len(CLUES) % 2 == 0
  assert len(CLUES) == 2*len(GRID)
  assert sum(CLUES) == sum(GRID), 'Clues sum: %s; grid sum: %s; diff: %s' % (
    sum(CLUES), sum(GRID), sum(CLUES)-sum(GRID))


def ApplySolved():
  for entry, x, y in SOLVED:
    assert x+y == entry, entry
    GRID.remove(entry)
    CLUES.remove(x)
    CLUES.remove(y)


def GetPossibles():
  possibles = []

  clues = sorted(CLUES)
  for entry in GRID:
    poss = []
    half = entry/2
    for x in clues:
      if x > half:
        break
      y = entry - x
      if x == y:
        break
      if y not in clues:
        continue
      poss.append(x)
    possibles.append((len(poss), entry, poss))
  return sorted(possibles)


def FilterPossibles(possibles, x, y):
  new_possibles = []
  for _, entry, items in possibles:
    n = []
    for i in items:
      j = entry-i
      if i == x or i == y or j == x or j == y:
        continue
      n.append(i)
    if not n:
      return None
    new_possibles.append((len(n), entry, n))
  return sorted(new_possibles)


def ApplyUniquePossibles(possibles):
  new_possibles = []

  while possibles:
    n, entry, items = possibles.pop()
    # If an item has one answer, it's obviously unique.  However, if it has two
    # answers and appears twice, it's still unique.
    if n <= GRID.count(entry):
      possibles = FilterPossibles(possibles, items[0], entry-items[0])
      new_possibles.append((n, entry, (items[0],)))
    else:
      new_possibles.append((n, entry, items))

  return new_possibles


def AccumulateSolutions(possibles, pairs, solutions):
  if not possibles:
    for entry, x in pairs:
      solutions[entry].add(x)
    return

  _, entry, items = possibles[0]
  rem_poss = possibles[1:]

  for x in items:
    y = entry-x
    new_poss = FilterPossibles(rem_poss, x, y)
    if new_poss is None:
      continue
    AccumulateSolutions(
      new_poss, pairs + ((entry, (x, y)),), solutions)


def PrintHeader(str):
  print '#' * 80
  print '#', str
  print '#' * 80


def PrintSolutions(solutions):
  options = {}
  for key, sol in solutions.iteritems():
    if len(sol) not in options:
      options[len(sol)] = []
    options[len(sol)].append((key, sol))

  for l in reversed(sorted(options.keys())):
    print
    print '%s:' % l
    for key, sol in sorted(options[l]):
      # Use # to prevent wrapping mid-item.
      line = '%5d - %d: %s' % (
          key, GRID.count(key), ', '.join('(%d,#%d)' % x for x in sorted(sol)))
      wrapped = textwrap.TextWrapper(subsequent_indent=' '*11).wrap(line)
      print '\n'.join(wrapped).replace('#', ' ')


def PrintPossibles(possibles):
  solutions = {}
  for _, entry, items in possibles:
    solutions[entry] = set((x, entry-x) for x in items)
  PrintSolutions(solutions)


def Main():
  print 'Clues:', len(CLUES), '--', CLUES
  print 'Grid: ', len(GRID), '--', sorted(GRID)
  Validate()
  ApplySolved()
  Validate()

  possibles = GetPossibles()
  possibles = ApplyUniquePossibles(possibles)

  PrintHeader('Pre-solve')
  PrintPossibles(possibles)

  total_possibles = 1
  for n, _, _ in possibles:
    total_possibles = total_possibles * n
  print 'Testing %.2E values...' % total_possibles

  solutions = {}
  for x in GRID:
    solutions[x] = set()
  AccumulateSolutions(possibles, (), solutions)

  PrintHeader('Solved')
  PrintSolutions(solutions)
    

if __name__ == '__main__':
  Main()
