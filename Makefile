# Atajos del laboratorio (requiere Docker + Docker Compose y `make`; en Windows usar Git Bash/WSL,
# o copiar los comandos de cada objetivo en PowerShell).
.PHONY: dirs up down reset baseline hardened scenario-apache scenario-nginx zap-export analyze compare test qr

COMPOSE = docker compose
MODE   ?= hardened

dirs:
	mkdir -p logs/apache logs/nginx logs/app-apache logs/app-nginx data/app-apache data/app-nginx
	chmod -R a+rwX logs data

up: dirs
	CONTROLS_MODE=$(MODE) $(COMPOSE) up -d --build

down:
	$(COMPOSE) down

# Borra estado (bloqueos y usuarios) y logs de las apps para empezar una corrida limpia.
reset: down
	rm -rf data logs

baseline:   ## sin controles (estado "antes")
	$(MAKE) reset && $(MAKE) up MODE=baseline

hardened:   ## con controles (estado "después")
	$(MAKE) reset && $(MAKE) up MODE=hardened

# client1 pasa por ZAP (proxy); client2 va directo (para comparar la IP de origen observada).
scenario-apache:
	$(COMPOSE) exec client1 python scripts/run_scenario.py --target apache --mode $(MODE)
scenario-nginx:
	$(COMPOSE) exec client1 python scripts/run_scenario.py --target nginx --mode $(MODE)

zap-export:
	$(COMPOSE) exec client1 python scripts/zap_export.py --zap http://zap:8090 --baseurl http://apache --out evidence/zap/apache_$(MODE).csv
	$(COMPOSE) exec client1 python scripts/zap_export.py --zap http://zap:8090 --baseurl http://nginx  --out evidence/zap/nginx_$(MODE).csv

analyze:
	python3 scripts/analyze_logs.py --audit logs/app-apache/auth.log --access apache=logs/apache/access.log --zap-csv evidence/zap/apache_$(MODE).csv --out evidence/analisis/apache_$(MODE).md
	python3 scripts/analyze_logs.py --audit logs/app-nginx/auth.log  --access nginx=logs/nginx/access.log  --zap-csv evidence/zap/nginx_$(MODE).csv  --out evidence/analisis/nginx_$(MODE).md

compare:
	python3 scripts/compare_results.py

test:
	cd app && python3 -m pytest -q

qr:
	$(COMPOSE) exec client1 python scripts/make_qr.py http://apache/r/qr1 --out phishing/qr_apache.png
	$(COMPOSE) exec client1 python scripts/make_qr.py http://nginx/r/qr1  --out phishing/qr_nginx.png
