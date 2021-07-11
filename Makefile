install:
	pip install --upgrade pip
	pip install -r requirements.txt

dev: install
	pip install -r dev-requirements.txt

test:
	python -m pytest tests/
