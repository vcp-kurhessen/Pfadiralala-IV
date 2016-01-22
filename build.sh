#!/bin/bash

dir=$(dirname "$0")

echo Script Location: $0
echo Folder Location: "$dir"

cd $dir
# 1st: get size of index
pdflatex PfadiralalaIV.tex
songidx titelIndexF.sxd
# 2nd: get correct positions
pdflatex PfadiralalaIV.tex
songidx titelIndexF.sxd
# 3rd: use correct index
pdflatex PfadiralalaIV.tex
