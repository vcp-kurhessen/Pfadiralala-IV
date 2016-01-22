#!/bin/bash

dir=$(dirname "$0")

echo Script Location: $0
echo Folder Location: "$dir"

cd $dir

pdflatex PfadiralalaIV.tex
songidx titleIndexF.sxd

mv titelIndexF.sbx titelIndexF.org.sbx
sed 's/songlink/hyperlink/g' titelIndexF.org.sbx > titelIndexF.sbx

pdflatex PfadiralalaIV.tex
