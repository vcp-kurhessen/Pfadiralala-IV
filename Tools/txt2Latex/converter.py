#!/usr/bin/env python3
# -*- coding: utf-8 -*-
'''
Created on Mon Mar  9 22:27:10 2020

@author: Paul Steuernagel
'''

from typing import Collection, Set, Union
from song_converter import SongKonverter
import sys
import os
import typing

# typing: Pfadspezifikation:
pfad = typing.Union[str, os.DirEntry]

insuffixes = {'.txt', '.lied'}
outsuffix = '.tex'
templatePfad = 'Template.jinja'


def get_dir_content(directory:pfad) -> Set[os.DirEntry]:
    # Gibt den Inhalt eines Verzeichnisses zurück
    with os.scandir(directory) as listing:
        return set(listing)


def get_files(dir_content:Set[pfad])-> Set[pfad]:
    #Gibt alle Pfade zurück, die Dateien entsprechen.
    return set(elem for elem in dir_content if elem.is_file)


def get_accessable(dir_content:Set[pfad], access=os.R_OK) -> Set[pfad]:
    # Gibt diejenigen Pfade zurück, auf die lesend / schreibend / ausführend (abhängig von access)
    #    zugegriffen werden kann.
    return set(elem for elem in dir_content if os.access(elem, access))


def filter_suffix(dir_content:Set[pfad], suffix:Union[str, Collection[str]]):
    # Gibt alle Dateien in dir_content zurück, die auf das bzw. eines der Suffix/e endet.
    erg = set()
    if type(suffix) == str:
        suffix = set((suffix, ))
    for file in dir_content:
        for suf in suffix:
            if file.name.endswith(suf):
                erg.add(file)
                break
    return erg


def get_inaccessable(dir_content:Set[pfad], access=os.R_OK) -> Set[pfad]:
    # Gibt alle dateien zurück, auf die nicht lesend [schreibend/ausführend] (abhängig von access)
    #     zugegriffen werden kann.
    return set.difference(dir_content, get_accessable(dir_content, access))


def get_outfilename(infilename:str, outending:str, inendings:Collection[str]) -> str:
    '''bestimmt einen Dateinamen für die Ausgabe
    outending ist die gewünschte endung der ausgabe, Endungen in inending werden entfernt'''
    for end in inendings: # Dateiendung kürzen
        if infilename.endswith(end):
            infilename = infilename[:len(infilename)-len(end)]
            break
    return infilename + outending #Dateiname für die Ausgabe


def readfile(filename:pfad, mode='r') -> str:
    # Liest den gesamten inhalt der Datei
    chunksize = 10000 # Anzahl der Zeichen, die auf einmal gelesen werden.
    data = ''
    with open(filename, mode) as file:
        while 1:
            newdata = file.read(chunksize)
            data += newdata
            if len(newdata) < chunksize: # wurde das Ende der Datei erreicht? 
                break
    return data


def writefile(filename:pfad, data:str, mode='w')->int:
    with open(filename, mode) as file:
        chars_written = file.write(data)
        if chars_written != len(data):
            return 1
    return 0


def build_path(directory:pfad, filename:str)-> pfad:
    return os.path.join(directory, filename)


def convertFile(infile:pfad, outfile: pfad, moreOutput:bool)-> None:
        # Datei laden
        if moreOutput: print(infile.name.rjust(30), ' lesen… ', end='')
        else: print('   '+infile.name)
        indata = readfile(infile)
        # Datei Konvertieren
        if moreOutput: print(' umwandeln… ', end='')
        outdata = konverter.konvertiere(indata)  # multithreading nötig/möglich?
        # Datei speichern
        if moreOutput: print(' speichern… ', end='')
        writefile(outfile, outdata)
        if moreOutput: print('fertig')


def getInfiles(directory:pfad) -> Set[pfad]:
    return get_accessable(filter_suffix(get_files(get_dir_content(directory)), insuffixes), os.R_OK)


def fileIsWriteable(datei:pfad, allow_overwrite=False) -> bool:
    # datei kann geschrieben werden und (es darf überschrieben werden oder die datei existiert nicht.)
    if os.path.exists(datei):
        # der pfad existiert.
        if os.path.isfile(datei) and allow_overwrite:  # ist es eine datei und ist überschreiben erlaubt
            # funktioniert auch für verknüpfungen, deren ziel schreibbar ist
            return os.access(datei, os.W_OK) 
        else:
            return False  # es handelt sich um ein verzeichnis oder wir dürfen nicht überschreiben(das heißt nicht, dass es nicht möglich wäre) 
    # datei existier nicht. Überprüfe schreibrechte im Ordner
    pdir = os.path.dirname(datei)
    if not pdir:
        pdir = '.'
    # Die datei kann erzeugt werden, falls in das verzeichnis geschrieben werde kann.
    return os.access(pdir, os.W_OK)

def rewriteFilename(dateiname:str) -> str:
    # Beschränkt den Dateinamen auf die Zeichen A-Z a-z 0-9 .-_+ (ohne Leerzeichen)
    # alle anderen Zeichen werden gelöscht.
    # Falls das erste Zeichen nach einem gelöschten Zeichen ein kleinbuchstabe ist, 
    # wird er zu einem GROSSBUCHSTABEN umgewandelt.
    # Dalls das erste ZEichen ein kleinbuchstabe ist, wirt der zu einem GROSSBUCHSTABEN
    # umgewandelt
    
    def konvertiereZeichen(zeichen:str, gross=False) -> str:
        # gibt das Zeichen zurück, falls das es in der Gruppe A-Z a-z 0-9 .-_+ ist.
        # konvertiert äöüß, alle anderen zeichen werden gelöscht
        # bestimme die nummer im unicode-zeichensatz
        # Mit gross=True werden kleinbuchstaben zu großbuchstaben konvertiert.

        if zeichen.isdigit(): # 0-9
            return zeichen
        
        #konvertieren Umlaute
        if zeichen=='ä':
            zeichen = 'a'
        if zeichen=='Ä':
            zeichen = 'A'
        if zeichen=='ö':
            zeichen = 'o'
        if zeichen=='Ö':
            zeichen = 'O'
        if zeichen=='ü':
            zeichen = 'u'
        if zeichen=='Ü':
            zeichen = 'U'
        if zeichen=='ß':
            zeichen = 's'
        
        nr = ord(zeichen)
        if nr >= 65 and nr <= 90: #Großbuchstabe
            return zeichen
        if nr >= 97 and nr <= 122: #kleinbuchstabe
            if gross:
                return zeichen.upper()
            return zeichen
        if zeichen in ".-_+":
            return zeichen
        return ''

    neuerName = ''
    naechsterGross=True
    for buchstabe in dateiname:
        neuerBuchstabe = konvertiereZeichen(buchstabe, naechsterGross)
        if neuerBuchstabe != '':
            naechsterGross = False
        else:
            naechsterGross = True
        neuerName += neuerBuchstabe
    return neuerName



if __name__== '__main__':
    # Aufrufparameter lesen
    moreOutput = False
    overwrite = False
    rewriteFilenames = False
    if len(sys.argv) >= 3:
        indir, outdir = sys.argv[-2:]
        # TODO: Wie liest man am einfachsten mehrere Argumente in der Form -oav statt -o -a -v
        if len(sys.argv) > 3 and '-o' in sys.argv[1:-2]:
            # Überschreiben ist erlaubt
            overwrite = True
        if len(sys.argv) > 3 and '-a' in sys.argv[1:-2]:
            # jede Datei soll konvertiert werden
            insuffixes.add('')
        if len(sys.argv) > 3 and '-v' in sys.argv[1:-2]:
            # mehr ausgabe
            moreOutput=True
        if len(sys.argv) > 3 and '-r' in sys.argv[1:-2]:
            # mehr ausgabe
            rewriteFilenames=True
    else:
        print('''Benutzung: converter.py [-o] [-a] [-v] Eingabeverzeichnis Ausgabeverzeichnis
            Konvertiert Lieder aus EINGABEVERZEICHNIS und speichert die Latexversion in AUSGABEVERZEICHNIS.
            Dabei werden nur Dateien verarbeitet, die auf .txt oder .lied enden.
            
            OPTIONEN:
            -o  Überschreibe vorhandene Dateien im Zielverzeichnis
            -a  alle Dateien verarbeiten (unabhängig vom suffix)
            -v  mehr Ausgabe
            -r  Dateinamen umschreiben: entfernt alle Leer- und Sonderzeichen 
                und schreibt den ersten Buchstaben jedes Wortes groß.''', file=sys.stderr)
        sys.exit(1)
    if not (os.path.isdir(indir)):
        raise Exception('dirctory "'+indir+'" not found')
    if not (os.path.isdir(outdir)):
        raise Exception('dirctory "'+outdir+'"not found')

    # Dateien, die gelesen werden können
    infiles = getInfiles(indir)

    # Konverter laden:
    konverter = SongKonverter(templatePfad=templatePfad)
    
    # Jetzt konvertieren wir die einzelnen Dateien:
    # zunächst wird der Dateiname und der Pfad für die Ausgabe festgelegt.
    for infile in infiles:
        outfilename = get_outfilename(infile.name, outsuffix, insuffixes) # Dateiname für die Ausgabe
        # Dateiname ggf umschreiben
        if rewriteFilenames:
            outfilename = rewriteFilename(outfilename)

        outpath = build_path(outdir, outfilename)     # Ausgabepfad

        # Prüfen, ob Ausgabedatei geschrieben werden kann / darf.
        if not fileIsWriteable(outpath, overwrite):
            print(outfilename, ' darf nicht überschrieben werden. ', infile.name, ' wird übersprungen.', file=sys.stderr)
            continue # Datei überspringen
        
        try:
            convertFile(infile, outpath, moreOutput)
        except Exception as e:
            print('FEHLER bei Datei', infile, e, file=sys.stderr)
