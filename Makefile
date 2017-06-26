LATEXMK = latexmk -pdf -pdflatex="pdflatex -interaction=nonstopmode" -use-make

all: PfadiralalaIV PfadiralalaIV-2 basic-design.tex songs.sty GrifftabelleGitarre.tex GrifftabelleUkuleleADFisH.tex GrifftabelleUkuleleDGHE.tex 

PfadiralalaIV: PfadiralalaIV.tex Lieder/*.tex Vorwort.tex Impressum.tex
	$(LATEXMK) $@.tex
	open $@.pdf

PfadiralalaIV-2: PfadiralalaIV-2.tex Lieder-neu/*.tex GrifftabelleUkuleleGCEA.tex
	$(LATEXMK) $@.tex
	open $@.pdf

clean:
	latexmk -CA