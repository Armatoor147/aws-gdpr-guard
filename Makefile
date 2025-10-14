SHELL := /bin/bash
PYTHON ?= python3
.PHONY: virtual-environment requirements run-black run-bandit run-pytest run-coverage run-pip-audit run-checks

virtual-environment:
	@if [ ! -d "venv" ]; then \
		echo ; \
		echo "   >>> Creating virtual environment with $(PYTHON)"; \
		$(PYTHON) -m venv venv; \
	else \
		echo ; \
		echo "   >>> Virtual environment already exists (venv/)"; \
	fi

ACTIVATE_ENV := source venv/bin/activate

define execute_in_venv
	$(ACTIVATE_ENV) && $1
endef

requirements:
	@echo
	@echo "\033[1;31m"
	@echo "   >>> Installing requirements from requirements-dev.txt"
	@echo "\033[0m"
	$(call execute_in_venv, pip install -r requirements-dev.txt)

setup:
	@$(MAKE) virtual-environment ; \
	$(MAKE) requirements ;

run-black:
	@echo
	@echo "\033[1;31m"
	@echo "   >>> Running black"
	@echo "\033[0m"
	$(call execute_in_venv, black --check aws_gdpr_guard/ tests/)

run-bandit:
	@echo
	@echo "\033[1;31m"
	@echo "   >>> Running bandit"
	@echo "\033[0m"
	$(call execute_in_venv, bandit -r aws_gdpr_guard/)

run-pytest:
	@echo
	@echo "\033[1;31m"
	@echo "   >>> Running pytest"
	@echo "\033[0m"
	$(call execute_in_venv, coverage run -m pytest tests/)

run-coverage:
	@echo
	@echo "\033[1;31m"
	@echo "   >>> Running coverage"
	@echo "\033[0m"
	$(call execute_in_venv, coverage report -m)

run-pip-audit:
	@echo
	@echo "\033[1;31m"
	@echo "   >>> Running pip-audit"
	@echo "\033[0m"
	$(call execute_in_venv, pip-audit --ignore-vuln GHSA-4xh5-x5gv-qwph)

run-checks:
	@$(MAKE) run-black ; \
	$(MAKE) run-bandit ; \
	$(MAKE) run-pytest ; \
	$(MAKE) run-coverage ; \
	$(MAKE) run-pip-audit