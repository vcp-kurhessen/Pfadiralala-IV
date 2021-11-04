# Konfiguration: Benötigt von lib/texttype/SongLaTexttype
from typing import List, Dict
# l: Mollakkorde in Kleinbuchstaben, m: mit m (e-> Em), (Leer): Keine Änderung
Akkordstil = 'm'

# Reguläre Ausdrücke, mit denen die verschiedenene Teile der Lieder identifiziertz werden können-
STROPHENREGEX = r'^\s?\d+([).:]|( :))*\s*' # Nummern für die Strophen
REFRAINREGEX = r'^\s?Ref(rain)?[).: ]+\s*' # Bezeichnung des Refrains
INFOREGEX = r'^\s?@?info((:\s*)|\s+)'      # Bezeichnung des Infoblockes

AKKORDREGEX = r'\S+' # muss einfach nur alles fressen, was möglicherweise ein Akkord sein könnte.

#regulärer Ausdruck für ZEilen, die nur Akkorde enthalten (spezifisch, soll nicht auf normalen Text passen)
akkord_zeilen_regex = r'( *([:|]+|(\(?([A-Ha-h](#|b)?(sus|dim|add|m(aj)?)?\d*)(\/([A-Ha-h](#|b)?(sus|dim|add|maj)?\d*))*\)?)))+ *'
#regulärer Ausdruck für einen Akkord (spezifisch, soll nicht auf normalen Text passen)
akkord_regex = r'(\(?([A-Ha-h](#|b)?(sus|dim|add|m(aj)?)?\d*)(\/([A-Ha-h](#|b)?(sus|dim|add|maj)?\d*))*\)?)'

#WDHLREGEX = r'[/|]{1,2}\:' #Im Moment nicht Verwendet
#WDHRREGEX = r'\:[/|]{1,2}' #Im Moment nicht Verwendet

# Liste der ersetzungen, die in den zeilen passieren soll
Ersetzungen = []
#Formatierungen: bevor und nachdem die Akkorde mit dem Text zusammengesetzt werden, können Formatierungen am Text vorgenommen werden. 
# beim zusammensetzen werden Text und Akkorde in eine Zeile geschrieben. Änderungen, die an den Akkordzeilen geschen, sollten also vorher gemacht werden. 
# Alle änderungen, die den Text ändern, danach stattfinden, da sich sonst die Akkorde verschieben.
#Eingabe und ausgabe sind Listen, die einen String für jede zeile enthalten.

def _WdhErsetzungen(line: str) -> str:
    """ erseetzt wiederholungen durch den dazugehörigen Latexbefehl"""
    # Stelle sicher, dass nach \lrep bzw. \rrep ein leerzeichen folgt. auch wenn es in der eingabe vergessen wurde.
    return line.replace("||:", r" \lrep ").replace("|:", r" \lrep ").replace(":||", r" \rrep ").replace(":|", r" \rrep ") #TODO: das geht schöner

#sollte ursprünglich umlaute ersetzen, tatsächlich sind wegen \usepackage{inputenc} im allgemeinen keine nötig
_UmlErsetzungen = { #"ä":r'{\"a}',
                    #"ö":r'{\"o}',
                    #"ü":r'{\"u}',
                    #'Ä':r'{\"A}',
                    #'Ö':r'{\"O}',
                    #'Ü':r'{\"U}'
                    }
#ersetzungen für Sonderzeichen
_ZeichenErsetzungen = { "&":r'{\&}',
                    "’":"'", #typographische Apostrophe und accents
                    "´":"'",
                    "`":"'",
                    "\"":r"{\dq}",
                    }
def _UmlErsetzen(line:str) -> str:
    """ ersetzt umlaute und Sonderzeichen durch latex-befehle bzw. Äquivalente"""
    for orig, new in _UmlErsetzungen.items():
        line = line.replace(orig, new)
    return line

def _ZeichenErsetzen(line:str) -> str:
    """ ersetzt umlaute und Sonderzeichen durch latex-befehle bzw. Äquivalente"""
    for orig, new in _ZeichenErsetzungen.items():
        line = line.replace(orig, new)
    return line


# Formatierungen am Refrain, die vor der Konvertierung der Akkorde durchgeführt werden:
def preFormatRef(text: List[str]) -> List[str]:
    return text

# Formatierungen am Refrain, die nach der Konvertierung der Akkorde durchgeführt werden:
def postFormatRef(text: List[str]) -> List[str]:
    for i in range(len(text)):
        text[i] = _WdhErsetzungen(text[i])
        text[i] = _UmlErsetzen(text[i])
        text[i] = _ZeichenErsetzen(text[i])
    return text

# Formatierungen an den Strophen, die vor der Konvertierung der Akkorde durchgeführt werden:
def preFormatVers(text: List[str]) -> List[str]:
    return text

# Formatierungen an den Strophen, die nach der Konvertierung der Akkorde durchgeführt werden: 
def postFormatVers(text: List[str]) -> List[str]:
    for i in range(len(text)):
        text[i] = _WdhErsetzungen(text[i])
        text[i] = _UmlErsetzen(text[i])
        text[i] = _ZeichenErsetzen(text[i])
    return text

# Formatierungen Am Infotext; hier werden keine Akkorde gesetzt, daher gibt es nur eine Funktion.
def formatInfo(text: List[str]) -> List[str]:
    for i in range(len(text)):
        text[i] = _UmlErsetzen(text[i])
        text[i] = _ZeichenErsetzen(text[i])
    return text

# Formatierungen Titel und Liedanfang
def formatTitel(text: List[str]) -> List[str]:
    for i in range(len(text)):
        text[i] = _UmlErsetzen(text[i])
        text[i] = _ZeichenErsetzen(text[i])
    return text

# Formatierungen anderen TExtbasiertzen MEtadaten(z.B. Autor, Album, etc.)
def formatMeta(meta: Dict[str,str]) -> Dict[str,str]:
    """erlaubt die Umformatierung der MEtadaten. 
    Aktuell werden nur Sonderzeichn durch latex-kompatible ersetzt. natürlich ist hier noch mehr möglich."""
    for metakey in meta.keys():
        meta[metakey] = _UmlErsetzen(meta[metakey])
        meta[metakey] = _ZeichenErsetzen(meta[metakey])
    return meta

Umgebungen = {  # Definiert die start- und endkommandos für die verwendeten latex-Umgebungen
    'standart': (r'\beginverse*',      r'\endverse'),# wird verwendet, falls aus irgendeinem Grund kein anderer passt.
    'strophe*':   (r'\beginverse*',      r'\endverse'),
    'strophe':    (r'\beginverse',       r'\endverse'),
    'refrain':   (r'\beginchorus',      r'\endchorus'),
    # HACK: Die Wiederholung des Refrain nutzt keine Umgebung. Erzeugt wird eine Umgebung ohne Inhalt und endstring. Das ist ein einzelnes Kommando.
    'refrainWdh': (r'\printchorus',      r''),
    'info':     (r'\beginscripture{}', r'\endscripture')
}
