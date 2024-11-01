# MLTED

This repository contains an implementation of O-MLTED, the optimal multi-label tree edit distance problem, computing both the distance and alignment between two input trees.

## Input

MLTED requires two files each specifying one of the input trees. The format for trees has two main parts. The first part is a list of nodes and their label set.  The second part is a list of parent:child sets where children nodes are separated by commas.

## Usage

To run MLTED:

```python MLTED.py file1 file2```