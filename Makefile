lint:
	isort --check --diff --profile black src/ tests/
	black --check --diff src/ tests/

format:
	isort --profile black src/ tests/
	black src/ tests/

test:
	pytest

cov:
	pytest --cov=src
