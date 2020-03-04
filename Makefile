.PHONY: all lint test install dev uninstall-dev clean distclean

PYTHON ?= python

all: ;

lint:
	q2lint
	flake8

test: all
	py.test

install:
	$(PYTHON) setup.py install

dev: all
	pip install -e .

uninstall-dev:
	pip uninstall q2-mystery-stew

clean: distclean

distclean: ;
