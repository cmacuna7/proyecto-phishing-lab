# Atajos del laboratorio (requiere Docker + Docker Compose y `make`; en Windows usar scripts/corrida.ps1).
.PHONY: dirs up down reset baseline hardened corrida run-mode analyze compare test qr

COMPOSE = docker compose
MODE   ?= hardened
PERSONA ?= sin-nombre
CORRIDA ?= evidence/corridas/$(shell date +%F)_$(PERSONA)

dirs:
	mkdir -p logs/apache logs/nginx logs/app-apache logs/app-nginx data/app-apache data/app-nginx
	chmod -R a+rwX logs data

up: dirs
	CONTROLS_MODE=$(MODE) $(COMPOSE) up -d --build --wait

down:
	$(COMPOSE) down

# Borra estado (bloqueos y usuarios) y logs de las apps para empezar una corrida limpia.
reset: down
	rm -rf data logs

baseline:   ## sin controles (estado "antes")
	$(MAKE) reset && $(MAKE) up MODE=baseline

hardened:   ## con controles (estado "después")
	$(MAKE) reset && $(MAKE) up MODE=hardened

# Corrida completa por persona: make corrida PERSONA=nombre-apellido  (no sobrescribe: falla si la carpeta existe)
corrida:
	test ! -e $(CORRIDA) || (echo "Ya existe $(CORRIDA); use CORRIDA=<otra carpeta>" && false)
	$(MAKE) baseline && $(MAKE) run-mode MODE=baseline CORRIDA=$(CORRIDA)
	$(MAKE) hardened && $(MAKE) run-mode MODE=hardened CORRIDA=$(CORRIDA)
	$(MAKE) analyze CORRIDA=$(CORRIDA)

# client1 pasa por ZAP (proxy); client2 va directo (para comparar la IP de origen observada).
run-mode:
	for t in apache nginx; do \
	  $(COMPOSE) exec client1 python scripts/run_scenario.py --target $$t --mode $(MODE) --out-dir $(CORRIDA)/resultados && \
	  $(COMPOSE) exec client1 python scripts/zap_export.py --baseurl http://$$t --out $(CORRIDA)/zap/$${t}_$(MODE).csv || exit 1; \
	done
	mkdir -p $(CORRIDA)/logs && cp -r logs $(CORRIDA)/logs/$(MODE) && find $(CORRIDA)/logs -name '*.pid' -delete

analyze:
	for m in baseline hardened; do for t in apache nginx; do \
	  a=$(CORRIDA)/logs/$$m/app-$$t/auth.log; \
	  python3 scripts/analyze_logs.py $$( [ -f $$a ] && echo --audit $$a ) --access $$t=$(CORRIDA)/logs/$$m/$$t/access.log \
	    --zap-csv $(CORRIDA)/zap/$${t}_$$m.csv --out $(CORRIDA)/analisis/$${t}_$$m.md > /dev/null || exit 1; \
	done; done
	python3 scripts/compare_results.py --results "$(CORRIDA)/resultados/*.json" --out $(CORRIDA)/analisis/comparacion.md
	$(MAKE) compare

compare:    ## todas las corridas: evidence/corridas/comparacion.md
	python3 scripts/compare_results.py > /dev/null

test:
	cd app && python3 -m pytest -q

qr:
	$(COMPOSE) exec client1 python scripts/make_qr.py http://apache/r/qr1 --out phishing/qr_apache.png
	$(COMPOSE) exec client1 python scripts/make_qr.py http://nginx/r/qr1  --out phishing/qr_nginx.png
