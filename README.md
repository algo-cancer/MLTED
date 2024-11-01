# O-MLTED

This repository contains an implementation of O-MLTED, the optimal multi-label tree edit distance problem, computing both the distance and alignment between two input trees.

## Input

O-MLTED requires two text files each specifying one of the two input trees. The format of the text files is three columns separated by whitespace: a node id, the node's parent id, and a list of the labels of the node.

The root node id should be ROOT with parent None.

The labels should be comma-separated, no white space.  See example-tree1.txt and example-tree2.txt for an example.

## Usage

This script is made in Python 3. To run the O-MLTED implementation:

```python OMLTED.py tree-file1 tree-file2```

Sample execution on the included example tree files:
```
C:\OMLTED python OMLTED.py example-tree1.txt example-tree2.txt
Checking k =   16
Finished k =  16
Non-common labels deleted in pre-processing:  0
OMLTED:  10
Normalized OMLTED:  0.29411764705882354
```