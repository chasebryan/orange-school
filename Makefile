PYTHON ?= python3
ORANGE_REPO ?= ../orange

.PHONY: check validate test host-examples examples professional-complete

check: validate test host-examples examples

validate:
	$(PYTHON) scripts/validate_curriculum.py --root .

test:
	$(PYTHON) -m unittest discover -s tests -v

host-examples:
	$(PYTHON) scripts/check_host_examples.py --root .

examples:
	ORANGE_REPO="$(ORANGE_REPO)" $(PYTHON) scripts/check_orange_examples.py --root .

professional-complete:
	$(PYTHON) scripts/validate_curriculum.py --root . --require-professional-complete
