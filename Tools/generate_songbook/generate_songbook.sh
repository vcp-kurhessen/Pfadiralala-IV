#!/usr/bin/env bash


cat Tools/generated-head.tex

for file in Lieder/*.tex; 
    do echo "\\input{$file}"
done

cat generated-foot.tex
