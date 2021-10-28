# Hinweise zur Konfiguration

Diese Dokument enthält die Dokumentation der Konfigurationsdateien.

## config.py

Hier werdden alle Wichtigen konfigurationen durchgeführt. Der einfachheit halber handelt es sich um ein PYthon-skript, sodass beliebige funktionien direkt programmiert werden können.

##### Akkordstil
Erlaubte Werte: `'l'`, `'m'` oder `''`
Akkorde können in zwei SChreibweisen Angegben werden:
 * Großkleinschreibung: Dur-Akkorde werden groß geschrieben, Moll-Akkorde werden klein geschrieben
 * 'm'-Schreibvweise: Dur-Akkorde werden groß geschrieben, Moll-Akkorde erhalten ein 'm'

Beide Schreibweise werden unterstützt. Mit dem Parameter `Akkordstil` wird festgelegt, welcher Stil in der ausgabe versendet werden soll.
`Akkordstil = ''` übernimmt die Akkorde so, wie sie in der eingabedatei angegeben werden.
`Akkordstil = 'm'` konvertiert  die Akkorde in die m-Schreibweise, falls nötig.
`Akkordstil = 'l'` konvertiert  die Akkorde in Großkleinschreibweise, falls nötig.

#### REGEX
Um Label für unterschiedliche Blocktypen zu erkennen, werden Reguläre ausdrücke verwendet. Da die eingabe intern Zeilenweise verarbeitet wird, werden die Regulären ausdrücke auf jede Zeile angewendet. REGEX für mehrzeiligen Text ist also nicht möglich.
Der gefundene Ausdruck wird aus der Eingabe entfernt. Es sollte nur eine Übereinstimmung in einer Zeile geben.
`STROPHENREGEX` ist der Reguläre Ausdruck für die Strophennummer von Nummerierten Strophen
`REFRAINREGEX` ist der Reguläre Ausdruck für die markierung des Refrains
`INFOREGEX` ist der REguläre Ausdruck, mit dem der anfang des Infoblockes identifiziert wird.

`AKKOORDREGEX` wird auf ZEilen angewendet, die nur Akkorde enthalten. Jeder Treffer sollte ein einzelner Akkord sein.

#### Ersetzungsfunktionen
Vor und nach der Konvertierung der Zeilen mit Akkorden und Text zu einer gemeinsamen ausgabezeile besteht die möglichkeit, manuell änderungen vorzunehmen. Das kann abhängig vom erkannten typ des Blockes, aus dem die Zeilen Stammen in den entsprechenden Funktionen passieren. Üblicherweise werden Hier zeichen, die Latex nicht verarbeiten kann, z.B. das kaufmännische und (`&`)  durch escape-sequenzen ersetzt, im Prinzip sind aber beliebige ersetzungen möglich.

Da im Titelblock und im Infoblock keine Akkordsymbole Verarbeitet werden, gibt es nur eine ersetzungsfunktion.

Eine Besonderheit stellt die Funktion `formatMeta` dar. Hier können die aus der Eingabe extrahierten Metadaten als dict bearbeitet werden. Es empfiehlt sich, nur die Werte zu bearbeiten und die Schlüssel so zu lassen, wie sie sind.

Alle Funktionen deren Name mit einem Unterstrich beginnt, werden nur lokal verwendet.

#### Umgebungen:
Hier werden die Namen der verwendeten Latex-Umgebungen für die unterschiedlichen Blocktypen definiert. siehe auch Template.jinja, bzw, die dazugehörige okumentation.
