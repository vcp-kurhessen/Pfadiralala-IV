import jinja2 as j2
import os
from typing import Tuple, Union, List, Dict, Collection
import re
import sys
from lib.Heuristik.Heuristik import Heuristik
from lib.texttype.texttype import texttype
from lib.texttype.SongLaTexttype import SongLaTexttype
import config.config as config
# Erlaubt das einfache Arbeiten mit texen zugeordneten daten

# typing: Pfadspezifikation:
pfad = Union[str, os.DirEntry]


class SongKonverter():
    def __init__(self, templatePfad: pfad) -> None:
        self.template = self.templateLaden(templatePfad)

    def templateLaden(self, templatePfad: pfad) -> None:
        #  Jinja konfigurieren
        self.latex_jinja_env = j2.Environment(
            block_start_string=r'\BLOCK{',
            block_end_string=r'}',
            variable_start_string=r'\VAR{',
            variable_end_string=r'}',
            comment_start_string=r'\#{',
            comment_end_string=r'}',
            line_statement_prefix=r'%%',
            line_comment_prefix=r'%#',
            trim_blocks=True,
            lstrip_blocks=True,
            autoescape=False,
            # Pfad des Ordners, in dem diese Datei (converter.py) liegt.
            loader=j2.FileSystemLoader(
                os.path.dirname(os.path.abspath(__file__)))
        )
        #  Template laden
        return self.latex_jinja_env.get_template(templatePfad)

    def konvertiere(self, lied: str) -> str:
        ''' Diese Funktion erledigt die Konvertierungsarbeit für ein einzelnes Lied.
            lied: [str] Inhalt der Datei '''
        lied = lied.split('\n')  # in zeilen zerlegen
        # Jeder zeile die beiden wahrscheinlichsten typen zuordnen
        typen = Heuristik(lied)
        # Klasse zum einfachen zeilenweisen verwalten der Daten
        zeilen = SongKonverter.finde_zeilentypen(SongLaTexttype(typen))
        # In Blöcke (Überschrift, Strophen, etc.) teilen.
        bloecke = zeilen.split('Leer')
        # Jeder Block entspricht einem Liedblock, also Liedtext/Akkorde, Überschrift oder Info
        # alle Blöcke, die in den latex Code übertragen werden werden in der liste inhalt gesammelt.
        inhalt = list()
        # info enthält informationen zum Lied, falls angegeben.
        info = False

        # Speziell für den Titelblock
        titel = ''  # wenn dieser titel nicht ersetzt wird, ist etwas falsch...
        # titel, Worte, Weise, alternativtitel, genre, tags, etc.
        metadaten = dict()

        # Jeden Block für die Ausgabe durch jinja2 vorbereiten
        for i in range(len(bloecke)):
            block = bloecke[i]
            # Der erste block enthält die Überschrift und alle metadaten und wird deshalb gesondert behandelt.
            if i == 0:
                # Erster Block: Hier sollte die Überschrift und die metadaten stehen.
                # Wenn der erste block keine Überschrift ist,
                if ('Überschrift' not in block.types()):
                    # gibt das kein sinnvolles Ergebnis.
                    print('Keine Überschrift gefunden', block, file=sys.stderr)
                    raise Exception()
                metadaten = SongKonverter.meta_aus_titel(block)
                # Benutzerdefinierte formatierungen an dem Metadaten:
                metadaten = config.formatMeta(metadaten)
                titel = metadaten.pop('title')

            else:
                # für latex konvertieren
                block.erstelleLatexDaten()
                if block.blocktyp == "info":
                    info = block
                    continue
                elif info != False: #Es wurde bereits ein Infoblock gefunden, aber danach gibt es noch andere Blöcke.
                    #Das wird im momemtn nicht so dargestellt, gebe eine Warnung aus.
                    print("Infoblöcke werden im moment nur am ende des Liedes unterstützt.", file=sys.stderr)
                inhalt.append(block)

        return self.templateFuellen(titel, metadaten, inhalt, info)

    @staticmethod
    def finde_zeilentypen(zeilen: texttype) -> texttype:
        # XXX: Hier kann man auch eine Simple Grammatik implementieren
        # Für jede Zeile den Wahrscheinlichsten typ wählen
        for zeilenNr in range(len(zeilen)):
            zeilentypen = zeilen.choices(zeilenNr)
            if zeilentypen[0] is None:
                if len(zeilentypen) > 1 and zeilentypen[1] is not None:
                    print('typ von zeile', zeilenNr,
                          'konnte nicht ermittelt werden. es wird \"'+zeilentypen[1]+'\" angenommen', file=sys.stderr)
                    zeilen.choose(zeilenNr, zeilentypen[1])
                else:
                    print('typ von zeile', zeilenNr,
                          'konnte nicht ermittelt werden. es wird \"Leer\" angenommen', file=sys.stderr)
                    zeilen.choose(zeilenNr, 'Leer')
                continue
            zeilen.choose(zeilenNr, zeilentypen[0])
        return zeilen

    @staticmethod
    def meta_aus_titel(block: texttype) -> Dict[str,str]:
        # Aufbau des Titelblockes: TITEL [Alternativtitel1]
        # key: value
        # …
        
        # text, wie in der Eingabedatei, zeilenweise als liste, nur dieser Block
        text = str(block).split('\n')
        # Marker:
        titelz = text[0]
        metatext = text[1:]
        lk = titelz.find('[')
        rk = titelz.find(']', lk)
        # Wenn das Zeichen nicht gefunden wurde:
        # Wenn das zeichen '[' nicht gefunden wird, gibt find() -1 zurück.
        # Das führt zu dem Problem, dass das Minimum (siehe unten)
        # den wert -1 hat (offset von 1 vom Ende des Strings).
        # Dadurch fehlt das letzte zeichen des Titels, wenn nichts dahinter kommt.
        # Setze die Zeichenposition in diesem Fall auf das len(text)-te Zeichen
        # des Textes. Diese Position kann zwar nicht gelesen werden, das passiert
        # aber auch nicht. Es löst das Problem
        if lk <= 0:
            lk = len(titelz)

        # metadaten dictionary
        meta = dict()
        # Titel finden:
        meta['title'] = titelz[:min((lk, len(titelz)))].strip()
        # alternativtitel finden
        if rk > lk:
            meta['index'] = titelz[lk + 1:rk].strip()

        # restliche metadaten:
        # Hier weden alle metadaten gelistet, die in der überschrift enthalten sein können
        from config.metakeys import metakeys 

        for line in metatext:
            if ':' in line:
                # davor ist der schlüssel, danach der wert
                i = line.index(':')  # in [0, len(ll)-1]
                keystr = line[:i].lower().replace(' ', '')
                # schlägt fehl wenn der wert nicht angegeben wird.
                valstr = line[i+1:].strip()
                if keystr in metakeys.keys():
                    key = metakeys[keystr]
                    meta[key] = valstr
                else:
                    # das sollte nicht passieren
                    print('ungültiger schlüssel:', keystr, file=sys.stderr)
            else:
                if line == '':
                    # die Zeile ist leer. Kein Problem, wird nicht verarbeitet, passiert ggf bei der letzten zeile des Titelblockes
                    pass
                else:
                    print('Falsch Formatierte metazeile:', line, file=sys.stderr)
        return meta

    konvertiere.__doc__ = '''lied: Ein string, der ein ganzes lied enthält. 
        Siehe hierzu die Dokumentation für Lieder im Eingabeverzeichnis. 
        Die funktion konvertiert das lied in latex. die ausgabe ist ein latex-dokument 
        das das lied darstellt.'''

    def templateFuellen(self, title: str, metadaten: Dict[str, str], inhalt: List[SongLaTexttype], info:SongLaTexttype) -> str:
        '''füllt das jinja2-template mit den metadaten uund dem Inhalt
        erlaubte Schlüssel für metadaten: index, wuw, mel, txt, meljahr, txtjahr, alb, lager, ...'''
        return self.template.render(title=title, metadata=metadaten, inhalt=inhalt, info=info)

    __doc__ = 'Erlaubt das konvertieren von Liedern in textform in Latex_dokumente'
