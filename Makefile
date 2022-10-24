PDFLATEX = pdflatex --interaction=nonstopmode --halt-on-error --enable-write18 -shell-escape
SONGIDX = texlua ./Tools/songidx.lua
GENERIC_DEPS = Lieder/*.tex Misc/GrifftabelleGitarre.tex Misc/GrifftabelleUkuleleGCEA.tex Misc/GrifftabelleUkuleleADFisH.tex Misc/GrifftabelleUkuleleDGHE.tex Misc/basic.tex Misc/songs.sty 
ABCM2PS = abcm2ps -c -F Misc/abcm2ps.fmt
SED = sed

ifeq ($(shell uname -s),Darwin)
    SED = gsed
endif

.PHONY: clean clean_Noten PDFs Noten

# make default targets
all: $(patsubst Ausgaben/%.tex,Ausgaben/%.pdf,$(wildcard Ausgaben/*.tex)) $(patsubst Ausgaben/%.tex,Ausgaben/%-pics.pdf,$(wildcard Ausgaben/*.tex))
clean: clean_Noten
	rm -f Ausgaben/*.lb Ausgaben/.*.lb Ausgaben/*.aux Ausgaben/*.log Ausgaben/*.sxc Ausgaben/*.sxd Ausgaben/*.sbx Ausgaben/*.synctex.gz Ausgaben/*.out Ausgaben/*.fls Ausgaben/*.pdf Ausgaben/*.tmp Ausgaben/CompleteEdition.tex
clean_Noten: 
	rm -f $(patsubst ABC_Noten/%.mcm,Noten/%.pdf,$(wildcard ABC_Noten/*.mcm))


# targets for song PDFs
PDFs/%.pdf: Lieder/%.tex Noten
	@mkdir -p PDFs
	SONG=$< pdflatex --enable-write18 -shell-escape -jobname=$(basename $@) Misc/Song.tex
	rm -f $(basename $@).log $(basename $@).aux $(basename $@).out
	
PDFs: $(patsubst Lieder/%.tex,PDFs/%.pdf,$(wildcard Lieder/*.tex))


# HTML exports 
html/%.html: Lieder/%.tex Noten
	@mkdir -p html
	Tools/pfadi2ascii.py -o $@ $<

html: $(patsubst Lieder/%.tex,html/%.html,$(wildcard Lieder/*.tex))


# Noten
ABC_Noten/%.a5.ps: ABC_Noten/%.mcm Misc/abcm2ps.fmt
	 $(ABCM2PS) -O $@ $< || true # The OR true is a quick fix to ignore errors...
ABC_Noten/%.a5.pdf: ABC_Noten/%.a5.ps
	ps2pdf $< $@
Noten/%.pdf: ABC_Noten/%.a5.pdf
	pdfcrop $< $@
Noten: $(patsubst ABC_Noten/%.mcm,Noten/%.pdf,$(wildcard ABC_Noten/*.mcm))

	
# Generic targets for all books
AUSGABE_DEPS = Ausgaben/%.tex $(wildcard Ausgaben/%/*.tex) Noten

Ausgaben/%.pdf: 		$(AUSGABE_DEPS) $(GENERIC_DEPS) Ausgaben/%.sbx
	$(PDFLATEX)  -jobname=$(basename $@) $(basename $@).tex
Ausgaben/%-print.pdf: 	$(AUSGABE_DEPS) $(GENERIC_DEPS) Ausgaben/%.sbx
	PRINT=1 $(PDFLATEX) -jobname=$(basename $@) $(basename $<).tex
Ausgaben/%-pics.pdf: 	$(AUSGABE_DEPS) $(GENERIC_DEPS) Ausgaben/%.sbx
	PICS=1 $(PDFLATEX) -jobname=$(basename $@) $(basename $<).tex
Ausgaben/%.html:		Ausgaben/%.pdf
	pdf2htmlEX --bg-format=svg $(basename $@).pdf $@

# create a temporary sxd
Ausgaben/%.sxd.tmp: 	$(AUSGABE_DEPS) $(GENERIC_DEPS)
	$(PDFLATEX) -jobname=$(basename $(basename $@)) $(basename $(basename $@)).tex
	mv $(basename $@) $@
# compile temporary sxd to temporary sbx
Ausgaben/%.sbx.tmp: 	Ausgaben/%.sxd.tmp
	$(SONGIDX) $< $@ 2>&1 | tee $@.log
# use temporary sbx file to create final sxd
Ausgaben/%.sxd:			Ausgaben/%.sbx.tmp $(AUSGABE_DEPS) $(GENERIC_DEPS)
	cp $(basename $@).sbx.tmp $(basename $@).sbx
	$(PDFLATEX) -jobname=$(basename $@) $(basename $@).tex
# compile final sxd
Ausgaben/%.sbx: 		Ausgaben/%.sxd
	$(SONGIDX) $< $@ 2>&1 | tee $@.log

# Special case: Pfadiralala IVplus with combined Index
LEGACY_IDX = ~~~{\\textit{&}}
Ausgaben/PfadiralalaIVplus.sbx: 		Ausgaben/PfadiralalaIV.sxd Ausgaben/PfadiralalaIVplus.sxd
	{ $(SED) '4~3s/.*//g; 2~3s/[^*].*$$/$(LEGACY_IDX)/g' Ausgaben/PfadiralalaIV.sxd ; tail -n+2 Ausgaben/PfadiralalaIVplus.sxd; } | \
	$(SONGIDX) - $@ 2>&1 | tee $@.log
Ausgaben/PfadiralalaIVplus.sbx.tmp: 	Ausgaben/PfadiralalaIV.sxd.tmp Ausgaben/PfadiralalaIVplus.sxd.tmp
	{ $(SED) '4~3s/.*//g; 2~3s/[^*].*$$/$(LEGACY_IDX)/g' Ausgaben/PfadiralalaIV.sxd.tmp ; tail -n+2 Ausgaben/PfadiralalaIVplus.sxd.tmp; } | \
	$(SONGIDX) - $@ 2>&1 | tee $@.log

# Special case: Generated Songbook with all Songs
Ausgaben/CompleteEdition.tex: ./Tools/generate_songbook.sh
Ausgaben/CompleteSortedEdition.tex: Tools/generate_sorted_songbook.py Lieder/*.tex
	python ./Tools/generate_sorted_songbook.py --by index --by txt --by mel --by titel Lieder/*.tex > $@
