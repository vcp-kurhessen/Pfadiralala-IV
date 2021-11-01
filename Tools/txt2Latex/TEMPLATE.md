# TEmplate
Das Template wird verwendet, um das Latex-dokument aus den gewonnen Daten mit Jinja zusammenzusetzen. Hier wird die Struktur der LAtex-Datei festgelegt. Siehe auch die Dokumentation von (jinja2)[https://jinja2docs.readthedocs.io/en/stable/]

Codeblöcke beginnen mit `BLOCK{` und enden mit `}`
Variablen beginnen mit `VAR{`  und enden mit `}`
Kommentare beginnen mit `#{` und enden mit `}`

Die Jinja2 umgebung wird folgendermaßen konfiguriert:
```python
j2.Environment(
    block_start_string=r'\BLOCK{',
    block_end_string=r'}',
    variable_start_string=r'\VAR{',
    variable_end_string=r'}',
    comment_start_string=r'#{',
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
```
