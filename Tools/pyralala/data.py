"""
Data structures used by pyralala
"""
import re
import itertools
import collections

__all__ = ["Song", "DummySong"]

METAINFO_FORMAT = collections.OrderedDict([
    ("mel", " Melodie: {}"),
    ("meljahr", " Text: {}"),
    ("txt", " Album: {}"),
    ("txtjahr", ", {}"),
    ("wuw", " Worte und Weise: {}"),
    ("alb", " Album: {}"),
    ("jahr", ", {}"),
])

SONGBOOK_FORMAT = collections.OrderedDict([
    ("bo", "Liederbock: {} "),
    ("pfi", "Pfadiralala I: {} "),
    ("pfii", "Pfadiralala II: {} "),
    ("pfiii", "Pfadiralala III: {} "),
    ("ju", "Jurtenburg: {} "),
    ("gruen", "Das Grüne: {} "),
    ("kssiv", "Kinder-Schoko-Songs IV: {} "),
    ("siru", "Die singende Runde: {} "),
    ("biest", "Das Biest: {} "),
])


class DummySong(object):
    def add_text(self, text):
        return


class Song(object):
    class MusicPart(object):
        def __init__(self):
            self._raw_text = ""
            self._lines = []
            self._replay_key = ""

        def append(self, new_text):
            self._raw_text += str(new_text)

        def end(self, memory, memorize_key=None):
            # remove comments
            lines = [line.split("%")[0]
                     for line in self._raw_text.splitlines()]
            # take only nonempty lines
            self._lines = ([l for l in lines if len(l) > 0])

            if not memorize_key == None:
                chords = self._get_memorize_chords()
                if len(chords) > 0:
                    memory[memorize_key] = chords
                self._replay_key = memorize_key

            self._finalize(memory)

        def _finalize(self, memory):
            # create lyrics and chords array
            self.lyrics = []
            self.chords = []

            # lookup previously saved chords
            try:
                chords = memory[self._replay_key]
                chord_gen = (c for c in chords)
            except KeyError:
                return

            # get extra chords for this part
            extra = self._get_memorize_chords(token="§")
            extra_gen = (c for c in extra)

            # loop over all chars in all lines and pick the matching chords
            for l in self._lines:
                line_chords = []
                loc = 0
                for c in l:
                    if c == '^':
                        line_chords.append((loc, next(chord_gen)))
                    elif c == "$":
                        line_chords.append((loc, next(extra_gen)))
                    else:
                        loc += 1
                self.lyrics.append(l.replace("^", "").replace("§", ""))
                self.chords.append(line_chords)

        def _get_memorize_chords(self, token="^"):
            # find all the chords
            ex = re.compile(r"\\\[([^\]]+)\]")
            chords = ex.findall("\n".join(self._lines))
            # replace chords in the lines
            self._lines = [ex.subn(token, l)[0] for l in self._lines]
            return chords

        def __repr__(self, head="[Music Part]"):
            ret = "{}\n".format(head)
            if len(self.text) == 0:
                return ret
            return ret + self.chorded_text + "\n\n"

        @property
        def text(self, sep="\n"):
            return sep.join(self.lyrics)
            # return sep.join([l.replace("^", "") for l in self.lines])

    class Chorus(MusicPart):
        def __init__(self, heading):
            Song.MusicPart.__init__(self)
            self.heading = heading

        def __repr__(self):
            return Song.MusicPart.__repr__(self, "[{}]".format(self.heading))

    class Verse(MusicPart):
        def __init__(self, verse_number):
            Song.MusicPart.__init__(self)
            self.verse_number = verse_number

        def __repr__(self):
            return Song.MusicPart.__repr__(self, "[Verse {}]".format(self.verse_number))

    class AnonVerse(MusicPart):
        def __init__(self):
            Song.MusicPart.__init__(self)

        def __repr__(self):
            return Song.MusicPart.__repr__(self, "")

    class Intermediate():
        def append(self, new_text):
            pass

        def __repr__(self):
            return ""

    class Graphics():
        def __init__(self, path, options=[]):
            self.path = path
            self.options = options

        def __repr__(self):
            return "[Graphic: {}]\n\n".format(self.path)

    def __init__(self, title, info=[]):
        self.title = title
        self.info = info
        self._contents = []
        self._verse_counter = 0
        self._memory = {}
        self._memorize_key = None
        self._contents.append(self.Intermediate())

    def __repr__(self):
        ascii_song = "### {} ###\n\n".format(self.title)
        for c in self._contents:
            ascii_song += str(c)
        return ascii_song

    def beginchorus(self, heading):
        self._contents.append(self.Chorus(heading))

    def beginverse(self):
        self._verse_counter += 1
        self._contents.append(self.Verse(self._verse_counter))

    def beginanonverse(self):
        self._contents.append(self.AnonVerse())

    def endmusicpart(self):
        # implicit memorize, if default is not yet set.
        if not "" in self._memory:
            self._memorize_key = ""
        self._contents[-1].end(self._memory, self._memorize_key)
        self._contents.append(self.Intermediate())

        # reset memorize key after use
        self._memorize_key = None

    def includegraphics(self, path, options):
        self._contents.append(self.Graphics(path, options))
        self._contents.append(self.Intermediate())

    def endsong(self):
        self._contents.append(self.Intermediate())

    def memorize(self, key=""):
        self._memorize_key = key

    def replay(self, key=""):
        self._contents[-1]._replay_key = key

    def add_text(self, text):
        self._contents[-1].append(text)

    @staticmethod
    def _key_formatter(formats, data):
        out = []
        for key, form in formats.items():
            for data_key, data_val in data:
                if data_val == "":
                    continue
                if key == data_key:
                    out.append(form.format(data_val))
        return out

    @property
    def metainfo(self):
        return self._key_formatter(METAINFO_FORMAT, self.info)

    @property
    def songbookinfo(self):
        return self._key_formatter(SONGBOOK_FORMAT, self.info)
