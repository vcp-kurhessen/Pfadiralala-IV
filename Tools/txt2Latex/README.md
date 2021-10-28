# txt2latex

Konvertiert Lieder aus Textdateien in Latex.
Die Ausgabe ist kompatibel mit dem Latex-Packet leadsheets.

## Installation:
Diese Software verwendet Python3. python3 kann auf [www.python.org](www.python.org/downloads/) heruntergeladen werden.

Außerdem wird die Bibliothek jinja2 benötigt:
`$ pip3 install jinja2`

## Verwendung:
Der Konveriterung wird gestartet mit
```$ python3 converter.py [-o] [-a] [-r] [-v] <Eingabeverzeichnis> <Ausgabeverzeichnis>```

Das Programm liest alle Dateien im Eingabeverzeichnis und erstellt für jede Datei `Name.txt` eine Datei `Name.tex` im Ausgabeverzeichnis, die den dazugehörenden Latex code enthält. Standartmäßig werden nur Dateien verarbeitet, die auf `.txt` oder `.lied` enden.

Die Option `-o` erlaubt das Überschreiben von Dateien im Ausgabeverzeichnis, falls nötig. 
Die Option `-a` deaktiviert den Dateinamenfilter. Es werden alle Dateien unabhängig vom Suffix verarbeitet
Die Option `-r` entfernt Sonderzeichen und Leerzeichen aus dem Dateinamen. (nützlich, falls die Datei hinterher in Skripten verwendet werden soll)
Die Option `-v` erzeugt zusätzliche Ausgabe.


### Eingabedateien:
Zum Besseren Verständnis der Syntax der Eingabe gibt es im Ordner "Beispiele" eine Daten mit dem Namen "Skellett.txt". Diw wesentlichen Elemente der Syntax sind darin zu erkennen.

Eine Eingabedatei enthält genau ein Lied. Sie besteht aus mehreren durch Leerzeilen voneinanader getrennen Absätzen, im Folgenden "Blöcke" genannt.

Der erste Block ist der Kopf des Liedes. Er kann nicht weggelassen werden und unterscheidet sich stark von allen anderen Blöcken. Alle weiteren Blöcke sind optional und enthalten das Lied selbst, sowie ggf. Zusatzinformationen zu den Lied. 

#### Kopf:
Der Kopf des liedes enthält alle Metadaten des Liedes. Dazu zählen:

* Titel des Liedes
* Name für die Sortierung
* Autoren von Melodie und Text
* Jahr, in dem die Melodie bzw. der Text entstanden sind
* Album (für Lieder von Bands)
* Lager (auf dem / für das das Lied geschrieben wurde)
* Tonart des Liedes
* Seitenzahlen in verschiedenen Liederbüchern

 Die erste Zeile des Kopfes sieht hat die folgende Syntax:
 
 ``` 
 Titel des Liedes [Name für die Sortierung]
 ```
 Die Angabe des Titels ist notwendig. die Angabe des Namens für die Sortierung ist im Moment optional, das kann sich aber in Zukunft ändern. Es wird empfohlen, hier den Ersten Vers, bzw. einen Teil des ersten Verses einzutragen.
 
Alle weiteren Metadaten werden im Format

 `schlüssel: Wert`
 
angegeben. Die erlaubten Schlüssel sind in [Beispiele/Skellett.txt] aufgeführt. Bei der Angabe der Schlüssel ist die Groß- Klein-Schreibung egal. Die Werte werden im allgemeinen 1:1 in das Ausgabedokument übernommen (für details siehe die Konfiguration im Ordner config). Pro Zeile ist dabei ein paar aus schlüssel und Wert erlaubt.
 
Der Kopf endet, wie alle anderen Blöcke auch mit einer Leerzeile. Eine Leerzeile ist eine Zeile, die keinen Inhalt hat (auch keine Leerzeichen).
 
#### Inhalt des Liedes:
Der Inhalt des Liedes wird zumeist durch mehrere Blöcke dargestellt. Ein Block ist dabei ein zusammenhängendes stück Lied, das man in einem Liederbuch zusammenhängend aufschreiben würde. Zum Beispiel: eine Strophe, der Refrain oder das Vorspiel. Das Ziel der Entwicklung war hier, Lieder die bereits als Textdateien vorliegen, mit möglichst wenig Aufwand konvertieren zu können. Außerdem sollten die Eingabedateien auch für Menschen gut lesbar sein, sodass das Lied gespielt und korrigiert werden kann, ohne das Liederbuch vollständig zu bauen. Es gibt drei verschiedene Möglichkeiten, einen Inhaltsblock zu schreiben:

* Akkorde und Text
* Nur Akkorde
* Nur Text

##### Akkorde und Text
In den meisten Fällen wird wenigstens ein Inhaltsblock im Stil _Akkorde und Text_ sein. in diesem Fall werden für jeden Vers zwei Zeilen verwendet. Zuerst die Akorde und in der nächsten Zeile der Text:

```  
     Em                    G        D        e         D
Ich ging eines Morgens so für mich hin im Julisonnenschein
```

Hierbei ist zu beachten, dass zwischen den Akkorden nur Leerzeichen stehen dürfen, der Tabualtor kann **nicht** verwendet werden. Das hat den Hintergrund, dass der Tabulator eine variable Länge hat, die das anzeigende Programm frei festlegen kann. Deshalb kann nicht sichergestellt werden, dass die Tabualtoren genau so breit sind wie im verwendeten Texteditor. Die Akkorde würden verrutschen und das Lied wäre nicht mehr spielbar.

Die Akkorde werden Linksbündig interpretiert. Betrachte dazu folgende Zeile:

``` 
    Dsus4
Lorem Ipsum es dolor sit amet.
```
Der Akkord `Dsus4` wird Linksbündig, also auf das `m` von `Lorem` gesetzt. Die Ausgabe hat dann die Form 

`Lore\[Dsus4]m Ipsum es dolor sit amet.`

##### Nur Akkorde:

Es ist möglich, Blocke zu haben, die nur aus Akkorden bestehen. Das ist zum Beipsiel für ein Vorspiel interessant. Hier werden die Akkorde einfach Hintereinander aufgeschrieben. Das Programm wird Versuchen, den Abstand zwischen den einzelnen Akkorden zu übernehmen. Es ist damti zu rechnen, dass das nicht exakt funktioniert, weil die Breiten der Buchstaben von der beim Setzen in Latex gewählten Schriftart abhängen.
Für Details zu den erkannten Akkorden siehe unten.

##### Nur Text:

Das sollte niemanden vor ein großes Problem stellen; einfach den Text Versweise in Zeilen schreiben.

##### Tipps:

* die Demodatei `Skellett.txt` und die umgewandelte Version `Skellett.tex` anschauen
* Wenn eine Textzeile in einem Block keine Akkorde hat, muss die darüber liegende (leere) Akkordzeile weggelassen werden. Tut man das nicht, dann entsteht ein neuer Block.
* Wann immer es möglich ist, werden die Akkorde an dem Text in der Zeile darunter ausgerichtet. wenn das nicht möglich ist, versucht das PRogramm, die Abstände zwischen den Akkorden aus der Eingabe zu übernehmen.
* Der Text sollte keine doppelten Leerzeichen enthalten: Sie stören erstens die Unterscheidung zwichen Akkordzeilen und Textzeilen und andererseits werden sie von Latex nicht als einzelnes Leerzeichen gesetzt. Im Allgemeinen stellt das kein Problem dar. es kann jedoch vorkommen, dass das Programm dadurch die Zeile falsch interpretiert.

##### STrophennummern und andere Labels:

Vor der ersten Zeile eines Blockes (oder vor der zweiten Zeile, falls die erste Zeile Akkorde enthält und die zweite Zeile den dazugehörigen Text) kann der Block ein Label bekommen. Mögliche Labels sind:

* Strophennummern (`1) ` oder `1. `) Bestehen aus einer Zahl, einem Punkt, Doppelpunkt oder schließenden Klammer und (mindestems) einem anschließenden Leerzeichen. Tatsächlich ist die Zahl irrelevant: Sie dient zum Erkennen eines nummerierten Blockes. Die Zahl wird am ende durch latex gesetzt.
* Refrain (`Ref.: `, `Ref. `, `Ref: `) Auch hier muss nach dem Label wenigstens ein Leerzeichen kommen.
* Alle Blöcke ohne Label werden als Strophe ohne Nummer betrachtet und werden in einer `verse*`-Umgebung ausgegeben. Das ist relevant, wenn strophen anders gesetzt werden, als die anderen Teile des Liedes.

##### Akkorde: Schreibweise
Grundsätzlich sind alle üblichen Schreibweisen für Akkorde erlaubt:
Dazu zählen insbedondere:
* (Dur-) Akkorde, als einzelner Großbuchstabe (`A-H`)
* Halbtonschritte (mit `#` oder `b`)
* (Moll-) Akkorde, als einzelner Kleinbuchstabe (`a-h`) **oder** als Großbuchstabe mit `m`
* 5-er, 6-er, 7-er, 9-er Akkorde und so weiter
* Sonstige (`sus`, `dim`, `add9`, usw.)
gültige Akkorde sind zum Beispiel:

```e    Em     Dsus2    F#m7    Esus2   C7,11,9    E/H```

Das Proramm konvertiert die Schreibweise eingegebener (Moll-) Akkorde automatisch. Die Ausgabe erfolgt entweder in Großbuchstaben mit m (`Akkordstil = 'm'`) oder in kleinbuchstaben (`Akkordstil = 'm'`) unabhängig von der Eingabedatei. Mit `Akkordstil = ''` lässt sich die Funktion deaktivieren. Das wird in config/config.py konfiguriert.

#### Infoblock:
Der Infoblock enthält zusätzlich Informationen über das Lied. zum Beispiel kann hier der Historische Kontext des Liedes oder die Geschichte seiner Entstehung  beschrieben werden. Der Infoblock beginnt mit `@info `. ein folgendes Leerzeichen ist nicht zwingend erforderlich, wird aber empfohlen. Obwohl es im Prinzip möglich ist, den Infoblock an eine beliebige Stelle im Lied zu setzen (Außer an die erste STelle; der Kopf muss zuerst kommen) wird empholen, den Infoblock als letzten Block zu verwenden. Unabhängig von seiner Position in der Eingabedatei wird er in der Ausgabe nach dem Lied gesetzt.

## Fehler:
Jedes größere Computerprogramm hat Fehler. Es heißt, dass niemand ein Auto kaufen würde, wenn es so viele Fehler hätte, wie ein Computerprogramm. Aber wir können etwas dagegen tun: Wenn du einen Fehler in diesem Programm findest, dann melde ihn bitte als issue auf github. Es hilft mir sehr, wenn du die Eingabedatei, bei der der Fehler auftritt, oder besser noch eine möglichst kurze Variante davon mitschickst, damit ich den Fehler reproduzieren  kann.
