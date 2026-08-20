#!/usr/bin/make

SHELL := bash
SPEC_IN := .github/assets/fedora/autogroups.spec.in
SPEC_OUT := .github/assets/fedora/autogroups.spec

VERSION := $(shell grep -iPo '^version\s*=\s*"\K[^"]+' pyproject.toml)

source:
	mkdir -p ~/rpmbuild/SOURCES ~/rpmbuild/SPECS
	sed "s/@VERSION@/$(VERSION)/g" $(SPEC_IN) > $(SPEC_OUT)
	cp $(SPEC_OUT) ~/rpmbuild/SPECS/
	python3 -m pip install --user build
	python3 -m build --sdist --outdir ~/rpmbuild/SOURCES/

srpm: source
	mkdir -p dist
	rpmbuild -bs ~/rpmbuild/SPECS/autogroups.spec --define "_srcrpmdir $(outdir)"

.PHONY: source srpm
