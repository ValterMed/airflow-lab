# 🛠️ Setup Guide - Kafka + MongoDB Laboratory

## 📋 Prerequisites Checklist

Before starting this lab, ensure you have:

- [ ] **Docker Desktop** installed and running
  - macOS: [Download Docker Desktop](https://www.docker.com/products/docker-desktop)
  - Windows: Requires WSL2 + Docker Desktop
  - Linux: Docker Engine + Docker Compose
  
- [ ] **Python 3.8+** installed
  ```bash
  python --version  # Should show 3.8 or higher
  ```

- [ ] **Lab 2 completed** (Kafka fundamentals)

- [ ] **Minimum system resources**:
  - 8GB RAM (16GB recommended)
  - 10GB free disk space
  - 4 CPU cores

---

## 🚀 Step-by-Step Setup

### Step 1: Navigate to Lab Directory

```bash
cd laboratories/3-kafka-mongodb-persistence
```

### Step 2: Start Docker Services

```bash
# Start all services in detached mode
docker-compose up -d

# Expected output:
# Creating network "kafka-mongo-network" ... done
# Creating volume "kafka-lab-zookeeper-data" ... done
# Creating volume "kafka-lab-mongodb-data" ... done
# Creating kafka-lab-zookeeper ... done
# Creating kafka-lab-kafka ... done
# Creating kafka-lab-mongodb ... done
# Creating kafka-lab-mongo-express ... done
# Creating kafka-lab-ui ... done
```

### Step 3: Wait for Services to Initialize

Services need time to start properly. Wait **30-60 seconds**, then verify:

```bash
# Check service status
docker-compose ps

# Expected output (all should show "Up"):
# NAME                    STATUS          PORTS
# kafka-lab-broker        Up             0.0.0.0:9092->9092/tcp
# kafka-lab-zookeeper     Up             0.0.0.0:2181->2181/tcp
# kafka-lab-mongodb       Up             0.0.0.0:27017->27017/tcp
# kafka-lab-mongo-express Up             0.0.0.0:8081->8081/tcp
# kafka-lab-ui            Up             0.0.0.0:8080->8080/tcp
```

### Step 4: Verify Service Health

#### Check Zookeeper
```bash
docker exec kafka-lab-zookeeper bash -c "echo ruok | nc localhost 2181"
# Expected: imok
```

#### Check Kafka
```bash
docker exec kafka-lab-broker kafka-broker-api-versions --bootstrap-server localhost:9092 | head -n 1
# Should show Kafka version info without errors
```

#### Check MongoDB
```bash
docker exec kafka-lab-mongodb mongosh -u admin -p mongopass --eval "db.adminCommand('ping')"
# Expected: { ok: 1 }
```

### Step 5: Verify Web Interfaces

#### Kafka UI
1. Open browser: http://localhost:8080
2. You should see "Kafka Clusters" page
3. Click on "local" cluster
4. Navigate to "Topics" - should be empty initially

#### Mongo Express
1. Open browser: http://localhost:8081
2. Login with:
   - Username: `admin`
   - Password: `mongopass`
3. You should see `kafka_events_db` database
4. Click it to see 3 collections: `sensors`, `ecommerce`, `mobile_events`

### Step 6: Install Python Dependencies

#### Option A: Using Virtual Environment (Recommended)

```bash
# Create virtual environment
python -m venv venv

# Activate it
# macOS/Linux:
source venv/bin/activate
# Windows:
venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Verify installation
pip list | grep -E "kafka-python|pymongo"
# Should show:
# kafka-python 2.0.2
# pymongo      4.6.1
```

#### Option B: System-wide Installation

```bash
pip install -r requirements.txt
```

### Step 7: Verify MongoDB Collections

**¿Qué pasó aquí?** 🤔

Cuando MongoDB arrancó por primera vez, Docker ejecutó automáticamente el archivo `init-mongo.js`. Este script:
- ✅ Creó la base de datos `kafka_events_db`
- ✅ Creó 3 colecciones con schema validation
- ✅ Creó índices para performance
- ✅ Insertó 3 documentos de ejemplo

**📖 Nota sobre `init-mongo.js`:**
- Es JavaScript porque MongoDB Shell ejecuta JS nativamente
- Es el método ESTÁNDAR en la industria (Docker + MongoDB)
- Se ejecuta automáticamente (no requiere pasos manuales)
- Solo se ejecuta UNA VEZ (primera vez que arranca MongoDB)

```bash
# Access MongoDB shell
docker exec -it kafka-lab-mongodb mongosh -u admin -p mongopass

# Run these commands:
use kafka_events_db
show collections
# Should show: ecommerce, mobile_events, sensors

db.sensors.countDocuments()
# Should show: 3 (sample documents insertados por init-mongo.js)

# Ver un documento de ejemplo
db.sensors.findOne()

exit
```

**🔄 Para resetear la base de datos:**
```bash
# Esto borrará TODO y re-ejecutará init-mongo.js
docker-compose down -v
docker-compose up -d
sleep 30  # Esperar inicialización
```

### Step 8: Kafka Topics (Auto-creados)

**📝 Nota**: Los topics de Kafka se crean **automáticamente** cuando el producer envía el primer mensaje.

Esto está habilitado en `docker-compose.yml`:
```yaml
KAFKA_AUTO_CREATE_TOPICS_ENABLE: 'true'
```

**No necesitas crear los topics manualmente.** Simplemente ejecuta el producer y se crearán:
- `smart-city-sensors`
- `ecommerce-events`
- `mobile-analytics`

**💡 Para verificar topics** (opcional, después de ejecutar el producer):
```bash
# Listar todos los topics
docker exec kafka-lab-broker kafka-topics --list \
  --bootstrap-server localhost:9092

# Ver detalles de un topic
docker exec kafka-lab-broker kafka-topics --describe \
  --bootstrap-server localhost:9092 \
  --topic smart-city-sensors
```

**🎓 Nota para instructores**: Los estudiantes ya aprendieron a crear topics en el Lab 2. Aquí usamos auto-create para enfocarnos en MongoDB.

### Step 9: Run Health Check

```bash
# If you have the Lab 2 utils script
python ../2-ETL-kafka/src/utils.py --health-check
```

---

## ✅ Verification Checklist

After setup, verify everything works:

- [ ] All 5 Docker containers running (`docker-compose ps`)
- [ ] Kafka UI accessible at http://localhost:8080
- [ ] Mongo Express accessible at http://localhost:8081
- [ ] MongoDB contains 3 collections with sample data
- [ ] Python dependencies installed (`pip list`)
- [ ] Kafka topics exist (or auto-create is enabled)

---

## 🐛 Troubleshooting Common Issues

### Issue 1: "Port already in use"

**Symptoms**: Error starting services, port conflicts

**Solutions**:
```bash
# Find what's using the ports
lsof -i :9092    # Kafka
lsof -i :27017   # MongoDB
lsof -i :8080    # Kafka UI
lsof -i :8081    # Mongo Express

# Option A: Kill the process
kill -9 <PID>

# Option B: Change ports in docker-compose.yml
# Edit the "ports" section for conflicting services
```

### Issue 2: "Cannot connect to MongoDB"

**Symptoms**: `pymongo.errors.ServerSelectionTimeoutError`

**Solutions**:
```bash
# Check if MongoDB is running
docker ps | grep mongodb

# Check MongoDB logs
docker logs kafka-lab-mongodb

# Try restarting MongoDB
docker-compose restart mongodb

# Wait 10 seconds and test
docker exec kafka-lab-mongodb mongosh -u admin -p mongopass --eval "db.version()"
```

### Issue 3: "kafka-python can't connect"

**Symptoms**: `NoBrokersAvailable` or connection timeout

**Solutions**:
```bash
# Check Kafka is running
docker logs kafka-lab-broker | tail -20

# Verify Kafka is ready
docker exec kafka-lab-broker kafka-broker-api-versions --bootstrap-server localhost:9092

# If not ready, wait longer (Kafka can take 60+ seconds to start)
sleep 30

# Restart Kafka if needed
docker-compose restart kafka
```

### Issue 4: "Mongo Express won't load"

**Symptoms**: Can't access http://localhost:8081

**Solutions**:
```bash
# Check Mongo Express logs
docker logs kafka-lab-mongo-express

# Ensure MongoDB is ready first
docker exec kafka-lab-mongodb mongosh -u admin -p mongopass --eval "db.version()"

# Restart Mongo Express
docker-compose restart mongo-express

# Wait 15 seconds
sleep 15

# Try accessing again
curl http://localhost:8081
```

### Issue 5: "Services start but crash immediately"

**Symptoms**: `docker-compose ps` shows "Exit 1" or "Restarting"

**Solutions**:
```bash
# Check logs for the specific service
docker logs kafka-lab-<service-name>

# Common fixes:
# 1. Not enough memory
docker system df  # Check disk usage
docker system prune  # Clean up if needed

# 2. Corrupted volumes
docker-compose down -v  # ⚠️ This deletes all data!
docker-compose up -d

# 3. Permission issues (Linux)
sudo chown -R $USER:$USER .
```

### Issue 6: "Python import errors"

**Symptoms**: `ModuleNotFoundError: No module named 'kafka'`

**Solutions**:
```bash
# Ensure virtual environment is activated
which python  # Should show path to venv/bin/python

# Reinstall dependencies
pip install --upgrade pip
pip install -r requirements.txt --force-reinstall

# Verify installation
python -c "import kafka; import pymongo; print('✅ All modules loaded')"
```

### Issue 7: "MongoDB authentication failed"

**Symptoms**: `Authentication failed` when connecting

**Solutions**:
```bash
# Reset MongoDB with correct credentials
docker-compose down
docker volume rm kafka-lab-mongodb-data
docker-compose up -d mongodb

# Wait for initialization
sleep 30

# Test connection
docker exec -it kafka-lab-mongodb mongosh -u admin -p mongopass
```

---

## 🔄 Restart Procedures

### Soft Restart (Keep Data)
```bash
docker-compose restart
```

### Full Restart (Keep Data)
```bash
docker-compose down
docker-compose up -d
```

### Clean Restart (⚠️ Deletes All Data)
```bash
docker-compose down -v
docker-compose up -d

# Wait for services to initialize
sleep 30
```

---

## 🧹 Cleanup After Lab

### Stop Services (Keep Data)
```bash
docker-compose stop
```

### Remove Everything
```bash
# Stop and remove containers
docker-compose down

# Also remove volumes (all data)
docker-compose down -v

# Remove Python virtual environment (optional)
rm -rf venv
```

---

## 📊 Resource Monitoring

### Check Docker Resource Usage
```bash
# Overall Docker stats
docker stats

# Specific to this lab
docker stats kafka-lab-broker kafka-lab-mongodb
```

### Check Disk Usage
```bash
# Docker disk usage
docker system df

# Volume sizes
docker volume ls | grep kafka-lab
```

---

## 🎯 Quick Reference

### Essential Commands

```bash
# Start all services
docker-compose up -d

# Stop all services
docker-compose stop

# View logs (all services)
docker-compose logs -f

# View logs (specific service)
docker-compose logs -f mongodb

# Restart a service
docker-compose restart kafka

# Check service status
docker-compose ps

# Access MongoDB shell
docker exec -it kafka-lab-mongodb mongosh -u admin -p mongopass

# Access Kafka shell
docker exec -it kafka-lab-broker bash
```

### Port Reference

| Port  | Service        | Access                              |
|-------|----------------|-------------------------------------|
| 2181  | Zookeeper      | Internal coordination               |
| 9092  | Kafka          | `localhost:9092`                    |
| 8080  | Kafka UI       | http://localhost:8080               |
| 27017 | MongoDB        | `mongodb://admin:mongopass@localhost:27017` |
| 8081  | Mongo Express  | http://localhost:8081 (admin/mongopass) |

---

## 🆘 Getting Help

If issues persist:

1. **Check Docker health**: `docker system info`
2. **Review logs**: `docker-compose logs` for all services
3. **Restart Docker Desktop** completely
4. **Verify prerequisites**: Python version, Docker version
5. **Ask instructor** during office hours with:
   - Error messages (exact text)
   - Output of `docker-compose ps`
   - Output of `docker-compose logs <service>`

---

**Setup complete! 🎉 Now proceed to STUDENT-EXERCISES.md**
