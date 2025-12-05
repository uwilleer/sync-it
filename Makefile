-include infra/.env

COMPOSE_DIR := infra/docker
COMPOSE_COMMAND := docker compose -f $(COMPOSE_DIR)/docker-compose.yml --env-file infra/.env
COMPOSE_DEV_FILE := $(COMPOSE_DIR)/docker-compose.dev.yml

SERVICES := api-gateway gpt-api scraper-api telegram-bot vacancy-parser vacancy-processor
MYPY_DIRS := libs $(foreach service,$(SERVICES),services/$(service)/src)

# Проверяем существование dev-файла и добавляем его к COMPOSE_COMMAND если включен режим разработки
ifeq ($(ENV_MODE),development)
	ifeq ($(wildcard $(COMPOSE_DEV_FILE)),$(COMPOSE_DEV_FILE))
		COMPOSE_COMMAND := $(COMPOSE_COMMAND) -f $(COMPOSE_DEV_FILE)
	endif
endif

define compose_action
	@if [ -z "$(s)" ]; then \
		echo $(COMPOSE_COMMAND) $(1) $(e); \
		$(COMPOSE_COMMAND) $(1) $(e); \
	else \
		echo $(COMPOSE_COMMAND) $(1) $(s) $(e); \
		$(COMPOSE_COMMAND) $(1) $(s) $(e); \
	fi
endef

help:
	@awk 'BEGIN {FS = ":.*#"; printf "\nUsage:\n  make \033[36m<target>\033[0m\n"} /^[a-zA-Z_-]+:.*?#/ { printf "  \033[36m%-15s\033[0m %s\n", $$1, $$2 } /^#@/ { printf "\n\033[1m%s\033[0m\n", substr($$0, 5) } ' $(MAKEFILE_LIST)

up: # compose up [s=<service>] [e="<extra> <extra2>"]
	$(call compose_action,up -d --wait)

down: # compose down [s=<service>] [e="<extra> <extra2>"]
	$(call compose_action,down)

stop: # compose stop [s=<service>] [e="<extra> <extra2>"]
	$(call compose_action,stop)

pull: # compose pull
	$(call compose_action,pull)

venv: # create/update venv
	@uv sync --frozen --all-packages

add: # add python package to service p=<package> s=<service> [e="<extra> <extra2>"]
	@if [ -z "$(p)" ] || [ -z "$(s)" ]; then \
		echo 'Usage: make add s=<service> p=<package> [e="<extra> <extra2>"]'; \
		exit 1; \
	fi; \
	uv add $(p) --package $(s) $(e);

lint: # run linters and formatters
	@uv run ruff check .
	@uv run ruff format --check .
	@uv run isort . --check-only
	@$(foreach dir,$(MYPY_DIRS),uv run mypy $(dir) && echo $(dir);)

lint-fix: # run linters and formatters with fix
	@uv run ruff check .
	@uv run ruff format .
	@uv run isort .
	@$(foreach dir,$(MYPY_DIRS),uv run mypy $(dir) && echo $(dir);)

mm: # create migration s=<service> m="migration message"
	@if [ -z "$(s)" ] || [ -z "$(m)" ]; then \
		echo 'Usage: make mm s=<service_name> m="migration message"'; \
		exit 1; \
	fi;
	$(COMPOSE_COMMAND) run --quiet --no-TTY --workdir /app/services/$(s) --rm $(s)-migrator alembic revision --autogenerate -m "$(m)"

migrate: # apply migrations [s=<service>]
	@if [ -z "$(s)" ]; then \
  		echo "Searching services for migrations..."; \
		for service in $(SERVICES); do \
			if $(COMPOSE_COMMAND) --profile migrator config --services | grep -q "^$$service-migrator$$"; then \
				echo "Applying migrations for $$service..."; \
				$(COMPOSE_COMMAND) run --quiet --no-TTY --workdir /app/services/$$service --rm $$service-migrator alembic upgrade head; \
			fi; \
		done; \
		echo "Migrations applied for all services with migrator"; \
	else \
		echo "Applying migrations for service $(s)..."; \
		if $(COMPOSE_COMMAND) --profile migrator config --services | grep -q "^$(s)-migrator$$"; then \
			$(COMPOSE_COMMAND) run --quiet --no-TTY --workdir /app/services/$(s) --rm $(s)-migrator alembic upgrade head; \
		else \
			echo "No migrator service for $(s)"; \
			exit 1; \
		fi; \
		echo "Migrations applied for service $(s)"; \
	fi

downgrade: # downgrade migration s=<service> r=<revision>
	@if [ -z "$(s)" ] || [ -z "$(r)" ]; then \
		echo "Usage: make downgrade s=<service_name> r=<revision>"; \
		exit 1; \
	fi; \
	$(COMPOSE_COMMAND) run --quiet --no-TTY --workdir /app/services/$(s) --rm $(s)-migrator alembic downgrade $(r)
