"""
Pyralala
---

@author: Jonas Höchst
@site: jonashoechst.de
"""
from pyralala.data import *
import TexSoup, re

IGNORE_CMD = {"intersong", "centering", "markboth", "beginscripture", "endscripture", "nolyrics", "newline", "newpage", "transpose", "vfill", "newchords", "$"}

class SongReader:
    def __init__(self, file_path):
        self.file_path = file_path
        with open(file_path, "r") as file:
            self.lines = file.read()

        self.tex = TexSoup.TexSoup(self.lines)
        self.song = DummySong()
        self._commands = {'\\everychorus': 'Refrain'}

    @staticmethod
    def parse_opt_args(args):
        parsed = []
        ex = re.compile(r"(\w+={[\w \(\),]+})")
        for pair in ex.findall(args):
            parsed.append(pair.split("="))
        return parsed

    def read_content(self, d):
        if isinstance(d, str):
            self.song.add_text(d)
        elif isinstance(d, TexSoup.data.RArg):
            self.song.add_text(d.value)

        elif d.name == "beginsong":
            for a in d.args:
                if isinstance(a, TexSoup.data.RArg):
                    self.song = Song(a.value)
                elif isinstance(a, TexSoup.data.OArg):
                    self.song.info = SongReader.parse_opt_args(a.value)
        elif d.name == "endsong":
            self.song.endsong()

        elif d.name == "renewcommand":
            arg = list(d.contents)[2]
            self._commands[d.args[0]] = arg.value[4:].rstrip()
        
        elif d.name == "beginchorus":
            self.song.beginchorus(self._commands['\\everychorus'])
        elif d.name == "printchorus":
            self.song.beginchorus("Refrain (wdh.)")
            self.song.endmusicpart()
        elif d.name == "repchorus":
            self.song.beginchorus("Refrain ({}x)".format(d.args[0]))
            self.song.endmusicpart()

        elif d.name == "beginverse":
            self.song.beginverse()
            for c in d.contents:
                self.song.add_text(c)
        elif d.name == "beginverse*":
            self.song.beginanonverse()
            for c in d.contents:
                self.song.add_text(c)
        elif d.name == "interlude":
            self.song.beginanonverse()
            self.song.add_text(d.args[0])
            self.song.endmusicpart()

        elif d.name in ["endverse", "endverse*", "endchorus"]:
            self.song.endmusicpart()

        elif d.name == "memorize":
            if len(d.args) == 1:
                self.song.memorize(key=d.args[0])
            else:
                self.song.memorize()
        elif d.name == "replay":
            if len(d.args) == 1:
                self.song.replay(key=d.args[0])
            else:
                self.song.replay()

        elif d.name == "lrep":
            self.song.add_text("|:")
        elif d.name == "rrep":
            self.song.add_text(":|")
        elif d.name == "rep":
            self.song.add_text(" (x{})".format(d.args[0]))
        elif d.name == "echo":
            self.song.add_text("({})".format(d.args[0]))
        elif d.name == "emph":
            self.song.add_text("*{}*".format(d.args[0]))

        elif d.name == "includegraphics":
            options = []
            for a in d.args:
                if isinstance(a, TexSoup.data.RArg):
                    path = a.value
                elif isinstance(a, TexSoup.data.OArg):
                    options = SongReader.parse_opt_args(a.value)
            self.song.includegraphics(path, options)

        # probably an escaped sharp-chord
        elif d.name.startswith("#"):
            self.song.add_text(str(d)[1:])
        elif d.name in IGNORE_CMD:
            pass
        else:
            raise Exception("Element is not parsed: \"{}\" ({})".format(d.name, type(d))) 

    def read(self):
        try:
            for d in self.tex.expr.contents:
                self.read_content(d)
        except AttributeError as e:
            print(d)
            raise e