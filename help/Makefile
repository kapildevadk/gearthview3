# Makefile for Sphinx documentation

SPHINXBUILD = sphinx-build
SOURCE      = source
BUILDDIR    = build

.PHONY: help clean $(SPHINXBUILD) html dirhtml singlehtml pickle json \
          htmlhelp qthelp devhelp epub latex latexpdf text man changes \
          linkcheck doctest

help:
	@echo "Please use \`make <target>' where <target> is one of"
	@echo "  $(SPHINXBUILD)       to run Sphinx build"
	@echo "  html               to make standalone HTML files"
	@echo "  dirhtml            to make HTML files named index.html in directories"
	@echo "  singlehtml         to make a single large HTML file"
	@echo "  pickle             to make pickle files"
	@echo "  json               to make JSON files"
	@echo "  htmlhelp           to make HTML files and a HTML help project"
	@echo "  qthelp             to make HTML files and a qthelp project"
	@echo "  devhelp            to make HTML files and a Devhelp project"
	@echo "  epub               to make an epub"
	@echo "  latex              to make LaTeX files, you can set PAPER=a4 or PAPER=letter"
	@echo "  latexpdf           to make LaTeX files and run them through pdflatex"
	@echo "  text               to make text files"
	@echo "  man                to make manual pages"
	@echo "  changes            to make an overview of all changed/added/deprecated items"
	@echo "  linkcheck          to check all external links for integrity"
	@echo "  doctest            to run all doctests embedded in the documentation (if enabled)"

clean:
	rm -rf $(BUILDDIR)/*

$(SPHINXBUILD):
	pip install -U -q sphinx

html: $(SPHINXBUILD)
html::
	$(SPHINXBUILD) -M html $(SOURCE) $(BUILDDIR) $(SPHINXOPTS)

dirhtml: $(SPHINXBUILD)
dirhtml::
	$(SPHINXBUILD) -M dirhtml $(SOURCE) $(BUILDDIR) $(SPHINXOPTS)

singlehtml: $(SPHINXBUILD)
singlehtml::
	$(SPHINXBUILD) -M singlehtml $(SOURCE) $(BUILDDIR) $(SPHINXOPTS)

pickle: $(SPHINXBUILD)
pickle::
	$(SPHINXBUILD) -M pickle $(SOURCE) $(BUILDDIR) $(SPHINXOPTS)

json: $(SPHINXBUILD)
json::
	$(SPHINXBUILD) -M json $(SOURCE) $(BUILDDIR) $(SPHINXOPTS)

htmlhelp: $(SPHINXBUILD)
htmlhelp::
	$(SPHINXBUILD) -M htmlhelp $(SOURCE) $(BUILDDIR) $(SPHINXOPTS)

qthelp: $(SPHINXBUILD)
qthelp::
	$(SPHINXBUILD) -M qthelp $(SOURCE) $(BUILDDIR) $(SPHINXOPTS)

devhelp: $(SPHINXBUILD)
devhelp::
	$(SPHINXBUILD) -M devhelp $(SOURCE) $(BUILDDIR) $(SPHINXOPTS)

epub: $(SPHINXBUILD)
epub::
	$(SPHINXBUILD) -M epub $(SOURCE) $(BUILDDIR) $(SPHINXOPTS)

latex: $(SPHINXBUILD)
latex::
	$(SPHINXBUILD) -M latex $(SOURCE) $(BUILDDIR) $(SPHINXOPTS)

latexpdf: $(SPHINXBUILD)
latexpdf::
	$(SPHINXBUILD) -M latex $(SOURCE) $(BUILDDIR) $(SPHINXOPTS) && \
		make -C $(BUILDDIR)/latex all-pdf

text: $(SPHINXBUILD)
text::
	$(SPHINXBUILD) -M text $(SOURCE) $(BUILDDIR) $(SPHINXOPTS)

man: $(SPHINXBUILD)
man::
	$(SPHINXBUILD) -M man $(SOURCE) $(BUILDDIR) $(SPHINXOPTS)

changes: $(SPHINXBUILD)
changes::
	$(SPHINXBUILD) -M changes $(SOURCE) $(BUILDDIR) $(SPHINXOPTS)

linkcheck: $(SPHINXBUILD)
linkcheck::
	$(SPHINXBUILD) -M linkcheck $(SOURCE) $(BUILDDIR) $(SPHINXOPTS)

doctest: $(SPHINXBUILD)
doctest::
	$(SPHINXBUILD) -M doctest $(SOURCE) $(BUILDDIR) $(SPHINXOPTS)
