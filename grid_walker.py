#!/usr/local/bin/python3
#
# Given input like "4D 3D 2L 3U 4U 2L 1L 4D 2D 2L 5U"...

import sys

GRID="""
NFOBAISNBE
GHEREIKDYT
ALWLCOOSOÜ
KRSOBÉSRAE
DNGBNIKELR
KIFOKCLONF
BTLAIDCYLD
ELONOLCOAW
EOISHBÜONR
GSPBAFNDKI
"""

# Switch GRID to an array for indexing.
GRID = GRID.strip().split('\n')

def Move(x, y, steps, val):
  if not steps:
    return val
  step = steps[0]
  assert len(step) == 2, "Currently only support 1 digit"
  dist = int(step[0])
  assert step[1] in "LRUD"
  if step[1] == "L":
    x -= dist
    if x < 0:
      return None
  elif step[1] == "R":
    x += dist
    if x >= len(GRID[0]):
      return None
  elif step[1] == "U":
    y -= dist
    if y < 0:
      return None
  elif step[1] == "D":
    y += dist
    if y >= len(GRID[0]):
      return None
  return Move(x, y, steps[1:], val + GRID[y][x])

for x in range(len(GRID[0])):
  for y in range(len(GRID)):
    val = Move(x, y, sys.argv[1:], GRID[y][x])
    if val:
      print(x, y, val)
