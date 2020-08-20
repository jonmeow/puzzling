#!/usr/bin/env python3

import sys

MAPPINGS = {
"TTT": "F",
"TTC": "F",
"TTA": "L",
"TTG": "L",
"TCT": "S",
"TCC": "S",
"TCA": "S",
"TCG": "S",
"TAT": "Y",
"TAC": "Y",
"TAA": "X",
"TAG": "X",
"TGT": "C",
"TGC": "C",
"TGA": "X",
"TGG": "W",
"CTT": "L",
"CTC": "L",
"CTA": "L",
"CTG": "L",
"CCT": "P",
"CCC": "P",
"CCA": "P",
"CCG": "P",
"CAT": "H",
"CAC": "H",
"CAA": "Q",
"CAG": "Q",
"CGT": "R",
"CGC": "R",
"CGA": "R",
"CGG": "R",
"ATT": "I",
"ATC": "I",
"ATA": "I",
"ATG": "M",
"ACT": "T",
"ACC": "T",
"ACA": "T",
"ACG": "T",
"AAT": "N",
"AAC": "N",
"AAA": "K",
"AAG": "K",
"AGT": "S",
"AGC": "S",
"AGA": "R",
"AGG": "R",
"GTT": "V",
"GTC": "V",
"GTA": "V",
"GTG": "V",
"GCT": "A",
"GCC": "A",
"GCA": "A",
"GCG": "A",
"GAT": "D",
"GAC": "D",
"GAA": "E",
"GAG": "E",
"GGT": "G",
"GGC": "G",
"GGA": "G",
"GGG": "G",
}

arg = sys.argv[1]

rem_arg = arg
while len(rem_arg) >= 3:
  val = rem_arg[:3]
  rem_arg = rem_arg[3:]
  print(MAPPINGS[val], end="")
print()
