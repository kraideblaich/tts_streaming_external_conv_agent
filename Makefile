all: help

.PHONY: help
help: Makefile
	@echo
	@echo " Choose a make command to run"
	@echo
	@sed -n 's/^##//p' $< | column -t -s ':' |  sed -e 's/^/ /'
	@echo

## init: initialize a new python project
.PHONY: init
init:
	uv python install
	uv venv
	uv sync

## install: add a new package (make install <package>), or install all project dependencies (make install)
.PHONY: install
install:
	@if [ -z "$(filter-out install,$(MAKECMDGOALS))" ]; then \
		echo "Installing dependencies"; \
		uv sync; \
	else \
		pkg="$(filter-out install,$(MAKECMDGOALS))"; \
		echo "Adding package $$pkg"; \
		uv add $$pkg; \
	fi

## start: run local project
.PHONY: start
start:
	clear
	@echo ""
	@if [ -f .env ]; then set -a && source .env && set +a && uv run python -u main.py; else uv run python -u main.py; fi

## deploy: deploy custom component to Home Assistant server
.PHONY: deploy
deploy:
	./deploy.sh

## build: build container image
.PHONY: build
build:
	@PYTHON_VERSION=$$(grep 'requires-python' pyproject.toml | sed -E 's/.*">=([0-9]+\.[0-9]+).*/\1/'); \
	PROJECT_NAME=$$(grep '^name = ' pyproject.toml | head -1 | sed 's/name = "\(.*\)"/\1/'); \
	echo "Building $$PROJECT_NAME with Python $$PYTHON_VERSION"; \
	docker build --build-arg PYTHON_VERSION=$$PYTHON_VERSION -t $$PROJECT_NAME .

%:
	@:
