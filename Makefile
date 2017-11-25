PDFLATEX = pdflatex --interaction=batchmode --enable-write18 -shell-escape
SONGIDX = ./Tools/songidx
TEX_DEPENDENCIES = Lieder/*.tex Misc/GrifftabelleGitarre.tex Misc/GrifftabelleUkuleleGCEA.tex Misc/GrifftabelleUkuleleADFisH.tex Misc/GrifftabelleUkuleleDGHE.tex Misc/basic.tex Misc/songs.sty 

.PHONY: clean PDFs PfadiralalaIV PfadiralalaIV-2

# Generic targets
all: PfadiralalaIV.pdf PfadiralalaIV-2.pdf
clean:
	@rm -f *.lb .*.lb *.aux *.log *.sxc *.sxd *.sbx *.synctex.gz *.out *.fls Pfadiralala*.pdf
	

# Target definitions for song PDFs
PDFs/%.pdf: Lieder/%.tex
	@mkdir -p PDFs
	SONG=$< $(PDFLATEX) -jobname=$(basename $@) Misc/Song.tex
	rm -f $(basename $@).log $(basename $@).aux $(basename $@).out
	
PDFs: $(patsubst Lieder/%.tex,PDFs/%.pdf,$(wildcard Lieder/*.tex))

# Noten
Noten/%.a5.ps: ABC_Noten/%.abc
	abcm2ps -O $@ -c -F Misc/abcm2ps.fmt $<
Noten/%.a5.pdf: Noten/%.a5.ps
	ps2pdf $< $@
Noten/%.pdf: Noten/%.a5.pdf
	pdfcrop $< $@
Noten: $(patsubst ABC_Noten/%.abc,Noten/%.pdf,$(wildcard ABC_Noten/*.abc))

# Pfadiralala IV
PfadiralalaIV: PfadiralalaIV.pdf
	open $<
PfadiralalaIV.pdf: PfadiralalaIV.tex PfadiralalaIV.sbx $(TEX_DEPENDENCIES)
	@echo "### $@"
	$(PDFLATEX) $(basename $@).tex
PfadiralalaIV-print.pdf: PfadiralalaIV.pdf
	PRINT=true $(PDFLATEX) -jobname=$(basename $@) $(basename $<).tex
PfadiralalaIV-pics.pdf: PfadiralalaIV.pdf
	PICS=true $(PDFLATEX) -jobname=$(basename $@) $(basename $<).tex
PfadiralalaIV.sbx: PfadiralalaIV.sxd
	@echo "### $@"
	$(SONGIDX) $< &> $@.log	
PfadiralalaIV.sxd: PfadiralalaIV.tex
	@echo "### $@"
	$(PDFLATEX) $(basename $@).tex
	make $(basename $@).sbx
	$(PDFLATEX) $(basename $@).tex


# Pfadiralala IV+
PfadiralalaIV-2: PfadiralalaIV-2.pdf
	open $<
PfadiralalaIV-2.pdf: PfadiralalaIV-2.tex PfadiralalaIV-2.sbx  $(TEX_DEPENDENCIES)
	@echo "### $@"
	$(PDFLATEX) $(basename $@).tex
PfadiralalaIV-2-print.pdf: PfadiralalaIV-2.pdf
	PRINT=true $(PDFLATEX) -jobname=$(basename $@) $(basename $<).tex
PfadiralalaIV-2-pics.pdf: PfadiralalaIV-2.pdf
	PICS=true $(PDFLATEX) -jobname=$(basename $@) $(basename $<).tex
PfadiralalaIV-2.sbx: PfadiralalaIV-2.sxd PfadiralalaIV-2.tex
	@echo "### $@"
	$(SONGIDX) $< &> $@.log
PfadiralalaIV-2.sxd: PfadiralalaIV-2.tex
	@echo "### $@"
	$(PDFLATEX) $(basename $@).tex
	make $(basename $@).sbx
	$(PDFLATEX) $(basename $@).tex