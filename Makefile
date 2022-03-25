all:
	echo "Please check the Makefile for available targets"

VERSION := $(shell python3 -c "import setup; print(setup.metadata.version)")

### Prepare the virtual env

install-pyrun:
	install-pyrun --python=3.10 pyenv

install-venv:
	python3 -m venv pyenv

packages:
	pip install -r requirements.txt

dev-packages:   packages
	pip install -r requirements-dev.txt

### Build

clean:
	find . -name '*~' -or -name '*.bak' -exec rm {} ';'

distclean:	clean
	rm -rf build dist *.egg-info __pycache__

create-dist:
	echo "Building distributions for version $(VERSION)"
	python3 setup.py sdist bdist_wheel

test-upload:
	python3 -m twine upload -r testpypi dist/*$(VERSION)*

prod-upload:
	python3 -m twine upload -r pypi dist/*$(VERSION)*

### Run the bot

run:
	python3 -m telegram_antispam_bot
