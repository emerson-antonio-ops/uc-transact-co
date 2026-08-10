SHELL := /bin/bash
-include .env

COMPOSE := docker compose
UV := uv run
SCENARIO ?= live
DEFECT ?=
POSTGRES_DB ?= transactco
ANALYTICS_RO_USER ?= analytics_ro
ANALYTICS_RO_PASSWORD ?= analytics_ro

.DEFAULT_GOAL := help
.PHONY: help setup bootstrap doctor test verify dbt-check up down seed land inject inject-quiet reveal score status reset psql psql-ro query query-ro clean

help: ## Show this help
	@echo ""
	@echo "  TransactCo · the analytics are killing the store"
	@echo ""
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) \
		| awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-14s\033[0m %s\n", $$1, $$2}'
	@echo ""

setup: ## First run: create .env, install deps, pre-warm the DuckDB extension
	@test -f .env || (cp .env.example .env && echo "  created .env from .env.example")
	uv sync --extra dbt
	@$(UV) python -c "import duckdb; c=duckdb.connect(); c.execute('INSTALL postgres'); c.execute('LOAD postgres'); print('  duckdb postgres extension ready')"

bootstrap: ## Rebuild and prove the complete clean Day 1 baseline
	@$(MAKE) setup
	@$(MAKE) up
	@$(MAKE) doctor
	@$(MAKE) seed
	@$(MAKE) clean
	@$(MAKE) land
	@$(MAKE) test
	@$(MAKE) verify
	@$(MAKE) dbt-check

doctor: ## Check Postgres, the schema, the seal and the DuckDB extension
	@$(UV) transactco doctor

test: ## Run the fast unit contract checks
	@$(UV) python -m unittest discover -s tests -v

verify: ## Verify the clean baseline, landing parity and oracle isolation
	@$(UV) transactco verify

dbt-check: ## Validate the empty dbt shell without building student models
	@cd dbt && $(UV) dbt debug --profiles-dir .
	@cd dbt && $(UV) dbt parse --profiles-dir .

up: ## Start Postgres and apply the schema
	$(COMPOSE) up -d --wait

down: ## Stop Postgres, keep the data
	$(COMPOSE) down

seed: ## Load correlated data and verify the baseline is clean
	@$(UV) transactco seed

land: ## Carry public.* into raw.* in warehouse.duckdb (read-only ATTACH)
	@$(UV) transactco land

inject: ## Inject defects (SCENARIO=live|deep|all|smoke, or DEFECT=name)
	@if [ -n "$(DEFECT)" ]; then \
		$(UV) transactco inject --defect $(DEFECT); \
	else \
		$(UV) transactco inject --scenario $(SCENARIO); \
	fi

inject-quiet: ## Inject in silence — the Day 4 version, says nothing about what landed
	@if [ -n "$(DEFECT)" ]; then \
		$(UV) transactco inject --quiet --defect $(DEFECT); \
	else \
		$(UV) transactco inject --quiet --scenario $(SCENARIO); \
	fi

reveal: ## Open the sealed oracle
	@$(UV) transactco reveal

score: ## Score analytics.detections against the oracle
	@$(UV) transactco score

status: ## Row counts and freshness (no spoilers)
	@$(UV) transactco status

defects: ## List the 14 injectable defects
	@$(UV) transactco defects

reset: ## Destroy the database and rebuild it clean
	$(COMPOSE) down -v
	$(COMPOSE) up -d --wait
	@$(UV) transactco seed
	@rm -f warehouse.duckdb warehouse.duckdb.wal

psql: ## Open psql inside the container
	$(COMPOSE) exec postgres psql -U transactco -d transactco

psql-ro: ## Open Postgres with the Day 1 read-only role
	$(COMPOSE) exec -e PGPASSWORD=$(ANALYTICS_RO_PASSWORD) postgres \
		psql -U $(ANALYTICS_RO_USER) -d $(POSTGRES_DB)

# Exported rather than interpolated into the recipe so multi-line SQL survives.
export Q
query: ## Run SQL against the warehouse: make query Q="select 1"
	@$(UV) python -c "import duckdb,os; duckdb.connect('warehouse.duckdb').sql(os.environ['Q']).show(max_rows=200)"

query-ro: ## Run read-only SQL against the warehouse: make query-ro Q="select 1"
	@$(UV) python -c "import duckdb,os; duckdb.connect('warehouse.duckdb', read_only=True).sql(os.environ['Q']).show(max_rows=200)"

clean: ## Remove the warehouse file
	rm -f warehouse.duckdb warehouse.duckdb.wal
