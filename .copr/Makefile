#!/usr/bin/make

SHELL := bash
SPEC_IN := .github/assets/fedora/autogroups.spec.in
SPEC_OUT := .github/assets/fedora/autogroups.spec
BUILD_REQUIRES := python3-devel python3-pip python3-build

VERSION := $(shell grep -iPo '^version\s*=\s*"\K[^"]+' pyproject.toml)

infra:
	dnf -y install $(BUILD_REQUIRES)

source: infra
	mkdir -p ~/rpmbuild/SOURCES ~/rpmbuild/SPECS
	sed "s/@VERSION@/$(VERSION)/g" $(SPEC_IN) > $(SPEC_OUT)
	cp $(SPEC_OUT) ~/rpmbuild/SPECS/
	python3 -m pip install --user build
	python3 -m build --sdist --outdir ~/rpmbuild/SOURCES/

srpm: source
	mkdir -p dist
	rpmbuild -bs ~/rpmbuild/SPECS/autogroups.spec --define "_srcrpmdir $(outdir)"

.PHONY: infra source srpm
