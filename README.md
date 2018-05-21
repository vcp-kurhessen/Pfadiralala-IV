# Pfadiralala-IV

Das ''Pfadiralala IV'' und ''Pfadiralala IVplus'' sind Liederbücher der Region Kurhessen im Verband Christlicher Pfadfinderinnen und Pfadfinder. Es ist ausschließlich zum internen Gebrauch von den Mitgliedern der Region bestimmt und wird nur an diese ausgegeben. Das Liederbuch stellt daher keine Veröffentlichung im Sinne des Pressegesetzes dar. Alle Rechte an den Melodien, Texten und Zeichnungen liegen bei den Autoren. 

## Datei-Struktur

- **basic-design.tex**: Konfiguration der verwendeten Pakete.
- **Grifftabelle\*.tex**: Grifftabellen für verschiedene Saiteninstrumente.
- **PfadiralalaIV.tex**: Definition des Liederbuchs (Lieder und Reihenfolgen).
- **PfadiralalaIVplus.tex**: Definition des Ergänzungsbuchs *Pfadiralala IVplus*.
- **Tutorial.tex**: Beispiel-Song mit den am häufigsten verwendeten Kommandos. 

## LaTeX kompilieren / Makefile
- **PfadiralalaIV{plus}.pdf**: Draft version des Liederbuchs
- **PfadiralalaIV{plus}-pics.pdf**: Version des Liederbuchs mit Bildern
- **PfadiralalaIV{plus}.pdf**: Version des Liederbuchs mit Bildern und Schnittrand
- **clean**: Löscht alle temporären Dateien und Liederbuch PDFs
- **PDFs/%**: Sucht in den Lieder* Ordnern nach dem Dateinamen und erzeugt ein PDF im Ordner PDFs
