#!/bin/bash

dir=$(dirname "$0")

echo Script Location: $0
echo Folder Location: "$dir"

cd $dir
# 1st: get size of index
pdflatex PfadiralalaIV-2.tex
songidx PfadiralalaIV-2.sxd

# 2nd: get correct positions
pdflatex PfadiralalaIV-2.tex
songidx PfadiralalaIV-2.sxd

# 3rd: use correct index
pdflatex PfadiralalaIV-2.tex
