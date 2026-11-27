PROM_VERSION ?= 3.5.0
OS   := $(shell uname -s | tr A-Z a-z)
ARCH := $(shell uname -m | sed -e 's/x86_64/amd64/' -e 's/aarch64/arm64/')
PROM_DIR := prometheus-$(PROM_VERSION).$(OS)-$(ARCH)

.PHONY: help prometheus up down status test rules-test compose-up compose-down
help:
	@echo "make prometheus   download prometheus + promtool into ./bin (one time)"
	@echo "make up           start the shop, load and Prometheus locally (no Docker needed)"
	@echo "make status       journey SLI, burn rates, dependencies, alerts"
	@echo "make down         stop everything"
	@echo "make test         unit tests + promtool rule tests"
	@echo "make compose-up   the same lab in Docker, plus Grafana on :3000"

prometheus:
	@mkdir -p bin
	curl -sSL https://github.com/prometheus/prometheus/releases/download/v$(PROM_VERSION)/$(PROM_DIR).tar.gz | tar xz -C bin
	cp bin/$(PROM_DIR)/prometheus bin/$(PROM_DIR)/promtool bin/
	@echo "ok: bin/prometheus and bin/promtool"

up:
	python lab.py up
down:
	python lab.py down
status:
	python lab.py status

rules-test:
	cd rules && ../bin/promtool check rules checkout-slo.yml checkout-probe.yml && ../bin/promtool test rules checkout-slo.test.yml checkout-probe.test.yml

test:
	python -m pytest -q

compose-up:
	docker compose up --build -d
compose-down:
	docker compose down
