.PHONY: help install setup db-start db-stop db-init fresh clean test serve

help:
	@echo ==========================================
	@echo   Multi-Agent E-Commerce Chatbot
	@echo ==========================================
	@echo ""
	@echo "Commandes disponibles:"
	@echo "  make install - Installer dependances Python"
	@echo "  make setup   - Installation complete"
	@echo "  make fresh   - Reinstallation complete"
	@echo "  make serve   - Demarrer serveur"
	@echo "  make test    - Lancer tests"
	@echo ""

install:
	@echo "[INFO] Installation dependances..."
	@pip install -r requirements.txt > nul 2>&1
	@echo "[SUCCESS] Dependances installees"

setup: install db-start db-init
	@echo "[SUCCESS] Setup termine"

fresh: db-stop clean
	@echo "[INFO] Suppression volumes Docker..."
	@docker volume rm multi-agent-chatbot_chatbot_db_data 2> nul || true
	@docker volume prune -f > nul 2>&1 || true
	@echo "[INFO] Reinstallation..."
	@pip install -r requirements.txt > nul 2>&1
	@docker-compose up -d
	@echo "[INFO] Attente MySQL 15s..."
	@sleep 15 2> nul || ping 127.0.0.1 -n 16 > nul
	@docker exec -i chatbot_mariadb mariadb -uroot -e "CREATE DATABASE IF NOT EXISTS ecommerce" 2> nul || true
	@docker exec -i chatbot_mariadb mariadb -uroot ecommerce < ecommerce.sql
	@echo "[SUCCESS] Installation terminee"

db-start:
	@echo "[INFO] Demarrage Docker..."
	@docker-compose up -d
	@echo "[INFO] Attente 10s..."
	@sleep 10 2> nul || ping 127.0.0.1 -n 11 > nul
	@echo "[SUCCESS] Docker demarre"

db-stop:
	@echo "[INFO] Arret Docker..."
	@docker-compose down > nul 2>&1 || true
	@echo "[SUCCESS] Docker arrete"

db-init:
	@echo "[INFO] Init base..."
	@sleep 5 2> nul || ping 127.0.0.1 -n 6 > nul
	@docker exec -i chatbot_mariadb mariadb -uroot -e "CREATE DATABASE IF NOT EXISTS ecommerce" 2> nul || true
	@docker exec -i chatbot_mariadb mariadb -uroot ecommerce < ecommerce.sql
	@echo "[SUCCESS] Base initialisee"

serve:
	@echo "[INFO] Demarrage serveur..."
	@python server.py

test:
	@echo "[INFO] Tests..."
	@python tests/test_all_scenarios.py

clean:
	@echo "[INFO] Nettoyage..."
	@rm -rf __pycache__ 2> nul || true
	@rm -rf agents/__pycache__ 2> nul || true
	@rm -rf core/__pycache__ 2> nul || true
	@rm -rf forms/__pycache__ 2> nul || true
	@rm -rf tools/__pycache__ 2> nul || true
	@rm -rf db_data 2> nul || true
	@echo "[SUCCESS] Nettoye"
