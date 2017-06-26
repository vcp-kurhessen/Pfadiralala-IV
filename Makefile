all: PfadiralalaIV PfadiralalaIV-2

PfadiralalaIV: PfadiralalaIV.tex
	latexmk -pdf -pdflatex="pdflatex -interaction=nonstopmode" -use-make PfadiralalaIV.tex

PfadiralalaIV-2: PfadiralalaIV-2.tex Lieder-neu/*.tex
	latexmk -pdf -pdflatex="pdflatex -interaction=nonstopmode" -use-make PfadiralalaIV-2.tex

clean:
	latexmk -CA