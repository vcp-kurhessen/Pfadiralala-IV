#!/usr/bin/env python3
import argparse
import sys
import logging

from pyparsing import *

logger = logging.getLogger(__name__)


def _setup_logging(level):
    if level > 3:
        logging_level = logging.DEBUG
    else:
        logging_level = logging.ERROR - (10 * level)

    # stderr_formatter = logging.Formatter(
        # "%(name)s - %(levelname)s - %(message)s")
    stderr_handler = logging.StreamHandler()
    # stderr_handler.setFormatter(stderr_formatter)
    logger.addHandler(stderr_handler)
    logger.setLevel(logging_level)

    if level > 3:
        logger.warning("Logging level cannot be increased further.")


_setup_logging(3)

# Configure Parser
ParserElement.setDefaultWhitespaceChars(' \t')

# Basics
Regulars = CharsNotIn("{},[]=\\")


class Element:
    _tests = []

    def __repr__(self):
        return f"<{self.__class__.__name__}: {self.__dict__}>"

    @classmethod
    def test(cls):
        for t in cls._tests:
            logger.debug(cls.Parser.parseString(t))


class Argument(Element):
    Parser = Regulars ^ (Literal("{") + CharsNotIn("}") + Literal("}"))
    Parser.setParseAction(lambda l: Argument(l))

    def __init__(self, l):
        if l[0] == "{":
            self.arg = l[1]
        else:
            self.arg = l[0]

    _tests = [
        "Simple Argument",
        "{Braced Argument!}",
    ]


Argument.test()


class KeyValueArgument(Element):
    Parser = Argument.Parser + Literal("=") + Argument.Parser
    Parser.setParseAction(lambda l: KeyValueArgument(l))

    def __init__(self, l):
        self.k = l[0]
        self.v = l[2]

    _tests = [
    ]

    @classmethod
    def test(cls):
        logger.debug(cls.Parser.parseString("jahr=1970"))
        logger.debug(cls.Parser.parseString("txt={A Great Composer, 1970}"))


KeyValueArgument.test()


class OptionalArgument(Element):
    Parser = Literal("[") + \
        (KeyValueArgument.Parser) + \
        ZeroOrMore(Literal(",") + (KeyValueArgument.Parser)) +\
        Literal("]")
    Parser.setParseAction(lambda l: OptionalArgument(l))

    def __init__(self, l):
        self.args = l[1::2]

    _tests = [
        "[jahr=1970]",
        "[jahr=1970, name={Example Name!}]",
    ]


OptionalArgument.test()


class Comment(Element):
    Parser = Literal("%") + Optional(CharsNotIn("\n"))
    Parser.setParseAction(lambda l: Comment(l))

    def __init__(self, l):
        if len(l) == 1:
            self.str = ""
        else:
            self.str = l[1]

    _tests = [
        "% Terrific comment :-)",
        "%"
    ]


Comment.test()


class Chord(Element):
    Parser = Literal("\\[") + CharsNotIn("]") + Literal("]")
    Parser.setParseAction(lambda l: Chord(l))

    def __init__(self, l):
        self.chord = l[1]

    _tests = [
        "\\[Am]",
        "\\[D/f#-C]",
    ]


Chord.test()


class RepChord(Element):
    Parser = Literal("^")
    Parser.setParseAction(lambda _: RepChord())

    _tests = [
        "^",
    ]


RepChord.test()


class Rrep(Element):
    Parser = Literal("\\rrep")
    Parser.setParseAction(lambda _: Rrep())

    _tests = [
        "\\rrep",
    ]


Rrep.test()


class Lrep(Element):
    Parser = Literal("\\lrep")
    Parser.setParseAction(lambda _: Lrep())

    _tests = [
        "\\lrep",
    ]


Lrep.test()


class Rep(Element):
    Parser = Literal("\\rep") + Argument.Parser
    Parser.setParseAction(lambda l: Rep(l))

    _tests = [
        "\\rep{2}",
    ]

    def __init__(self, l):
        self.count = l[1]


Rep.test()


class Lyrics(Element):
    Parser = CharsNotIn("\\[]\n^%")
    Parser.setParseAction(lambda l: Lyrics(l))

    def __init__(self, l):
        self.lyrics = l[0]

    _tests = [
        "I sing a song",
    ]


Lyrics.test()


class MusicLine(Element):
    Parser = ZeroOrMore(Comment.Parser ^ Lyrics.Parser ^
                        Chord.Parser ^ Rep.Parser ^ Lrep.Parser ^ Rrep.Parser) + Literal("\n")
    Parser.setParseAction(lambda l: MusicLine(l))

    def __init__(self, l):
        print(l)
        self.parts = l[:-1]

    _tests = [
        "\n",
        "\\[Am]\n",
        "% Empty line\n",
        "\\[Am]I sing ^lyrics.\n",
    ]


MusicLine.test()


# # Lyrics

# class PLyrics(str):
#     pass

# Lyrics = CharsNotIn("\\[]\n^%")
# Lyrics.setParseAction(lambda l: PLyrics(l[0]))
# print(Lyrics.parseString("Some lyrics"))

# # Music Line

# class PMusicLine(list):
#     pass

# MusicLine = ZeroOrMore(Comment ^ Lyrics ^ Chord ^ Rep) + Literal("\n")
# MusicLine.setParseAction(lambda l: PMusicLine(l[:-1]))
# print(MusicLine.parseString("\\[Am]I sing ^lyrics. % Comment\n"))

# # Songparts

# class PMusicPart(list):
#     def __init__(self, inlist):
#         if inlist[0] == "\\memorize":
#             self.memorize = True
#             self += inlist[1:]
#         else:
#             self += inlist

# class PVerse(PMusicPart):
#     pass

# class PChorus(PMusicPart):
#     pass

# class PGraphics:
#     def __init__(self, l):
#         if isinstance(l[1], POptionalArgument):
#             self.config = config
#             self.path = l[1]
#         else:
#             self.config = POptionalArgument

# Verse = Literal("\\beginverse") + Optional(Literal("\\memorize")) + \
#     ZeroOrMore(MusicLine) + Literal("\\endverse")
# Verse.setParseAction(lambda l: PVerse(l[1:-1]))
# print(Verse.parseString(
#     "\\beginverse\\memorize\nMusical \\[Am]Line\n\\endverse"))

# Chorus = Literal("\\beginchorus") + Optional(Literal("\\memorize")) + \
#     ZeroOrMore(MusicLine) + Literal("\\endchorus")
# Chorus.setParseAction(lambda l: PChorus(l[1:-1]))
# print(Chorus.parseString(
#     "\\beginchorus\nMusical \\[Am]Line\n\\endchorus"))

# Graphics = Literal("\\includegraphics") + OptionalArgument + Argument
# Graphics.setParseAction(lambda l: PGraphics(
#     l[1]) if len(l) < 2 else PGraphics(l[2], l[1]))
# print(Graphics.parseString("\\includegraphics[page=1]{Test.pdf}"))

# # Song

# class PBeginsong:
#     def __init__(self, l):
#         self.name = l[0]
#         if len(l) == 2:
#             self.meta = l[1]
#         else:
#             self.meta = POptionalArgument([])

# Beginsong = Literal("\\beginsong") + \
#     Argument + Optional(OptionalArgument)
# Beginsong.setParseAction(lambda l: PBeginsong(l[1:]))
# print(Beginsong.parseString("\\beginsong{A Song}"))

# def newSong(l):
# song = Song(l[1], l[2])

# Endsong = Literal("\\endsong")
# Emptyline = Literal("\n")
# ParseSong = Beginsong + ZeroOrMore(Verse ^ Chorus ^
#                                    Graphics ^ Comment ^ Emptyline) + Endsong


def _test():
    pass
# print(Argument.parseString("{Autor Name, 1992}"))
# print(Argument.parseString("begin"))
# print(KeyValueArgument.parseString("mel=value"))
# print(OptionalArgumentParser.parseString("[jahr=2019, mel={Author Name}]"))
# Comment.parseString("% This is a comment.")

# Chord.parseString("\\[C#m/G#]")
# MusicLine.parseString("\\[Dm]Abends ^geh'n \\lrep\n")

# exampleVerse = '''\\beginverse
# \\[Dm]Doch! Auch meiner \\[C]Abendtaten, \\[Dm]deren \\[C]Sklav' ich \\[Dm]bin,
# \\[Dm]Kann der Weltgeist \\[C]nicht entraten, \\[Dm]Sie auch \\[C]haben \\[Dm]Sinn.
# \\endverse'''

# Verse.parseString(exampleVerse)
# Chorus.parseString("\\beginchorus\n\\endchorus\n")
# Graphics.parseString("\\includegraphics[page=1]{Noten/Abends.pdf}")

# Beginsong.parseString(
#     "\\beginsong{Abends geh'n die Liebespaare}[txt={Hermann Hesse}, mel={Florian Schön, BdP Raugrafen, Simmern(2013)}, siru={1}, biest={503}]")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Convert LaTeX songs files.')
    parser.add_argument("file", help="The LaTeX song file to be converted.")
    parser.add_argument("-o", "--out", help="Output file path.")
    parser.add_argument("-t", "--test", help="Only test parsing.", action='store_const',
                        const=True, default=False)
    parser.add_argument(
        "-v", "--verbose", help="verbose output", action="count", default=0)
    args = parser.parse_args()

    _setup_logging(args.verbose)

    with open(args.file) as infile:
        contents = infile.read()

    if args.test:
        _test()
    #     ParseSong.parseString(contents)
    #     sys.exit(0)

    # s = ParseSong.parseString(contents)
    # print(s)
