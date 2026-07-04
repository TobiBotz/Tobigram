UV := uv
PYTHON := $(UV) run python3
TAG = v$(shell grep -E '__version__ = ".*"' pyrogram/__init__.py | cut -d\" -f2)

RM := rm -rf

GREEN  := \033[0;32m
RED    := \033[0;31m
YELLOW := \033[0;33m
BLUE   := \033[0;34m
BOLD   := \033[1m
RESET  := \033[0m

.PHONY: venv clean-venv clean-build clean-api clean-docs clean api docs docs-archive build tag dtag

venv:
	$(UV) sync --frozen
	@printf "$(YELLOW)Synced environment with %s$(RESET)\n" "$$($(PYTHON) --version)"

venv-dev:
	$(UV) sync --frozen --extra dev
	@printf "$(YELLOW)Synced dev environment with %s$(RESET)\n" "$$($(PYTHON) --version)"

clean-venv:
	$(RM) .venv
	@printf "$(YELLOW)Cleaned .venv directory$(RESET)\n"

clean-build:
	$(RM) dist *.egg-info build
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
	cd compiler/api && $(UV) run python3 compiler.py
	cd compiler/errors && $(UV) run python3 compiler.py

docs:
	cd compiler/docs && ../../$(PYTHON) compiler.py
	$(UV) run sphinx-build -b dirhtml "docs/source" "docs/build/html" -j auto

docs-archive:
	cd docs/build/html && zip -r ../docs.zip ./

build:
	$(UV) build

publish:
	$(UV) publish

test:
	$(UV) run pytest --no-header -q

tag:
	git tag $(TAG)
	git push origin $(TAG)

dtag:
	git tag -d $(TAG)
	git push origin -d $(TAG)
