all: format lint test

format:
	poetry run black .
	poetry run isort .

lint:

test:
