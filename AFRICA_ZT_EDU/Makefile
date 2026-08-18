PYTHON ?= python3
LATEX ?= pdflatex
BIBTEX ?= bibtex

.PHONY: all paper simulate benchmark figures reproduce clean verify

all: paper

simulate:
	$(PYTHON) experiments/simulate_policy.py

benchmark:
	$(PYTHON) scripts/benchmark.py --output-dir results

figures:
	$(PYTHON) scripts/generate_figures.py

reproduce: simulate benchmark figures paper

paper:
	$(LATEX) -interaction=nonstopmode -halt-on-error main.tex
	$(BIBTEX) main
	$(LATEX) -interaction=nonstopmode -halt-on-error main.tex
	$(LATEX) -interaction=nonstopmode -halt-on-error main.tex
	cp main.pdf compiled_paper.pdf

verify:
	@echo "Pages:"; pdfinfo compiled_paper.pdf | grep '^Pages:'
	@echo "Bib entries:"; grep -c '^@[A-Za-z].*{' references.bib
	@echo "Table environments:"; grep -c '^\\begin{table' main.tex
	@echo "Figure environments:"; grep -c '^\\begin{figure' main.tex
	@echo "Type 3 fonts (expected none):"; pdffonts compiled_paper.pdf | grep 'Type 3' || true

clean:
	rm -f main.aux main.bbl main.blg main.fdb_latexmk main.fls main.log main.out main.pdf
