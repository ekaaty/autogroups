#!/usr/bin/make

SHELL := bash

RPM_SOURCES := $(shell rpm --eval '%{_sourcedir}')
RPM_SPECS   := $(shell rpm --eval '%{_specdir}')

SPEC_IN  := .github/assets/fedora/autogroups.spec.in
SPEC_OUT := $(RPM_SPECS)/autogroups.spec

BUILD_REQUIRES := python3-devel python3-pip python3-build

VERSION := $(shell grep -iPo '^version\s*=\s*"\K[^"]+' pyproject.toml)

infra:
	dnf -y install $(BUILD_REQUIRES)
	mkdir -p "$(RPM_SOURCES)" "$(RPM_SPECS)" "$(outdir)"

source: infra
	sed "s/@VERSION@/$(VERSION)/g" $(SPEC_IN) > $(SPEC_OUT)
	python3 -m build --sdist --outdir "$(RPM_SOURCES)/"

srpm: source
	rpmbuild -bs "$(SPEC_OUT)" --define "_srcrpmdir $(outdir)"

.PHONY: infra source srpm
