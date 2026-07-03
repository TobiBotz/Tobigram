VENV := venv

ifeq ($(OS),Windows_NT)
    PYTHON := $(VENV)/Scripts/python
    SPHINX := $(VENV)/Scripts/sphinx-build
else
    PYTHON := $(VENV)/bin/python
    SPHINX := $(VENV)/bin/sphinx-build
endif
PIP := $(PYTHON) -m pip
TAG = v$(shell grep -E '__version__ = ".*"' pyrogram/__init__.py | cut -d\" -f2)

RM := rm -rf

GREEN  := \033[0;32m
RED    := \033[0;31m
YELLOW := \033[0;33m
BLUE   := \033[0;34m
BOLD   := \033[1m
RESET  := \033[0m

.PHONY: venv venv-docs clean-venv clean-build clean-api clean-docs clean api docs docs-archive build tag dtag

PY := $(shell command -v python3 2>/dev/null || command -v python 2>/dev/null || command -v py 2>/dev/null)

venv:
	$(PY) -m venv $(VENV)
	$(PYTHON) -m pip install -U pip wheel setuptools
	$(PYTHON) -m pip install -U -e .[dev]
	@printf "$(YELLOW)Created venv with %s$(RESET)\n" "$$($(PYTHON) --version)"

venv-docs:
	$(PY) -m venv $(VENV)
	$(PYTHON) -m pip install -U pip wheel setuptools
	$(PYTHON) -m pip install -U -e .[docs]
	@printf "$(YELLOW)Created docs venv with %s$(RESET)\n" "$$($(PYTHON) --version)"

clean-venv:
	$(RM) $(VENV)
	@printf "$(YELLOW)Cleaned venv directory$(RESET)\n"

clean-build:
	$(RM) *.egg-info build dist
	@printf "$(YELLOW)Cleaned build directory$(RESET)\n"

clean-api:
	$(RM) pyrogram/errors/exceptions pyrogram/raw/all.py pyrogram/raw/base pyrogram/raw/functions pyrogram/raw/types
	@printf "$(YELLOW)Cleaned api directory$(RESET)\n"

clean-docs:
	$(RM) docs/build docs/source/api/bound-methods docs/source/api/methods docs/source/api/types docs/source/api/enums docs/source/telegram
	@printf "$(YELLOW)Cleaned docs directory$(RESET)\n"

clean: clean-venv clean-build clean-api clean-docs
	@printf "$(GREEN)Cleaned all directories$(RESET)\n"

api:
	cd compiler/api && ../../$(PYTHON) compiler.py
	cd compiler/errors && ../../$(PYTHON) compiler.py
	# compiler/methods: run manually from project root: python compiler/methods/compiler.py

docs:
	cd compiler/docs && ../../$(PYTHON) compiler.py
	$(SPHINX) -b dirhtml "docs/source" "docs/build/html" -j auto

docs-archive:
	cd docs/build/html && zip -r ../docs.zip ./

build:
	hatch build

tag:
	git tag $(TAG)
	git push origin $(TAG)

dtag:
	git tag -d $(TAG)
	git push origin -d $(TAG)
