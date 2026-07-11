###############################################################################
# Institutional Quant Platform
# Enterprise Makefile
###############################################################################

.DEFAULT_GOAL := help

###############################################################################
# Variables
###############################################################################

PYTHON := python3

PIP := pip

PYTEST := pytest

RUFF := ruff

BLACK := black

MYPY := mypy

BANDIT := bandit

SEMGREP := semgrep

CHECKOV := checkov

DOCKER := docker

TERRAFORM := terraform

HELM := helm

MKDOCS := mkdocs

COVERAGE := coverage

###############################################################################
# Help
###############################################################################

.PHONY: help

help:
	@echo ""
	@echo "Institutional Quant Platform"
	@echo "============================"
	@echo ""
	@echo "Development"
	@echo "-----------"
	@echo "make install"
	@echo "make update"
	@echo "make clean"
	@echo ""
	@echo "Quality"
	@echo "-------"
	@echo "make format"
	@echo "make lint"
	@echo "make typecheck"
	@echo "make security"
	@echo ""
	@echo "Testing"
	@echo "-------"
	@echo "make test"
	@echo "make coverage"
	@echo "make benchmark"
	@echo ""
	@echo "Documentation"
	@echo "-------------"
	@echo "make docs"
	@echo "make docs-build"
	@echo ""
	@echo "Containers"
	@echo "----------"
	@echo "make docker"
	@echo "make docker-run"
	@echo ""
	@echo "Infrastructure"
	@echo "--------------"
	@echo "make terraform"
	@echo "make helm"
	@echo ""
	@echo "CI"
	@echo "--"
	@echo "make ci"

###############################################################################
# Installation
###############################################################################

.PHONY: install

install:
	$(PIP) install --upgrade pip
	$(PIP) install -r requirements.txt
	@if [ -f requirements-dev.txt ]; then \
		$(PIP) install -r requirements-dev.txt; \
	fi
	pre-commit install

###############################################################################
# Update
###############################################################################

.PHONY: update

update:
	$(PIP) install --upgrade -r requirements.txt

###############################################################################
# Formatting
###############################################################################

.PHONY: format

format:
	$(BLACK) .
	$(RUFF) format .
	$(RUFF) check . --fix

###############################################################################
# Lint
###############################################################################

.PHONY: lint

lint:
	$(RUFF) check .
	$(BLACK) --check .

###############################################################################
# Type Checking
###############################################################################

.PHONY: typecheck

typecheck:
	$(MYPY) .

###############################################################################
# Tests
###############################################################################

.PHONY: test

test:
	$(PYTEST)

###############################################################################
# Coverage
###############################################################################

.PHONY: coverage

coverage:
	$(COVERAGE) erase
	$(COVERAGE) run -m pytest
	$(COVERAGE) report
	$(COVERAGE) html
	$(COVERAGE) xml

###############################################################################
# Security
###############################################################################

.PHONY: security

security:
	$(BANDIT) -r .
	$(SEMGREP) scan --config auto
	$(CHECKOV) -d .

###############################################################################
# Documentation
###############################################################################

.PHONY: docs

docs:
	$(MKDOCS) serve

.PHONY: docs-build

docs-build:
	$(MKDOCS) build

###############################################################################
# Docker
###############################################################################

.PHONY: docker

docker:
	$(DOCKER) build -t institutional-quant-platform .

.PHONY: docker-run

docker-run:
	$(DOCKER) run --rm -it -p 8501:8501 institutional-quant-platform

###############################################################################
# Terraform
###############################################################################

.PHONY: terraform

terraform:
	cd infrastructure/terraform && \
	$(TERRAFORM) init && \
	$(TERRAFORM) validate && \
	$(TERRAFORM) fmt -recursive

###############################################################################
# Helm
###############################################################################

.PHONY: helm

helm:
	$(HELM) lint infrastructure/helm

###############################################################################
# Benchmark
###############################################################################

.PHONY: benchmark

benchmark:
	$(PYTEST) -m benchmark

###############################################################################
# Clean
###############################################################################

.PHONY: clean

clean:
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type d -name ".pytest_cache" -exec rm -rf {} +
	find . -type d -name ".ruff_cache" -exec rm -rf {} +
	find . -type d -name ".mypy_cache" -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	rm -rf htmlcov
	rm -rf .coverage
	rm -rf coverage.xml
	rm -rf coverage.json
	rm -rf dist
	rm -rf build

###############################################################################
# Complete CI Pipeline
###############################################################################

.PHONY: ci

ci: format lint typecheck test coverage security docs-build

###############################################################################
# End
###############################################################################