#!/usr/bin/env bash -c


cat Tools/generate_songbook/generated-head.tex

# Sortiert die Lieder nach dem Autor des Textes und bei gleichem Autor nach Titel
#Tools/generate_songbook/list-sorted-songs.py --by titel --by txt --prefix $'\t\t\\input{' --suffix '}' Lieder/*.tex

# Sortiert die Lieder Nach liedanfang (indexeintrag) Diese Sortierung findet man zum beispiel beim Liederbock
#Tools/generate_songbook/list-sorted-songs.py --by index --prefix $'\t\t\\input{' --suffix '}' Lieder/*.tex

# Verhalten des ursprünglichen Codes: Sortierung nach Dateipfad (hier äquivalent zu --by name
# da es nur ein Verzeichnis mit Liedern gibt.
Tools/generate_songbook/list-sorted-songs.py --by path --prefix $'\t\t\\input{' --suffix '}' Lieder/*.tex
# $'\t\t\\' schreibt zwei Tabulatoren und einen backslash und sorgs damit für die passende Einrückung. Das ist natürlich rein kosmetisch.

cat Tools/generate_songbook/generated-foot.tex
