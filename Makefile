.PHONY: help install db-up db-down db-reset db-init serve test test-offline clean

COMPOSE ?= docker compose
DB_CONTAINER ?= chatbot_mariadb

help:
	@echo "make install       install the Python dependencies"
	@echo "make db-up         start MariaDB + phpMyAdmin (the database is seeded on first start)"
	@echo "make db-init       reload db/ecommerce.sql and db/seed_extra.sql into the running container"
	@echo "make db-down       stop the containers (data is kept in the volume)"
	@echo "make db-reset      stop the containers and delete the database volume"
	@echo "make serve         start the Flask server on http://localhost:5000"
	@echo "make test          run the 15 scenarios against a running server"
	@echo "make test-offline  run the tool-loop tests (no key, no database needed)"

install:
	pip install -r requirements.txt

db-up:
	$(COMPOSE) up -d

db-down:
	$(COMPOSE) down

db-reset:
	$(COMPOSE) down -v

db-init:
	docker exec -i $(DB_CONTAINER) mariadb -uroot ecommerce < db/ecommerce.sql
	docker exec -i $(DB_CONTAINER) mariadb -uroot ecommerce < db/seed_extra.sql

serve:
	python server.py

test:
	python tests/test_all_scenarios.py

test-offline:
	python tests/test_tool_loop.py

clean:
	find . -name __pycache__ -type d -prune -exec rm -rf {} +
