"""
Data structures used by pyralala
"""
import sys, itertools
import pyralala

__all__ = ["Compiler"]

class Compiler(object):
    def __init__(self):
        self._lines = []

    def compile(self, song, out=sys.stdout):
        self._lines = []
        self._compile_start(song)

        for part in song._contents:
            if isinstance(part, pyralala.data.Song.MusicPart):
                self._compile_music(part)
            elif isinstance(part, pyralala.data.Song.Intermediate):
                pass
            elif isinstance(part, pyralala.data.Song.Graphics):
                self._compile_graphics(part)
            else:
                raise Exception("Implementation missing for song part {}.".format(type(part)))

    def write(self, out=sys.stdout):
        out.write("\n".join(self._lines))

    def _compile_start(self, song):
        self._lines.append("### {} ###".format(song.title))
        self._lines.append("")

    def _compile_end(self, song):
        pass

    def _compile_music(self, part):
        if isinstance(part, pyralala.data.Song.Chorus):
            self._lines.append("[{}]".format(part.heading))
        elif isinstance(part, pyralala.data.Song.Verse):
            self._lines.append("[Verse {}]".format(part.verse_number))

        chord_lines = [self._gen_chord_line(c) for c in part.chords]
        self._lines += itertools.chain(*zip(chord_lines, part.lyrics))
        if len(chord_lines) > 0:
            self._lines.append("")
            self._lines.append("")

    def _compile_graphics(self, part):
        self._lines.append("[Graphic: {}]".format(part.path))
        self._lines.append("")

    @staticmethod
    def _gen_chord_line(chords):
        out = ""
        for pos, val in chords:
            out = out.ljust(pos) + val
        return out

class MarkdownCompiler(Compiler):
    def _compile_start(self, song):
        self._lines.append("## {} ".format(song.title))
        self._lines.append("")

    def _compile_end(self, song):
        pass

    def _compile_music(self, part):
        if isinstance(part, pyralala.data.Song.Chorus):
            self._lines.append("#### {}".format(part.heading))
        elif isinstance(part, pyralala.data.Song.Verse):
            self._lines.append("#### Verse {}".format(part.verse_number))

        if len(part.lyrics) > 0:
            self._lines.append("```")
            chord_lines = [self._gen_chord_line(c) for c in part.chords]
            self._lines += itertools.chain(*zip(chord_lines, part.lyrics))
            self._lines.append("```")
            self._lines.append("")

    def _compile_graphics(self, part):
        self._lines.append("![](../{})".format(part.path))
        self._lines.append("")

    @staticmethod
    def _gen_chord_line(chords):
        out = ""
        for pos, val in chords:
            out = out.ljust(pos) + val
        return out

    
