#! /usr/bin/env python3
# Listet Lieder nach beliebiger Sortierung auf. Durch die möglichkeit eines Prefixes und Suffixes ist es möglich, direkt \input{} statements für die Dateien zu erzeugen.
import argparse
from typing import Tuple, List, Dict, Union
import os
import sys

#header and footer for the output file
generated_head = """\documentclass{book}

\\providecommand{\\bookname}{Pfadiralala IV: Complete Sorted Edition}

\\input{Misc/basic}

% different spacing
\\versesep=10pt plus 2pt minus 4pt
\\afterpreludeskip=2pt
\\beforepostludeskip=2pt

\\newindex{Seitenzahlen}{Ausgaben/CompleteEdition}
\\indexsongsas{Seitenzahlen}{\\thepage}

\\begin{document}
	\\begin{songs}{Seitenzahlen}

		\\showindex[2]{Inhaltsverzeichnis}{Seitenzahlen}"""
generated_foot = """
	\\end{songs}
\\end{document}"""


"Unter einen Lied wird hier eine Textdatei im Latexformat verstanden, das nichts außer (genau) einem Lied entsprechend des songs-Packets enthält. Die Datei beginnt also mit \\begin{song}… und endet mit \\end{song}"

argParser = argparse.ArgumentParser(description="sortiert die eingegebenen Lieder (tex-Format) nach den Metadaten. Fügt einen Dateikopf und einen Dateifuß hinzu, sodass ein komplettes Latex-Dokument als Ausgabe entsteht.")
argParser.add_argument('-b', '--by', action="append", help="Schlüssel, nach dem sortiert werden soll. Wird die die Option mehrfach spezifiziert, finden die Sortierungen in der angegebenen Reihenfolge statt. \nGültig sind alle Schlüssel, die in den Metadaten angegeben werden können. Außerdem \"titel\", um nach dem Titel zu sortieren. \"wuw\" (Worte und Weise) wird in \"txt\" und \"mel\" übertragen, falls ersteres gesetzt und letztere jeweils nicht gesetzt sind. Der Schlüssel \"index\" wird mit dem Wert des Titels versehen, falls er nicht existiert. Weiterhin gibt es die Möglichkeiten \"name\" (sortiert nach dem Dateinamen) und \"pfad\" (sortiert nach dem absoluten Pfad). \nKommt ein Schlüssel in einer Datei mehrfach vor (z.B. mehrere index-Einträge), wird der zuletzt angegebene Wert zur Sortierung herangezogen.")
argParser.add_argument('-p', '--root', action="store", default=None, nargs="?", const=".", help="Wurzelverzeichnis für die Ausgabe von Pfaden. Standardmäßig findet keine Veränderung statt. Wird die Option ohne Angabe eines Pfades verwendet, wird das aktuelle Verzeichnis (.) gewählt")
argParser.add_argument('--prefix', action="store", default="\t\t\input{", help="fügt ein Prefix vor jedem ausgegebenen Dateipfad ein. (Standard ist \"\t\t\input{\")")
argParser.add_argument('--suffix', action="store", default="}", help="fügt ein Suffix nach jedem ausgegebenen Dateipfad ein. (Standard ist \"}\")")
argParser.add_argument('files', action="extend", nargs="+", help = "Die sortiert aufzulistenden Dateien. Wenn Fehler, zum Beispiel aufgrund eines falschen Formats auftreten, sind die fehlerhaften Dateien nicht in der Ausgabe enthalten.")


class SortierbaresLied():
	def __init__(self, pfad):
		self.pfad = pfad
		self.inhalt = None
		self.meta = None

	def lesen(self):
		with open(self.pfad, "r") as file:
			self.inhalt = file.read()

	def getMeta(self):
		self.meta = MetaFinder.lese_meta(self, MetaFinder.finde_meta_indicees(self))

	def __str__(self):
		if not self.meta:
			self.getMeta()
		return self.pfad + "\n\t".join(key + ' = ' + self.meta[key] for key in self.meta.keys())


class MetaFinder():
	@staticmethod
	def finde_meta_indicees(lied: SortierbaresLied) -> Tuple[str]:
		# Findet die string indecees von Angang und Ende des Titels bzw. des Metastrings
		if lied.inhalt is None:
			lied.lesen()
		# Die zu findenden steuerzeichen
		search = [r"\beginsong", "{", "}", "[", "]"]
		searchindex = 0  # index des aktuell zu suchenden steuerzeichens
		start = 0       # index, bei dem die Suche beginnt
		starttitle = -1  # Index des Zeichens, bei dem der Titel anfängt
		endtitle = -1   # Index des Zeichens, bei dem der Titel aufhört
		startmeta = -1 	# Index des Zeichens, bei dem der Metablock anfängt
		endmeta = -1    # Index des Zeichens, bei dem der MEtablock aufhört
		while searchindex < len(search):
			finding = lied.inhalt.find(search[searchindex])
			if finding == -1:  # nichts gefunden
				raise Exception("format error: " + search[searchindex] + " not found")
			else:  # wert von search gefunden
				if searchindex == 0:  # \beginsong
					pass
				elif searchindex == 1:  # { (Anfang des titels)
					# Durch diese Addition ergibt lied.inhalt[starttitle:endtitle] den Titel ohne Steuerzeichen
					starttitle = finding + 1
				elif searchindex == 2:  # } (Ende des Titels)
					endtitle = finding
				elif searchindex == 3:  # [ (begin der Metadaten)
					# Durch diese Addition ergibt lied.inhalt[startmeta:endmeta] den Metastring ohne Steuerzeichen
					startmeta = finding + 1
				elif searchindex == 4:  # ] (ende der Metadaten)
					endmeta = finding
				else:  # Der searchindex hat einen seltsamen Wert angenommen
					raise Exception("This should never happen")

			searchindex += 1
			start = finding

		return (starttitle, endtitle), (startmeta, endmeta)

	@staticmethod
	def lese_meta(lied: SortierbaresLied, indicees: Tuple[Tuple[int, int], Tuple[int, int]]) -> Dict[str, str]:
		# erstellt ein dictionary der metadaten des Lieds

		meta = MetaFinder.dateiname_zu_meta(lied)

		# Inhalt lesen, falls noch nicht geschehen
		if lied.inhalt is None:
			lied.lesen()

		# Indezees auspacken
		(starttitle, endtitle), (startmeta, endmeta) = indicees
		# Titel extrahieren. Das ist einfach
		meta["titel"] = lied.inhalt[starttitle: endtitle]

		# Metasting extrahieren:
		# einzelne Metaangaben sind durch Kommata getrennt. Sie haben das Format <key>=["{"]<value>["}"],
		# funktioniert nicht, wenn der string escapte endmeta-zeichen enthält (z.B. \}, wenn endmeta } ist).
		metastrings = lied.inhalt[startmeta: endmeta].split(',')

		for m in metastrings:
			# findet das Trennzeichen zwischen schlüssel und wert.
			sepIndex = m.find('=')

			if sepIndex == -1:
				continue  # Trennzeichen nicht gefunden; kein metastring hier

			schluessel = m[: sepIndex]
			schluessel = schluessel.strip(" \n\r\t")
			if len(schluessel) == 0:
				continue

			wert = m[sepIndex+1:]
			wert = wert.strip(" \n\r\t{}")

			meta[schluessel] = wert
		return meta

	@staticmethod
	def dateiname_zu_meta(lied: SortierbaresLied) -> Dict[str, str]:
		meta = dict()
		meta["pfad"] = str(os.path.abspath(lied.pfad))
		meta["name"] = str(os.path.basename(lied.pfad))

		return meta



def sort(sortierbareLieder: List[SortierbaresLied], by:Union[List[str], str], default:str="") -> List[SortierbaresLied]:
	# sortiert die Lieder nach mehreren Schlüsseln. Die Sortierung findet inplace statt. wenn ein Schlüssel nicht existiert, wird def default wert verwendet.
	if type(by) is str:
		by = [by,]

	for sortKey in by:
		#sortiere nach dem Sortierschlüssel. Die sort-Methode ist stabil, daher kann man nach mehreren schlüsseln sortieren.
		sortierbareLieder.sort(
				key = lambda sortierbaresLied: sortierbaresLied.meta.get(sortKey) if sortKey in sortierbaresLied.meta.keys() else default
			)
	return sortierbareLieder


def pfad_umschreiben(pfad:str, root:Union[str,None]='.') -> str:
	if root is None:
		return pfad
	else:
		return os.path.relpath(os.path.abspath(pfad), start=os.path.abspath(root))


if __name__ == '__main__':
	args = argParser.parse_args()
	files = args.files
	#print("ARGS:", args)

	# sortierbare objekte anlegen
	lieder = []
	for file in files:
		try:
			lied = SortierbaresLied(file)
			lied.getMeta()
			# WUW tag umschreiben:
			if "wuw" in lied.meta.keys():
				if "mel" not in lied.meta.keys():
					lied.meta["mel"] = lied.meta["wuw"]
				if "txt" not in lied.meta.keys():
					lied.meta["txt"] = lied.meta["wuw"]
			#anfang tag setzten, falls er nicht existiert
			if "anfang" not in lied.meta.keys():
				lied.meta["anfang"] = lied.meta["titel"]

			lieder.append(lied)
		except:
			print("Fehler bei Lied " + str(file), file=os.sys.stderr)

	lieder = sort(lieder, by=args.by)

	print(generated_head)
	for i in range(len(lieder)):
		print(args.prefix + pfad_umschreiben(lieder[i].pfad, args.root) + args.suffix)
	print(generated_foot)
