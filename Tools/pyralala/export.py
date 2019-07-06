"""
Data structures used by pyralala
"""
import sys
import itertools
import os.path
import tempfile
import subprocess
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
                raise Exception(
                    "Implementation missing for song part {}.".format(type(part)))

        self._compile_end(song)

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


SVG_IGNORE_ATTRIBUTES = ("height", "width")


class HTMLCompiler(Compiler):
    def _compile_start(self, song):
        self._lines.append("<html>")
        self._lines.append("<head>")
        self._lines.append("    <title>{}</title>".format(song.title))
        self._lines.append("    <meta charset=\"UTF-8\">")
        self._lines.append(
            "    <meta name=\"viewport\" content=\"width=device-width, initial-scale=0.5, user-scalable=yes\">")
        self._lines.append(
            "    <meta name=\"keywords\" content=\"Liederbuch, Songbook, Songs, Bündisch, Pfadfinder, Pfadiralala, VCP\">")
        for k, v in song.info:
            self._lines.append(
                "    <meta name=\"{}\" content=\"{}\">".format(k, v))
            # additionally set the song author as document author (to enable search engines better matching)
            if k in ["wuw", "mel", "txt"]:
                self._lines.append(
                    "    <meta name=\"author\" content=\"{}\">".format(v))
        self._lines.append("    ")
        self._lines.append("    <style>")
        head_path = os.path.join(os.path.dirname(__file__), "pyralala.css")
        with open(head_path, "r") as head_file:
            self._lines.append(head_file.read())
        self._lines.append("    </style>")
        self._lines.append("</head>")
        self._lines.append("<body>")
        self._lines.append("<header>")
        self._lines.append("    <h2> {} </h2>".format(song.title))
        self._lines.append("</header>")

    @staticmethod
    def _gen_music_line(lyric_line, chord_line):
        parts = ["<p>"]
        splits = [pos for pos, _ in chord_line]
        prev = 0
        for i, split in enumerate(splits):
            parts.append(lyric_line[prev:split])
            parts.append("<span>{}</span>".format(chord_line[i][1]))
            prev = split
        parts.append(lyric_line[prev:])
        parts.append("</p>")
        return "".join(parts).replace("|:", "&#119046;").replace(":|", "&#119047;")

    def _compile_music(self, part):
        if isinstance(part, pyralala.data.Song.Chorus):
            self._lines.append("<div class=\"chorus\">")
            self._lines.append("    <h3>{}</h3>".format(part.heading))
        elif isinstance(part, pyralala.data.Song.Verse):
            self._lines.append("<div class=\"verse\">")

        if len(part.lyrics) > 0:
            if isinstance(part, pyralala.data.Song.Verse):
                self._lines.append(
                    "    <h3>{}.</h3>".format(part.verse_number))

            for lyric_line, chord_line in zip(part.lyrics, part.chords):
                self._lines.append(
                    self._gen_music_line(lyric_line, chord_line))

        self._lines.append("</div>")

    def _compile_end(self, song):
        self._lines.append("<footer>")
        self._lines.append("    <h3>{}</h3>".format("".join(song.metainfo)))
        self._lines.append(
            "    <h4>{}</h4>".format("".join(song.songbookinfo)))
        self._lines.append("</footer>")
        self._lines.append("</body>")
        self._lines.append("</html>")

    def _compile_graphics(self, part):
        graphics_id = os.path.splitext(os.path.basename(part.path))[0]
        temp_name = tempfile.mktemp()
        subprocess.call(["pdf2svg", part.path, temp_name])
        with open(temp_name, "r") as temp_file:
            svg = temp_file.readlines()

            self._lines.append(" ".join([attr for attr in svg[1].split(
                " ") if not attr.startswith(SVG_IGNORE_ATTRIBUTES)]))

            for svg_line in svg[2:]:
                self._lines.append(svg_line[:-1].replace("glyph", graphics_id))

        os.remove(temp_name)
