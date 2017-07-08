#!/usr/bin/env python
import sys, re

legit_chords = ["A","B","H","C","C#","D","C#","E","F","F#","G","G#"]
legit_chords += [chord+"m" for chord in legit_chords]
legit_chords += ["Cadd9","Dsus4","Dsus2"]

def isChordLine(line):
    # criteria: more than half of the words are legit chords
    chord_count = sum([c in legit_chords for c in line.split()])
    # sys.stderr.write("{} / {} chords are legit: {}\n".format(chord_count, len(line.split()), line))
    if chord_count > 0 and float(chord_count) / len(line.split()) > 0.5: 
        return True

    return False
    
def getChordLocations(line):
    chords = []
    for m in re.finditer(r'\S+', line):
        index, chord = m.start(), m.group()
        chords.append((index, chord))
    return chords

def mergeChordsAndLine(chords, line):
    positions = [0] + [chord[0] for chord in chords] + [len(line)]
    inserts = ["\["+chord[1]+"]" for chord in chords]
    parts = [line[i:j] for i, j in zip(positions[:-1], positions[1:])]
    merged = [item for pair in zip(parts, inserts) for item in pair] + [parts[-1]]

    return "".join(merged)

if __name__ == "__main__":
    
    for line in sys.stdin:
        if isChordLine(line):
            chords = getChordLocations(line)
            lyrics = sys.stdin.next()
            
            chordline = mergeChordsAndLine(chords, lyrics)
            sys.stdout.write(chordline)
        else:
            sys.stdout.write(line)
            pass
    
    