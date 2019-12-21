#!/usr/bin/env python3

"""
Pyralala
---

@author: Jonas Höchst
@site: jonashoechst.de
"""
from data import *
from parser import Song
import re

IGNORE_CMD = {"intersong", "centering", "markboth", "beginscripture", "endscripture",
              "nolyrics", "newline", "newpage", "transpose", "vfill", "newchords", "$"}


class SongReader:
    def __init__(self, file_path):
        self.file_path = file_path
        with open(file_path, "r") as infile:
            self.lines = infile.read()

        self.parsed = Song.parseString(self.lines)
        self.iter = iter(self.parsed)
        self.song = DummySong()
        self._commands = {'everychorus': 'Refrain'}

    def read(self):
        while True:
            d = next(self.iter)
            self.read_content(d)

    def read_content(self, d):
        print(d)


s = SongReader("Lieder/Abends.tex")
s.read()
