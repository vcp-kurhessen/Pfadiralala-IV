#!/usr/bin/env bash

for song in Lieder/*.tex; do 
    grep "${song%.tex}" Ausgaben/*.tex > /dev/null || echo "${song}" ; 
done
