#!/usr/bin/python3
"""Battleship Puzzle Solver.

The program will run to find all possible solutions, printing each as found.

Modify this file to specify the given row/column counts, ships and staring
grid.  This program does not handle initial partial ships.
"""

# TODO: Handle initial partial ships
#   The current implementation assumes that a ship can go any place not
#     explicitly marked as water. This breaks with partial ships because
#     one adjacent direction could be a ship, but not both.
#     Issue?  Placing a ship should mark the other direction.
#   Slop count doesn't work properly with partial ships

import sys

########################################################################
DEBUG = False
WATER = '.'
U = 99

########################################################################
# KEY FOR USER INPUT
INPUT_WATER = 'w'
UNKNOWN = '-'
SHIP = 's'
UNKNOWN_COUNT = U

# User input goes here
INIT_ROW_COUNTS = [4, 2, 3, 3, U, U, 3, 3]
INIT_COL_COUNTS = [4, 3, 1, 2, 2, 1, 3, 4]
INIT_SHIPS = [4, 3, 3, 2, 2, 2, 1, 1, 1, 1]

# partial ships are not supported yet
INIT_GRID = [
  "--w--w--",
  "--------",
  "--------",
  "--------",
  "--------",
  "--------",
  "--------",
  "--w--w--"
]

########################################################################

class State:
  """A battleship puzzle.  The class owns and manipulates the state of
     the puzzle.  The algorithm for what to alter is external to the state."""

  def __init__(self, ships, grid, row_counts, col_counts, row_slop, col_slop,
               ships_to_cover):

    # public
    self.nrows = len(row_counts)
    self.ncols = len(col_counts)

    # private
    self._unplaced_ships = ships
    self._grid = grid

    self._row_counts = row_counts
    self._col_counts = col_counts

    # The number of row/column spaces that are not explicitly claimed
    # in the initial grid enumeration.
    self._row_count_slop = row_slop
    self._col_count_slop = col_slop
    self._ships_to_cover = ships_to_cover

  def DeepCopy(self):
    copy = State(ships=list(self._unplaced_ships),
                 grid=self._DeepCopyOfGrid(),
                 row_counts=list(self._row_counts),
                 col_counts=list(self._col_counts),
                 row_slop=self._row_count_slop,
                 col_slop=self._col_count_slop,
                 ships_to_cover =self._ships_to_cover)
    return copy

  def _DeepCopyOfGrid(self):
    new_grid = list()
    for row in self._grid:
      new_grid.append(list(row))
    return new_grid

  def PrintSolvedGrid(self):
    print("SOLUTION:", len(solved_states))
    self._PrintGrid(INIT_ROW_COUNTS, INIT_COL_COUNTS)
    print("")

  def PrintGrid(self):
    self._PrintGrid(self._row_counts, self._col_counts)
    print("row_slop({}), col_slop({})\n"
          .format(self._row_count_slop, self._col_count_slop))

  def _PrintGrid(self, row_counts, col_counts):
    grid = self._GridOverlaidWithInputWaterAndShips()
    for row in range(self.nrows):
      print(str(row_counts[row]).replace(str(U), ' '), "".join(grid[row]))
    col_labels = ",".join([str(col) for col in col_counts])
    print(" ", col_labels.replace(str(U), ' ').replace(',', ''))

  def _GridOverlaidWithInputWaterAndShips(self):
    """Put back the water and ship symbols provided in the initial input"""
    grid = self._DeepCopyOfGrid()
    for r in range(self.nrows):
      for c in range(self.ncols):
        if INIT_GRID[r][c] == INPUT_WATER or INIT_GRID[r][c] == SHIP:
          grid[r][c] = INIT_GRID[r][c]
    return grid

  def FillWater(self):
    """Change all unknowns to water in rows/cols with a remaining count of 0."""
    for row in range(self.nrows):
      if not self._row_counts[row]:
        self._FillRowWithWater(row)

    for col in range(self.ncols):
      if not self._col_counts[col]:
        self._FillColumnWithWater(col)

  def NextUnplacedShip(self):
    return self._unplaced_ships[0]

  def AllShipsPlaced(self):
    return not self._unplaced_ships

  def NextLegalHorizontalPlacementInRow(self, row, ship, col_offset):
    if not self._RowHasSpaceForShip(row, ship):
      return None

    col = col_offset
    while col+ship <= self.ncols:
      s = 0
      while s < ship and self._SpaceCanBeShip(row, col+s):
        s += 1
      if s == ship:
        if (self._SpaceNotShip(row, col+ship)
            and (self._col_count_slop >=
                 _Count(UNKNOWN_COUNT, self._col_counts[col:col+ship]))):
#                 - _Count(SHIP, self._grid[row][col:col+ship]))):
# Need to check adjacency for preplaced ships
          return col
        col += 1   # Optimization likely costs more than brute force
      else:
        col += s+1

    return None


  def NextLegalVerticalPlacementInColumn(self, col, ship, row_offset):
    if not self._ColumnHasSpaceForShip(col, ship):
      return None

    row = row_offset
    while row+ship <= self.nrows:
      s = 0
      while s < ship and self._SpaceCanBeShip(row+s, col):
        s += 1
      if s == ship:
        if (self._SpaceNotShip(row+s, col)
            and (self._row_count_slop >=
                 _Count(UNKNOWN_COUNT, self._row_counts[row:row+ship]))):
#                 - _Count(SHIP, self._grid[row:row+ship][col]))):
          return row
        row += 1   # Optimization likely costs more than brute force
      else:
        row += s+1

    return None

  def _SpaceCanBeShip(self, row, col):
    return self._grid[row][col] == UNKNOWN or self._grid[row][col] == SHIP

  def _SpaceNotShip(self, row, col):
    return (row == self.nrows or col == self.ncols
            or not self._grid[row][col] == SHIP)


  def InsertFirstShipHorizontalAt(self, row, col):
    new_state = self.DeepCopy()
    ship = new_state._RemoveFirstUnplacedShip()
    new_state._MarkHorizontalRangeAsWater(row, col, ship)
    new_state._DecrementRowCount(row, ship)
    for i in range(ship):
      new_state._grid[row][col+i] = str(ship)
      new_state._DecrementColumCount(col+i)

    if DEBUG:
      print("Horizontal: size({}) at  ({},{})".format(ship, row, col))
      new_state.PrintGrid()
    return new_state

  def InsertFirstShipVerticalAt(self, row, col):
    new_state = self.DeepCopy()
    ship = new_state._RemoveFirstUnplacedShip()
    new_state._MarkVerticalRangeAsWater(row, col, ship)
    new_state._DecrementColumCount(col, ship)
    for i in range(ship):
      new_state._grid[row+i][col] = str(ship)
      new_state._DecrementRowCount(row+i)

    if DEBUG:
      print("Vertical: size({}) at  ({},{})".format(ship, row, col))
      new_state.PrintGrid()

    return new_state

  def _RowHasSpaceForShip(self, row, ship):
    if UNKNOWN_COUNT == self._row_counts[row]:
      return ship <= self._row_count_slop
    return ship <= self._row_counts[row]

  def _ColumnHasSpaceForShip(self, col, ship):
    if UNKNOWN_COUNT == self._col_counts[col]:
      return ship <= self._col_count_slop
    return ship <= self._col_counts[col]

  def _DecrementRowCount(self, row, count=1):
    # TODO: Fix method name.  More than the count is changed
    if UNKNOWN_COUNT == self._row_counts[row]:
      self._row_count_slop -= count
      return
    self._row_counts[row] -= count
    if not self._row_counts[row]:
      self._FillRowWithWater(row)

  def _DecrementColumCount(self, col, count=1):
    # TODO: Fix method name.  More than the count is changed
    if UNKNOWN_COUNT == self._col_counts[col]:
      self._col_count_slop -= count
      return
    self._col_counts[col] -= count
    if not self._col_counts[col]:
      self._FillColumnWithWater(col)

  def _RemoveFirstUnplacedShip(self):
    return self._unplaced_ships.pop(0)

  def _FillRowWithWater(self, row):
    for c in range(self.ncols):
      if self._grid[row][c] == UNKNOWN:
        self._grid[row][c] = WATER

  def _FillColumnWithWater(self, column):
    for r in range(self.nrows):
      if self._grid[r][column] == UNKNOWN:
        self._grid[r][column] = WATER

  def _MarkRangeAsWater(self, min_row, min_col, max_row, max_col):
    """Mark as water says make it water, don't check previous state."""
    min_row = max(min_row, 0)
    min_col = max(min_col, 0)
    max_row = min(max_row+1, self.nrows)
    max_col = min(max_col+1, self.ncols)
    for r in range(min_row, max_row):
      for c in range(min_col, max_col):
        self._grid[r][c] = WATER

  def _MarkHorizontalRangeAsWater(self, row, col, size):
    self._MarkRangeAsWater(row-1, col-1, row+1, col+size)

  def _MarkVerticalRangeAsWater(self, row, col, size):
    self._MarkRangeAsWater(row-1, col-1, row+size, col+1,)

  def __eq__(self, other):
    return self.__hash__() == other.__hash__()

  def __hash__(self):
    # Only care about the grid
    h = ""
    for r in self._GridOverlaidWithInputWaterAndShips():
      h += "".join(r)
    return hash(h)


########################################################################
# Placement Algorithm (not part of the class)

def _TryInsertFirstShipHorizontal(state):
  ship = state.NextUnplacedShip()
  for r in range(state.nrows):
    c = state.NextLegalHorizontalPlacementInRow(r, ship, col_offset=0)
    while c is not None:
      _Solve(state.InsertFirstShipHorizontalAt(r, c))
      c = state.NextLegalHorizontalPlacementInRow(r, ship, c+1)
  return False

def _TryInsertFirstShipVertical(state):
  ship = state.NextUnplacedShip()
  for c in range(state.ncols):
    r = state.NextLegalVerticalPlacementInColumn(c, ship, row_offset=0)
    while r is not None:
      _Solve(state.InsertFirstShipVerticalAt(r, c))
      r = state.NextLegalVerticalPlacementInColumn(c, ship, r+1)
  return False

solved_states = set()
def _Solve(state):
  if state.AllShipsPlaced():
    if state not in solved_states:
      solved_states.add(state)
      state.PrintSolvedGrid()
    return

  if DEBUG:
    print("Ships Remaining({}) {}".format(len(state.ships), state.ships))

  _ = _TryInsertFirstShipHorizontal(state) or _TryInsertFirstShipVertical(state)


########################################################################
# Initializaiton

def _SplitInputRowStringsIntoArrays(grid):
  return [list(row) for row in grid]

def _Count(x, iterable):
  return sum([1 for n in iterable if n == x])

def _GetPreplacedShipCount(grid):
  return sum([row.count(SHIP) for row in grid])

def _GetRowAndColSlopCounts(row_counts, col_counts, ships):
  """The slop is the amount not pre-assigned to a given column or row."""
  ship_sum = sum(ships)
  row_sum = sum(row_counts) - _Count(UNKNOWN_COUNT, row_counts) * UNKNOWN_COUNT
  col_sum = sum(col_counts) - _Count(UNKNOWN_COUNT, col_counts) * UNKNOWN_COUNT
  row_slop = ship_sum - row_sum
  col_slop = ship_sum - col_sum
  if (row_slop < 0) or (col_slop < 0):
    sys.exit("Invalid state: ship_sum({}) row_sum({}), col_sum({})"
             .format(ship_sum, row_sum, col_sum))
  return row_slop, col_slop

########################################################################
def main():
  """Solves battleship puzzle, printing all solutions as they are found.
     The initial puzzle specification must be entered at the top of this file.
     This implementaiton does not handle partial ships.
  """
  grid = _SplitInputRowStringsIntoArrays(INIT_GRID)
  preplaced_ship_count = _GetPreplacedShipCount(INIT_GRID)
  row_slop, col_slop = _GetRowAndColSlopCounts(INIT_ROW_COUNTS,
                                               INIT_COL_COUNTS, INIT_SHIPS)

  state = State(ships=INIT_SHIPS,
                grid=grid,
                row_counts=INIT_ROW_COUNTS, col_counts=INIT_COL_COUNTS,
                row_slop=row_slop, col_slop=col_slop,
                ships_to_cover=preplaced_ship_count)
  state.FillWater()
  print("Starting state after filling in any initial water.")
  print("{}x{} with {} ships, needing a total of {} spaces."
        .format(state.nrows, state.ncols, len(INIT_SHIPS), sum(INIT_SHIPS)))
  print("Ships {}".format(INIT_SHIPS))
  state.PrintGrid()

  # Solutions are printed as they are found.
  _Solve(state)
  print("No (more) solutions.")

if __name__ == '__main__':
  main()
