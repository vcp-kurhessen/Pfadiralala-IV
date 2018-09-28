PDFLATEX = pdflatex --interaction=batchmode --enable-write18 -shell-escape
SONGIDX = ./Tools/songidx
TEX_DEPENDENCIES = Lieder/*.tex Misc/GrifftabelleGitarre.tex Misc/GrifftabelleUkuleleGCEA.tex Misc/GrifftabelleUkuleleADFisH.tex Misc/GrifftabelleUkuleleDGHE.tex Misc/basic.tex Misc/songs.sty 
ABCM2PS = abcm2ps -c -F Misc/abcm2ps.fmt
GSED = gsed

.PHONY: clean PDFs PfadiralalaIV PfadiralalaIVplus Noten

# Generic targets
all: PfadiralalaIV.pdf PfadiralalaIVplus.pdf
clean:
	@rm -f *.lb .*.lb *.aux *.log *.sxc *.sxd *.sbx *.synctex.gz *.out *.fls Pfadiralala*.pdf
	

# Target definitions for song PDFs
PDFs/%.pdf: Lieder/%.tex Noten
	@mkdir -p PDFs
	SONG=$< pdflatex --enable-write18 -shell-escape -jobname=$(basename $@) Misc/Song.tex
	rm -f $(basename $@).log $(basename $@).aux $(basename $@).out
	
PDFs: $(patsubst Lieder/%.tex,PDFs/%.pdf,$(wildcard Lieder/*.tex))

# HTML exports 
html/%.html: Lieder/%.tex Noten
	@mkdir -p html
	@Tools/pfadi2ascii.py -o $@ $<

html: $(patsubst Lieder/%.tex,html/%.html,$(wildcard Lieder/*.tex))


# Noten
ABC_Noten/%.a5.ps: ABC_Noten/%.abc Misc/abcm2ps.fmt
	 $(ABCM2PS) -O $@ $< || true # The OR true is a quick fix to ignore errors...
ABC_Noten/%.a5.pdf: ABC_Noten/%.a5.ps
	ps2pdf $< $@
Noten/%.pdf: ABC_Noten/%.a5.pdf
	pdfcrop $< $@
Noten: $(patsubst ABC_Noten/%.abc,Noten/%.pdf,$(wildcard ABC_Noten/*.abc))

# Pfadiralala IV
PfadiralalaIV: PfadiralalaIV.pdf
	open $<
PfadiralalaIV.pdf: PfadiralalaIV.tex PfadiralalaIV.sbx Misc/Impressum.tex Misc/Vorwort.tex $(TEX_DEPENDENCIES)
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


# Pfadiralala IVplus
PfadiralalaIVplus: PfadiralalaIVplus.pdf
	open $<
PfadiralalaIVplus.pdf: PfadiralalaIVplus.tex PfadiralalaIVplus.sbx Misc/Impressum2.tex Misc/Vorwort2.tex Noten $(TEX_DEPENDENCIES)
	@echo "### $@"
	$(PDFLATEX) $(basename $@).tex
PfadiralalaIVplus-print.pdf: PfadiralalaIVplus.pdf
	PRINT=true $(PDFLATEX) -jobname=$(basename $@) $(basename $<).tex
PfadiralalaIVplus-pics.pdf: PfadiralalaIVplus.pdf
	PICS=true $(PDFLATEX) -jobname=$(basename $@) $(basename $<).tex
LEGACY_IDX = ~~~~{\\footnotesize\\textit{&}}
PfadiralalaIVplus.sbx: PfadiralalaIV.sxd PfadiralalaIVplus.sxd
	@echo "### $@"
	# concat both sxd files; remove hyperrefs and set format in first file, skip header in 2nd file
	{ $(GSED) '4~3s/.*//g; 2~3s/[^*].*$$/$(LEGACY_IDX)/g' PfadiralalaIV.sxd ; tail -n+2 PfadiralalaIVplus.sxd; } | $(SONGIDX) - --output $@ &> $@.log
PfadiralalaIVplus.sxd: PfadiralalaIVplus.tex
	@echo "### $@"
	$(PDFLATEX) $(basename $@).tex
	make $(basename $@).sbx
	$(PDFLATEX) $(basename $@).tex
