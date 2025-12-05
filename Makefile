# ==================================================================================
# 🎯 MAKEFILE - Lab 3: Kafka + MongoDB
# ==================================================================================
# Comandos útiles para gestionar el laboratorio
#
# Uso: make <comando>
# Ejemplo: make clean-ports
#
# ==================================================================================

.PHONY: help clean-ports start stop restart status logs install test clean-all verify

# Colores para output
RED=\033[0;31m
GREEN=\033[0;32m
YELLOW=\033[1;33m
BLUE=\033[0;34m
NC=\033[0m # No Color

# ==================================================================================
# 📖 HELP - Mostrar todos los comandos disponibles
# ==================================================================================
help:
	@echo "$(BLUE)╔════════════════════════════════════════════════════════════╗$(NC)"
	@echo "$(BLUE)║  Lab 3: Kafka + MongoDB - Makefile Commands              ║$(NC)"
	@echo "$(BLUE)╚════════════════════════════════════════════════════════════╝$(NC)"
	@echo ""
	@echo "$(GREEN)🚀 Comandos de Inicio:$(NC)"
	@echo "  $(YELLOW)make start$(NC)          - Iniciar todos los servicios"
	@echo "  $(YELLOW)make stop$(NC)           - Detener todos los servicios"
	@echo "  $(YELLOW)make restart$(NC)        - Reiniciar todos los servicios"
	@echo ""
	@echo "$(GREEN)🧹 Comandos de Limpieza:$(NC)"
	@echo "  $(YELLOW)make clean-ports$(NC)    - Liberar puertos 2181, 9092, 27017, 8080, 8081"
	@echo "  $(YELLOW)make clean-all$(NC)      - Detener TODOS los contenedores y limpiar"
	@echo ""
	@echo "$(GREEN)📊 Comandos de Monitoreo:$(NC)"
	@echo "  $(YELLOW)make status$(NC)         - Ver estado de servicios"
	@echo "  $(YELLOW)make logs$(NC)           - Ver logs de todos los servicios"
	@echo "  $(YELLOW)make verify$(NC)         - Verificar que todo funciona correctamente"
	@echo ""
	@echo "$(GREEN)🔧 Comandos de Utilidad:$(NC)"
	@echo "  $(YELLOW)make install$(NC)        - Instalar dependencias Python"
	@echo "  $(YELLOW)make test$(NC)           - Probar conexiones a Kafka y MongoDB"
	@echo ""
	@echo "$(GREEN)🌐 URLs de Acceso:$(NC)"
	@echo "  Kafka UI:       http://localhost:8080"
	@echo "  Mongo Express:  http://localhost:8081 (admin/mongopass)"
	@echo ""

# ==================================================================================
# 🧹 CLEAN PORTS - Liberar los puertos usados por este lab
# ==================================================================================
clean-ports:
	@echo "$(YELLOW)🧹 Liberando puertos del Lab 3...$(NC)"
	@echo ""
	@echo "$(BLUE)Deteniendo contenedores del Lab 2 (si existen)...$(NC)"
	@-cd ../2-ETL-kafka && docker compose down 2>/dev/null || true
	@echo ""
	@echo "$(BLUE)Deteniendo contenedores del Lab 3...$(NC)"
	@docker compose down
	@echo ""
	@echo "$(BLUE)Verificando puertos...$(NC)"
	@echo "Puerto 2181 (Zookeeper):"
	@-lsof -ti:2181 && echo "  $(RED)❌ Aún ocupado$(NC)" || echo "  $(GREEN)✅ Libre$(NC)"
	@echo "Puerto 9092 (Kafka):"
	@-lsof -ti:9092 && echo "  $(RED)❌ Aún ocupado$(NC)" || echo "  $(GREEN)✅ Libre$(NC)"
	@echo "Puerto 27017 (MongoDB):"
	@-lsof -ti:27017 && echo "  $(RED)❌ Aún ocupado$(NC)" || echo "  $(GREEN)✅ Libre$(NC)"
	@echo "Puerto 8080 (Kafka UI):"
	@-lsof -ti:8080 && echo "  $(RED)❌ Aún ocupado$(NC)" || echo "  $(GREEN)✅ Libre$(NC)"
	@echo "Puerto 8081 (Mongo Express):"
	@-lsof -ti:8081 && echo "  $(RED)❌ Aún ocupado$(NC)" || echo "  $(GREEN)✅ Libre$(NC)"
	@echo ""
	@echo "$(GREEN)✅ Limpieza completada. Ahora puedes ejecutar: make start$(NC)"

# ==================================================================================
# 🚀 START - Iniciar todos los servicios
# ==================================================================================
start:
	@echo "$(YELLOW)🚀 Iniciando servicios del Lab 3...$(NC)"
	@docker compose up -d
	@echo ""
	@echo "$(BLUE)⏳ Esperando que los servicios inicialicen (30 segundos)...$(NC)"
	@sleep 30
	@echo ""
	@make status
	@echo ""
	@echo "$(GREEN)✅ Servicios iniciados!$(NC)"
	@echo ""
	@echo "$(BLUE)🌐 Acceso Web:$(NC)"
	@echo "  Kafka UI:       http://localhost:8080"
	@echo "  Mongo Express:  http://localhost:8081 (admin/mongopass)"

# ==================================================================================
# 🛑 STOP - Detener servicios (sin borrar datos)
# ==================================================================================
stop:
	@echo "$(YELLOW)🛑 Deteniendo servicios...$(NC)"
	@docker compose stop
	@echo "$(GREEN)✅ Servicios detenidos (datos preservados)$(NC)"

# ==================================================================================
# 🔄 RESTART - Reiniciar todos los servicios
# ==================================================================================
restart:
	@echo "$(YELLOW)🔄 Reiniciando servicios...$(NC)"
	@docker compose restart
	@echo "$(BLUE)⏳ Esperando reinicio (20 segundos)...$(NC)"
	@sleep 20
	@make status

# ==================================================================================
# 📊 STATUS - Ver estado de los servicios
# ==================================================================================
status:
	@echo "$(BLUE)╔════════════════════════════════════════════════════════════╗$(NC)"
	@echo "$(BLUE)║  Estado de Servicios - Lab 3                             ║$(NC)"
	@echo "$(BLUE)╚════════════════════════════════════════════════════════════╝$(NC)"
	@echo ""
	@docker compose ps

# ==================================================================================
# 📝 LOGS - Ver logs de todos los servicios
# ==================================================================================
logs:
	@echo "$(BLUE)📝 Logs de servicios (Ctrl+C para salir)...$(NC)"
	@docker compose logs -f

# Logs de un servicio específico
logs-kafka:
	@docker compose logs -f kafka

logs-mongodb:
	@docker compose logs -f mongodb

logs-zookeeper:
	@docker compose logs -f zookeeper

# ==================================================================================
# 📦 INSTALL - Instalar dependencias Python
# ==================================================================================
install:
	@echo "$(YELLOW)📦 Instalando dependencias Python...$(NC)"
	@pip install -r requirements.txt
	@echo "$(GREEN)✅ Dependencias instaladas$(NC)"

# ==================================================================================
# 🧪 TEST - Probar conexiones
# ==================================================================================
test:
	@echo "$(YELLOW)🧪 Probando conexiones...$(NC)"
	@echo ""
	@echo "$(BLUE)1. Probando MongoDB...$(NC)"
	@docker exec kafka-lab-mongodb mongosh -u admin -p mongopass --eval "db.adminCommand('ping')" --quiet && \
		echo "  $(GREEN)✅ MongoDB: OK$(NC)" || echo "  $(RED)❌ MongoDB: FAIL$(NC)"
	@echo ""
	@echo "$(BLUE)2. Probando Kafka...$(NC)"
	@docker exec kafka-lab-broker kafka-topics --list --bootstrap-server localhost:9092 2>/dev/null && \
		echo "  $(GREEN)✅ Kafka: OK$(NC)" || echo "  $(RED)❌ Kafka: FAIL$(NC)"
	@echo ""
	@echo "$(BLUE)3. Probando Zookeeper...$(NC)"
	@docker exec kafka-lab-zookeeper bash -c "echo ruok | nc localhost 2181" 2>/dev/null && \
		echo "  $(GREEN)✅ Zookeeper: OK$(NC)" || echo "  $(RED)❌ Zookeeper: FAIL$(NC)"

# ==================================================================================
# 🗑️ CLEAN-ALL - Detener TODO y limpiar volúmenes
# ==================================================================================
clean-all:
	@echo "$(RED)⚠️  ADVERTENCIA: Esto borrará TODOS los datos del lab$(NC)"
	@echo "$(YELLOW)Presiona Ctrl+C para cancelar, Enter para continuar...$(NC)"
	@read confirm
	@echo ""
	@echo "$(YELLOW)🗑️  Deteniendo y limpiando...$(NC)"
	@docker compose down -v
	@echo "$(GREEN)✅ Todo limpio. Los datos han sido borrados.$(NC)"

# ==================================================================================
# ✅ VERIFY - Verificación completa del lab
# ==================================================================================
verify:
	@echo "$(BLUE)╔════════════════════════════════════════════════════════════╗$(NC)"
	@echo "$(BLUE)║  Verificación Completa del Lab 3                         ║$(NC)"
	@echo "$(BLUE)╚════════════════════════════════════════════════════════════╝$(NC)"
	@echo ""
	@echo "$(YELLOW)1. Verificando contenedores...$(NC)"
	@docker compose ps
	@echo ""
	@echo "$(YELLOW)2. Verificando puertos...$(NC)"
	@echo -n "  Puerto 2181 (Zookeeper):  "
	@lsof -ti:2181 > /dev/null && echo "$(GREEN)✅ En uso$(NC)" || echo "$(RED)❌ No disponible$(NC)"
	@echo -n "  Puerto 9092 (Kafka):      "
	@lsof -ti:9092 > /dev/null && echo "$(GREEN)✅ En uso$(NC)" || echo "$(RED)❌ No disponible$(NC)"
	@echo -n "  Puerto 27017 (MongoDB):   "
	@lsof -ti:27017 > /dev/null && echo "$(GREEN)✅ En uso$(NC)" || echo "$(RED)❌ No disponible$(NC)"
	@echo -n "  Puerto 8080 (Kafka UI):   "
	@lsof -ti:8080 > /dev/null && echo "$(GREEN)✅ En uso$(NC)" || echo "$(RED)❌ No disponible$(NC)"
	@echo -n "  Puerto 8081 (Mongo Expr): "
	@lsof -ti:8081 > /dev/null && echo "$(GREEN)✅ En uso$(NC)" || echo "$(RED)❌ No disponible$(NC)"
	@echo ""
	@echo "$(YELLOW)3. Verificando conexiones...$(NC)"
	@make test
	@echo ""
	@echo "$(YELLOW)4. Verificando MongoDB colecciones...$(NC)"
	@docker exec kafka-lab-mongodb mongosh -u admin -p mongopass --quiet --eval \
		"use kafka_events_db; db.getCollectionNames()" 2>/dev/null | grep -E "sensors|ecommerce|mobile" && \
		echo "  $(GREEN)✅ Colecciones inicializadas$(NC)" || echo "  $(YELLOW)⚠️  Sin datos aún$(NC)"
	@echo ""
	@echo "$(GREEN)✅ Verificación completa!$(NC)"

# ==================================================================================
# 🎓 DEMO - Comandos útiles para demos en clase
# ==================================================================================
demo-quick:
	@echo "$(BLUE)🎬 Demo Rápida - Generando datos de prueba...$(NC)"
	@cd src && python producer.py --stream smart_city --duration 1 --rate 5 &
	@sleep 5
	@echo "$(GREEN)✅ Producer corriendo en background$(NC)"
	@echo "$(YELLOW)Ahora ejecuta el consumer en otra terminal:$(NC)"
	@echo "  cd src/consumers && python sensor_mongo_consumer.py"

demo-stop:
	@echo "$(YELLOW)🛑 Deteniendo demos...$(NC)"
	@pkill -f "python producer.py" || true
	@echo "$(GREEN)✅ Demos detenidos$(NC)"

# ==================================================================================
# 📋 SHOW-PORTS - Mostrar qué está usando cada puerto
# ==================================================================================
show-ports:
	@echo "$(BLUE)╔════════════════════════════════════════════════════════════╗$(NC)"
	@echo "$(BLUE)║  Puertos del Lab 3                                       ║$(NC)"
	@echo "$(BLUE)╚════════════════════════════════════════════════════════════╝$(NC)"
	@echo ""
	@echo "$(YELLOW)Puerto 2181 (Zookeeper):$(NC)"
	@lsof -i:2181 || echo "  $(GREEN)✅ Puerto libre$(NC)"
	@echo ""
	@echo "$(YELLOW)Puerto 9092 (Kafka):$(NC)"
	@lsof -i:9092 || echo "  $(GREEN)✅ Puerto libre$(NC)"
	@echo ""
	@echo "$(YELLOW)Puerto 27017 (MongoDB):$(NC)"
	@lsof -i:27017 || echo "  $(GREEN)✅ Puerto libre$(NC)"
	@echo ""
	@echo "$(YELLOW)Puerto 8080 (Kafka UI):$(NC)"
	@lsof -i:8080 || echo "  $(GREEN)✅ Puerto libre$(NC)"
	@echo ""
	@echo "$(YELLOW)Puerto 8081 (Mongo Express):$(NC)"
	@lsof -i:8081 || echo "  $(GREEN)✅ Puerto libre$(NC)"

