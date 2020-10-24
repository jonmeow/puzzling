#!/usr/bin/python3
"""Jigsaw puzzle solver"
The program will run to find all possible solutions, printing each as found.
Modify this file to specify the pieces and whether the pieces can be rotated.
"""

import sys
from pprint import PrettyPrinter

DEBUG = False

########################################################################
# User input goes here


# Default: Create an empty grid of size ROW_COUNT * COL_COUNT
# If the grid should have blocked squares (e.g. holes), you can specify
# the starting state by hand.  Any non-space char is a blocking character.
GRID = []
ROW_COUNT = 4
COL_COUNT = 5

# Pieces -- Tip: Put the biggest pieces first
#           Enter each piece as a rectangle with blanks as needed
#           The piece should touch every edge (no blank edge columns or rows)
ALLOW_ROTATED_PIECES = True
PIECES = [
]

USE_SAMPLE_DATA = not PIECES
if USE_SAMPLE_DATA:
  # Sample pieces and solution when no rotation is allowed
  # 33311
  # 44211
  # 42265
  # 42665

  PIECES = [
    ["11",
     "11"
    ],

    [" 2",
     "2 ",
     "2 "],

    ["333"],

    ["44",
     "4 ",
     "4 "],

    ["5",
     "5"],

    [" 6",
     "66"]
    ]
  GRID = ["     ", "     ", "  x  ", "     "]
  ROW_COUNT = 4
  COL_COUNT = 5

########################################################################

solved_states = set()
class State:
  """A partially filled in jigsaw puzzle."""

  def __init__(self, pieces, grid, nrows, ncols, next_space_to_fill=None):
    self._unplaced_pieces = pieces
    self._grid = grid
    self._nrows = nrows
    self._ncols = ncols
    self._next_space_to_fill = next_space_to_fill
    if not next_space_to_fill:
      self._next_space_to_fill = [0, 0]
      self._FindNextSpaceToFill()


  def PrintSolvedGrid(self):
    print("SOLUTION:", len(solved_states))
    for row in range(self._nrows):
      print("".join(self._grid[row]))
    print("")

  def DeepCopy(self):
    return State(pieces=list(self._unplaced_pieces),
                 grid=self._DeepCopyOfGrid(),
                 nrows=self._nrows, ncols=self._ncols,
                 next_space_to_fill=self._next_space_to_fill)

  def _DeepCopyOfGrid(self):
    new_grid = list()
    for row in self._grid:
      new_grid.append(list(row))
    return new_grid

  def _CanPlacePiece(self, piece):
    return self._OverlayPiece(piece, mark_piece=False)

  def _PlacePiece(self, piece, unrotated_piece):
    self._OverlayPiece(piece, mark_piece=True)
    self._unplaced_pieces.remove(unrotated_piece)

  @staticmethod
  def _NumberOfLeadingSpacesInFirstRow(piece):
    count = 0
    for c in piece[0]:
      if not c.isspace():
        return count
      count += 1
    return count

  def _OverlayPiece(self, piece, mark_piece):
    base_row = self._next_space_to_fill[0]
    base_col = self._next_space_to_fill[1]

    base_col -= self._NumberOfLeadingSpacesInFirstRow(piece)
    if (base_col < 0 or
        base_col + len(piece[0]) > self._ncols or
        base_row + len(piece) > self._nrows):
      return False

    row_delta = 0
    for row in piece:
      col_delta = 0
      for c in row:
        if not (c.isspace() or
                self._grid[base_row+row_delta][base_col+col_delta].isspace()):
          return False

        if mark_piece and not c.isspace():
          self._grid[base_row+row_delta][base_col+col_delta] = c

        col_delta += 1
      row_delta += 1

    return True

  def _FindNextSpaceToFill(self):
    row = self._next_space_to_fill[0]
    col = self._next_space_to_fill[1]
    while row < self._nrows:
      while col < self._ncols:
        if self._grid[row][col].isspace():
          self._next_space_to_fill = [row, col]
          return
        col += 1
      row += 1
      col = 0

  def _TryFillNextSpace(self):
    """Fill the grid from top left to bottom right, filling each row."""
    for piece in self._unplaced_pieces:
      self._TryFillNextSpaceWithRotatedPiece(piece, piece)
      if ALLOW_ROTATED_PIECES:
        self._TryFillNextSpaceWithRotatedPiece(self._Rotate90(piece), piece)
        self._TryFillNextSpaceWithRotatedPiece(self._Rotate180(piece), piece)
        self._TryFillNextSpaceWithRotatedPiece(self._Rotate270(piece), piece)

  def _TryFillNextSpaceWithRotatedPiece(self, piece, unrotated_piece):
    if self._CanPlacePiece(piece):
      new_state = self.DeepCopy()
      new_state._PlacePiece(piece, unrotated_piece)
      new_state._FindNextSpaceToFill()
      if DEBUG:
        print("placed {}".format(piece))
        PrettyPrinter().pprint(new_state._grid)
      new_state.Solve()
    return False

  # Is there a clean way to merge the 90 and 270 rotations?
  # The method differ by one line.  (And are both written like crap)
  @staticmethod
  def _Rotate90(piece):
    print(piece)
    #exit(1)
    nrows = len(piece)
    ncols = len(piece[0])
    new_piece = []
    for c in range(ncols):
      new_row = [" "] * nrows
      for r in range(nrows):
        new_row[r] = piece[nrows-r-1][c]
      new_piece.append(new_row)
    return new_piece

  @staticmethod
  def _Rotate180(piece):
    new_piece = []
    for row in reversed(piece):
      new_piece.append("".join(reversed(row)))
    return new_piece

  @staticmethod
  def _Rotate270(piece):
    nrows = len(piece)
    ncols = len(piece[0])
    new_piece = []
    for c in range(ncols):
      new_row = [" "] * nrows
      for r in range(nrows):
        new_row[r] = piece[r][ncols-c-1]
      new_piece.append(new_row)
    return new_piece

  def Solve(self):
    if not self._unplaced_pieces:
      if self not in solved_states:
        solved_states.add(self)
        self.PrintSolvedGrid()
      return

    if DEBUG:
      print("Pieces Remaining({}) {}"
            .format(len(self._unplaced_pieces), self._unplaced_pieces))

    _ = self._TryFillNextSpace()


  def __eq__(self, other):
    return self.__hash__() == other.__hash__()

  def __hash__(self):
    # Only care about the grid
    h = ""
    for r in self._grid:
      h += "".join(r)
    return hash(h)


########################################################################
# Initializaiton

def _SpacesInStartingGrid(grid):
  return sum(row.count(" ") for row in grid)

def _SizeOfPiece(piece):
  total = 0
  for row in piece:
    for c in row:
      total += not c.isspace()
  return total

def _SumOfPieceSizes(pieces):
  total = 0
  for piece in pieces:
    total += _SizeOfPiece(piece)
  return total

def _CreateEmptyGrid():
  return [[' ' for c in range(COL_COUNT)] for r in range(ROW_COUNT)]

def _PrintStartingState():
  print("{}x{} with {} Pieces, needing a total of {} spaces."
        .format(ROW_COUNT, COL_COUNT, len(PIECES), _SumOfPieceSizes(PIECES)))

  print("Pieces:")
  for p in PIECES:
    PrettyPrinter().pprint(p)
  print()

  # Use Grid if Given, else start with an empty grid
  if GRID:
    print("Starting Grid:")
    print(GRID)
    print()

########################################################################
def main():
  """Solves a jigsaw puzzle, printing all solutions as they are found.
     The initial puzzle specification must be entered at the top of this file.
  """
  _PrintStartingState()

  grid = GRID if GRID else _CreateEmptyGrid()

  if not _SumOfPieceSizes(PIECES) == _SpacesInStartingGrid(grid):
    print("ERROR: Pieces will not exactly fill grid which has {} spaces."
          .format(_SpacesInStartingGrid(grid)))
    sys.exit(1)

  # Solutions are printed as they are found.
  State(pieces=PIECES, grid=grid, nrows=ROW_COUNT, ncols=COL_COUNT).Solve()

  print("No (more) solutions.")

if __name__ == '__main__':
  main()
