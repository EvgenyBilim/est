SERVICE_DIR := src
TXT_BOLD := \e[1m
TXT_MAGENTA := \e[35m
TXT_RESET := \e[0m

setup:
	@poetry install --sync

setup-pre-commit:
	@poetry run pre-commit install

lint:
	@printf "${TXT_BOLD}${TXT_MAGENTA}========================== RUFF FORMAT ============================${TXT_RESET}\n"
	@poetry run ruff format $(SERVICE_DIR)/ tests/
	@printf "${TXT_BOLD}${TXT_MAGENTA}=========================== RUFF LINT =============================${TXT_RESET}\n"
	@poetry run ruff check --fix --show-fixes --exit-non-zero-on-fix .
	@printf "${TXT_BOLD}${TXT_MAGENTA}=========================== MYPY =================================${TXT_RESET}\n"
	@poetry run mypy $(SERVICE_DIR)/

format:
	@poetry run ruff format $(SERVICE_DIR)/ tests/

test:
	@poetry run pytest tests/ -vv

migration:
	@poetry run alembic revision --autogenerate

migrate:
	@poetry run alembic upgrade head

start-docker:
	docker-compose up postgres -d

stop-docker:
	docker-compose down

start_http:
	@poetry run python -m src.api.app
