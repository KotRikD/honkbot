.PHONY: all test apidoc

python=python3

all:
	$(python) example/run.py

apidoc:
	sphinx-apidoc -o docs/src/ . $(PWD)/setup.py

test:
	$(python) -m unittest discover -s test
