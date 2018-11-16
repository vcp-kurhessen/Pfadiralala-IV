PDFLATEX = pdflatex --interaction=batchmode --enable-write18 -shell-escape
SONGIDX = ./Tools/songidx
GENERIC_DEPS = Lieder/*.tex Misc/GrifftabelleGitarre.tex Misc/GrifftabelleUkuleleGCEA.tex Misc/GrifftabelleUkuleleADFisH.tex Misc/GrifftabelleUkuleleDGHE.tex Misc/basic.tex Misc/songs.sty 
ABCM2PS = abcm2ps -c -F Misc/abcm2ps.fmt
SED = sed

ifeq ($(shell uname -s),Darwin)
    SED = gsed
endif


.PHONY: clean PDFs Noten

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
PfadiralalaIV_DEPS = PfadiralalaIV.tex Misc/Impressum.tex Misc/Vorwort.tex

PfadiralalaIV.pdf: 			$(PfadiralalaIV_DEPS) $(GENERIC_DEPS) PfadiralalaIV.sbx
	@echo "### $@"
	$(PDFLATEX) $(basename $@).tex
	@echo ""
PfadiralalaIV-print.pdf: 	$(PfadiralalaIV_DEPS) $(GENERIC_DEPS) PfadiralalaIV.sbx
	@echo "### $@"
	PRINT=true $(PDFLATEX) -jobname=$(basename $@) $(basename $<).tex
	@echo ""
PfadiralalaIV-pics.pdf: 	$(PfadiralalaIV_DEPS) $(GENERIC_DEPS) PfadiralalaIV.sbx
	@echo "### $@"
	PICS=true $(PDFLATEX) -jobname=$(basename $@) $(basename $<).tex
	@echo ""

PfadiralalaIV.sbx: 		PfadiralalaIV.sxd
	@echo "### $@"
	$(SONGIDX) --output $@ $< 2>&1 | tee $@.log	
	@echo ""
PfadiralalaIV.sbx.tmp: 	PfadiralalaIV.sxd.tmp
	@echo "### $@"
	$(SONGIDX) --output $@ $< 2>&1 | tee $@.log	
	@echo ""
PfadiralalaIV.sxd:		$(PfadiralalaIV_DEPS) $(GENERIC_DEPS) PfadiralalaIV.sbx.tmp
	@echo "### $@"
	cp PfadiralalaIV.sbx.tmp PfadiralalaIV.sbx
	$(PDFLATEX) PfadiralalaIV.tex
	@echo ""
PfadiralalaIV.sxd.tmp: 	$(PfadiralalaIV_DEPS) $(GENERIC_DEPS)
	@echo "### $@"
	$(PDFLATEX) PfadiralalaIV.tex
	mv PfadiralalaIV.sxd $@
	@echo ""


# Pfadiralala IVplus
PfadiralalaIVplus_DEPS = PfadiralalaIVplus.tex Misc/Impressum2.tex Misc/Vorwort2.tex Noten
LEGACY_IDX = ~~~{\\textit{&}}

PfadiralalaIVplus.pdf: 			$(PfadiralalaIVplus_DEPS) $(GENERIC_DEPS) PfadiralalaIVplus.sbx
	@echo "### $@"
	$(PDFLATEX) $(basename $@).tex
	@echo ""
PfadiralalaIVplus-print.pdf: 	$(PfadiralalaIVplus_DEPS) $(GENERIC_DEPS) PfadiralalaIVplus.sbx
	@echo "### $@"
	PRINT=true $(PDFLATEX) -jobname=$(basename $@) $(basename $<).tex
	@echo ""
PfadiralalaIVplus-pics.pdf: 	$(PfadiralalaIVplus_DEPS) $(GENERIC_DEPS) PfadiralalaIVplus.sbx
	@echo "### $@"
	PICS=true $(PDFLATEX) -jobname=$(basename $@) $(basename $<).tex
	@echo ""

PfadiralalaIVplus.sbx: 		PfadiralalaIV.sxd 		PfadiralalaIVplus.sxd
	@echo "### $@"
	{ $(SED) '4~3s/.*//g; 2~3s/[^*].*$$/$(LEGACY_IDX)/g' PfadiralalaIV.sxd ; tail -n+2 PfadiralalaIVplus.sxd; } | \
	$(SONGIDX) --output $@ - 2>&1 | tee $@.log
	@echo ""
PfadiralalaIVplus.sbx.tmp: 	PfadiralalaIV.sxd.tmp	PfadiralalaIVplus.sxd.tmp 
	@echo "### $@"
	{ $(SED) '4~3s/.*//g; 2~3s/[^*].*$$/$(LEGACY_IDX)/g' PfadiralalaIV.sxd.tmp ; tail -n+2 PfadiralalaIVplus.sxd.tmp; } | \
	$(SONGIDX) --output $@ - 2>&1 | tee $@.log
	@echo ""
PfadiralalaIVplus.sxd: 		$(PfadiralalaIVplus_DEPS) $(GENERIC_DEPS) PfadiralalaIVplus.sbx.tmp 
	@echo "### $@"
	cp PfadiralalaIVplus.sbx.tmp PfadiralalaIVplus.sbx
	$(PDFLATEX) PfadiralalaIVplus.tex
	@echo ""
PfadiralalaIVplus.sxd.tmp: 	$(PfadiralalaIVplus_DEPS) $(GENERIC_DEPS)
	@echo "### $@"
	$(PDFLATEX) PfadiralalaIVplus.tex
	mv PfadiralalaIVplus.sxd $@
	@echo ""