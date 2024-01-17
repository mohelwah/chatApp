install:
	python.exe -m pip install --upgrade pip &&\
		pip install -r requirements.txt

test:
	python -m pytest -vv test_hello.py

format:
	black app/

lint:
	pylint --disable=R,C app/

all: install format lint test