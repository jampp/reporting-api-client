current_branch := $(shell git rev-parse --abbrev-ref HEAD)
.PHONY: clean clean-test clean-pyc clean-build docs help
.DEFAULT_GOAL := help

define BROWSER_PYSCRIPT
import os, webbrowser, sys

try:
	from urllib import pathname2url
except:
	from urllib.request import pathname2url

webbrowser.open("file://" + pathname2url(os.path.abspath(sys.argv[1])))
endef
export BROWSER_PYSCRIPT

define PRINT_HELP_PYSCRIPT
import re, sys

for line in sys.stdin:
	match = re.match(r'^([a-zA-Z_-]+):.*?## (.*)$$', line)
	if match:
		target, help = match.groups()
		print("%-20s %s" % (target, help))
endef
export PRINT_HELP_PYSCRIPT

BROWSER := python -c "$$BROWSER_PYSCRIPT"
CURRENT_DIR = $(shell pwd)

help:
	@python -c "$$PRINT_HELP_PYSCRIPT" < $(MAKEFILE_LIST)

clean: clean-build clean-pyc clean-test ## remove all build, test, coverage and Python artifacts

clean-build: ## remove build artifacts
	rm -fr build/
	rm -fr dist/
	rm -fr .eggs/
	find . -name '*.egg-info' -exec rm -fr {} +
	find . -name '*.egg' -exec rm -f {} +

clean-pyc: ## remove Python file artifacts
	find . -name '*.pyc' -exec rm -f {} +
	find . -name '*.pyo' -exec rm -f {} +
	find . -name '*~' -exec rm -f {} +
	find . -name '__pycache__' -exec rm -fr {} +

clean-test: ## remove test and coverage artifacts
	rm -fr .tox/
	rm -f .coverage
	rm -fr htmlcov/
	rm -fr .pytest_cache

lint: ## check style with flake8
	flake8 setup.py reporting_api_client tests
	mypy reporting_api_client

format: ## Format files using black
	black .

test: ## run tests quickly with the default Python
	py.test

coverage: ## check code coverage quickly with the default Python
	coverage run --source reporting_api_client -m pytest

docs: ## generate Sphinx HTML documentation, including API docs
	$(MAKE) -C docs -e clean
	$(MAKE) -C docs -e html

docs-show: docs ## generate sphinx HTML documentation and open it on a Browser
	$(BROWSER) docs/_build/html/index.html

docs-doc8: ## check rST files for errors
	doc8

docs-spelling: ## check the doc for spelling errors
	$(MAKE) -C docs -e spelling

release: dist ## package and upload a release
	twine upload -u $(shell echo PYPI_USERNAME) -p $(shell echo PYPI_PASSWORD) dist/*

dist: clean ## builds source and wheel package
	python setup.py sdist
	python setup.py bdist_wheel
	pip install twine
	ls -l dist

install: clean ## install the package to the active Python's site-packages
	python setup.py install

build:
	docker build -t docker.jampp.com/reporting-api-client:$(current_branch) ./

test-unit:
	docker run --rm \
		docker.jampp.com/reporting-api-client:$(current_branch) \
		run_tests
