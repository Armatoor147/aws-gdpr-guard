SHELL := /bin/bash
PYTHON ?= python3
.PHONY: virtual-environment upgrade-pip requirements run-black run-bandit run-pytest run-coverage run-pip-audit run-checks

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

upgrade-pip:
	@echo
	@echo "\033[1;31m"
	@echo "   >>> Upgrading pip"
	@echo "\033[0m"
	$(call execute_in_venv, python -m pip install --upgrade pip)

requirements:
	@echo
	@echo "\033[1;31m"
	@echo "   >>> Installing requirements from requirements.txt"
	@echo "\033[0m"
	$(call execute_in_venv, pip install -r requirements.txt)

setup:
	@$(MAKE) virtual-environment ; \
	$(MAKE) upgrade-pip ; \
	$(MAKE) requirements ;

run-black:
	@echo
	@echo "\033[1;31m"
	@echo "   >>> Running black"
	@echo "\033[0m"
	$(call execute_in_venv, black --check aws_gdpr_guard/ test/)

run-bandit:
	@echo
	@echo "\033[1;31m"
	@echo "   >>> Running bandit"
	@echo "\033[0m"
	$(call execute_in_venv, bandit -r aws_gdpr_guard/ test/)

run-pytest:
	@echo
	@echo "\033[1;31m"
	@echo "   >>> Running pytest"
	@echo "\033[0m"
	$(call execute_in_venv, pytest test/)

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
	$(call execute_in_venv, pip-audit)

run-checks:
	@$(MAKE) run-black ; \
	$(MAKE) run-bandit ; \
	$(MAKE) run-pytest ; \
	$(MAKE) run-coverage ; \
	$(MAKE) run-pip-audit