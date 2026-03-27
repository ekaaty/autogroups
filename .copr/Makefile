#!/usr/bin/make

SHELL := bash

source:
	rpmbuild -bs .github/assets/fedora/autogroups.spec

srpm: source
	mkdir -p $(outdir)
	cp dist/*.src.rpm $(outdir)
