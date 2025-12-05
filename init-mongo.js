// ========================================================================================
// 🗄️ MONGODB INITIALIZATION SCRIPT
// ========================================================================================
// 
// 📖 ¿QUÉ ES ESTE ARCHIVO?
// Este es un script de inicialización automática para MongoDB. Docker lo ejecuta
// AUTOMÁTICAMENTE cuando MongoDB arranca por primera vez.
//
// 🤔 ¿POR QUÉ ESTÁ EN JAVASCRIPT Y NO EN PYTHON?
// - MongoDB Shell (mongosh) ejecuta JavaScript nativamente
// - Docker busca archivos *.js en /docker-entrypoint-initdb.d/ y los ejecuta automáticamente
// - Es el método ESTÁNDAR en la industria para inicializar MongoDB con Docker
// - Se ejecuta ANTES de que la app Python esté disponible
//
// ✅ VENTAJAS DE ESTE APPROACH:
// 1. Automático - No requiere pasos manuales
// 2. Idempotente - Se ejecuta solo UNA VEZ (primera vez)
// 3. Consistente - Todos tienen la misma configuración inicial
// 4. Profesional - Es el método usado en producción
//
// 🎯 LO QUE HACE ESTE SCRIPT:
// 1. Crea la base de datos: kafka_events_db
// 2. Crea 3 colecciones con schema validation:
//    - sensors (datos de sensores IoT)
//    - ecommerce (eventos de e-commerce)
//    - mobile_events (analytics móviles)
// 3. Crea índices para optimizar queries
// 4. Inserta datos de ejemplo para testing inmediato
// 5. Crea usuario de aplicación con permisos limitados
//
// 📚 PARA ESTUDIANTES:
// - NO necesitas modificar este archivo
// - Léelo para entender la estructura de datos
// - Los scripts Python (src/consumers/) escribirán a estas colecciones
// - Los scripts de queries (src/queries/) leerán de aquí
//
// 🔄 SI QUIERES RESETEAR TODO:
// docker-compose down -v && docker-compose up -d
// (esto borrará todos los datos y re-ejecutará este script)
//
// ========================================================================================

// Cambiar a la base de datos del laboratorio
// getSiblingDB() es equivalente a "USE kafka_events_db" en SQL
db = db.getSiblingDB('kafka_events_db');

print('🚀 Iniciando configuración de MongoDB para Kafka Events Lab...');
print('📝 Este script se ejecuta automáticamente al iniciar MongoDB por primera vez');

// ==================================================================================
// 📊 COLECCIÓN 1: SENSORS (Smart City IoT Data)
// ==================================================================================
// PROPÓSITO: Almacenar eventos de sensores urbanos en tiempo real
// SCHEMA: Flexible - cada documento puede tener campos diferentes según sensor_type

db.createCollection('sensors', {
    validator: {
        $jsonSchema: {
            bsonType: "object",
            required: ["sensor_id", "sensor_type", "city", "timestamp"],
            properties: {
                sensor_id: {
                    bsonType: "string",
                    description: "ID único del sensor (ej: SENSOR-MX-TEMP-001)"
                },
                sensor_type: {
                    bsonType: "string",
                    enum: ["temperature", "humidity", "air_quality", "noise_level", "traffic_density", "parking_occupancy", "energy_consumption"],
                    description: "Tipo de sensor instalado"
                },
                city: {
                    bsonType: "string",
                    description: "Ciudad donde está el sensor"
                },
                value: {
                    bsonType: ["double", "int"],
                    description: "Lectura del sensor"
                },
                timestamp: {
                    bsonType: "string",
                    description: "Timestamp ISO 8601 del evento"
                },
                location: {
                    bsonType: "object",
                    description: "Coordenadas geográficas (opcional para geospatial queries)"
                }
            }
        }
    }
});

print('✅ Colección "sensors" creada con schema validation');

// Índices para optimización de queries
db.sensors.createIndex({ "timestamp": -1 }, { name: "idx_timestamp_desc" });
db.sensors.createIndex({ "city": 1, "sensor_type": 1 }, { name: "idx_city_sensor_type" });
db.sensors.createIndex({ "sensor_id": 1 }, { name: "idx_sensor_id" });
// Índice geoespacial para queries de proximidad (ej: "sensores cerca de lat/lng")
db.sensors.createIndex({ "location": "2dsphere" }, { name: "idx_geospatial" });

print('✅ Índices creados para colección sensors');

// ==================================================================================
// 🛒 COLECCIÓN 2: ECOMMERCE (User Events & Transactions)
// ==================================================================================
// PROPÓSITO: Event sourcing para e-commerce - cada interacción del usuario
// USO: Análisis de funnels, segmentación, recomendaciones

db.createCollection('ecommerce', {
    validator: {
        $jsonSchema: {
            bsonType: "object",
            required: ["event_id", "user_id", "event_type", "timestamp"],
            properties: {
                event_id: {
                    bsonType: "string",
                    description: "ID único del evento"
                },
                user_id: {
                    bsonType: "string",
                    description: "ID del usuario que generó el evento"
                },
                event_type: {
                    bsonType: "string",
                    enum: ["page_view", "product_view", "add_to_cart", "remove_from_cart", "purchase", "search", "login", "logout"],
                    description: "Tipo de evento de e-commerce"
                },
                timestamp: {
                    bsonType: "string",
                    description: "Timestamp ISO 8601"
                },
                product_name: {
                    bsonType: "string",
                    description: "Nombre del producto (opcional según event_type)"
                },
                amount: {
                    bsonType: ["double", "int"],
                    description: "Monto de la transacción si event_type=purchase"
                }
            }
        }
    }
});

print('✅ Colección "ecommerce" creada con schema validation');

// Índices para queries de e-commerce
db.ecommerce.createIndex({ "user_id": 1, "timestamp": -1 }, { name: "idx_user_timeline" });
db.ecommerce.createIndex({ "event_type": 1 }, { name: "idx_event_type" });
db.ecommerce.createIndex({ "timestamp": -1 }, { name: "idx_timestamp_desc" });
db.ecommerce.createIndex({ "product_name": 1 }, { name: "idx_product_name" });

print('✅ Índices creados para colección ecommerce');

// ==================================================================================
// 📱 COLECCIÓN 3: MOBILE_EVENTS (App Analytics)
// ==================================================================================
// PROPÓSITO: Telemetría de aplicaciones móviles - crashes, performance, user actions
// USO: Debugging, optimización, análisis de UX

db.createCollection('mobile_events', {
    validator: {
        $jsonSchema: {
            bsonType: "object",
            required: ["event_id", "user_id", "event_type", "timestamp"],
            properties: {
                event_id: {
                    bsonType: "string",
                    description: "ID único del evento"
                },
                user_id: {
                    bsonType: "string",
                    description: "ID del usuario"
                },
                event_type: {
                    bsonType: "string",
                    enum: ["session_start", "session_end", "screen_view", "user_action", "crash", "performance"],
                    description: "Tipo de evento mobile"
                },
                timestamp: {
                    bsonType: "string",
                    description: "Timestamp ISO 8601"
                },
                platform: {
                    bsonType: "string",
                    description: "iOS o Android"
                },
                app_version: {
                    bsonType: "string",
                    description: "Versión de la app"
                }
            }
        }
    }
});

print('✅ Colección "mobile_events" creada con schema validation');

// Índices para mobile analytics
db.mobile_events.createIndex({ "user_id": 1, "timestamp": -1 }, { name: "idx_user_timeline" });
db.mobile_events.createIndex({ "event_type": 1 }, { name: "idx_event_type" });
db.mobile_events.createIndex({ "timestamp": -1 }, { name: "idx_timestamp_desc" });
db.mobile_events.createIndex({ "platform": 1, "app_version": 1 }, { name: "idx_platform_version" });

print('✅ Índices creados para colección mobile_events');

// ==================================================================================
// 👤 CREAR USUARIO DE APLICACIÓN
// ==================================================================================
// CONCEPTO: Principio de mínimo privilegio - la app NO debe usar admin
// PERMISOS: Solo lectura/escritura en kafka_events_db

db.createUser({
    user: "kafka_app_user",
    pwd: "kafka_app_pass",
    roles: [
        {
            role: "readWrite",
            db: "kafka_events_db"
        }
    ]
});

print('✅ Usuario "kafka_app_user" creado con permisos readWrite');

// ==================================================================================
// 📝 INSERTAR DATOS DE EJEMPLO
// ==================================================================================
// PROPÓSITO: Datos iniciales para que los estudiantes puedan probar queries
// inmediatamente sin esperar a que lleguen eventos de Kafka

// Ejemplo: Sensores
db.sensors.insertMany([
    {
        sensor_id: "SENSOR-CDMX-TEMP-001",
        sensor_type: "temperature",
        city: "Ciudad de México",
        value: 22.5,
        timestamp: new Date().toISOString(),
        location: { type: "Point", coordinates: [-99.1332, 19.4326] }
    },
    {
        sensor_id: "SENSOR-GDL-AQ-001",
        sensor_type: "air_quality",
        city: "Guadalajara",
        value: 85,
        timestamp: new Date().toISOString(),
        location: { type: "Point", coordinates: [-103.3496, 20.6597] }
    },
    {
        sensor_id: "SENSOR-MTY-TRAFFIC-001",
        sensor_type: "traffic_density",
        city: "Monterrey",
        value: 67,
        timestamp: new Date().toISOString(),
        location: { type: "Point", coordinates: [-100.3161, 25.6866] }
    }
]);

print('✅ Insertados 3 documentos de ejemplo en sensors');

// Ejemplo: E-commerce
db.ecommerce.insertMany([
    {
        event_id: "EVT-" + Date.now() + "-1",
        user_id: "USER-001",
        event_type: "product_view",
        product_name: "Laptop Dell XPS 15",
        timestamp: new Date().toISOString(),
        device_type: "Desktop",
        city: "Ciudad de México"
    },
    {
        event_id: "EVT-" + Date.now() + "-2",
        user_id: "USER-001",
        event_type: "add_to_cart",
        product_name: "Laptop Dell XPS 15",
        timestamp: new Date().toISOString(),
        device_type: "Desktop",
        city: "Ciudad de México"
    },
    {
        event_id: "EVT-" + Date.now() + "-3",
        user_id: "USER-001",
        event_type: "purchase",
        product_name: "Laptop Dell XPS 15",
        amount: 25000,
        timestamp: new Date().toISOString(),
        device_type: "Desktop",
        city: "Ciudad de México"
    }
]);

print('✅ Insertados 3 documentos de ejemplo en ecommerce');

// Ejemplo: Mobile
db.mobile_events.insertMany([
    {
        event_id: "MOBILE-" + Date.now() + "-1",
        user_id: "MUSER-001",
        event_type: "session_start",
        platform: "iOS",
        app_version: "2.5.0",
        timestamp: new Date().toISOString(),
        device_model: "iPhone 14 Pro"
    },
    {
        event_id: "MOBILE-" + Date.now() + "-2",
        user_id: "MUSER-001",
        event_type: "screen_view",
        platform: "iOS",
        app_version: "2.5.0",
        screen_name: "Home",
        timestamp: new Date().toISOString(),
        device_model: "iPhone 14 Pro"
    }
]);

print('✅ Insertados 2 documentos de ejemplo en mobile_events');

// ==================================================================================
// 📊 MOSTRAR ESTADÍSTICAS FINALES
// ==================================================================================

print('\n📊 Resumen de configuración:');
print('   - Base de datos: kafka_events_db');
print('   - Colecciones creadas: ' + db.getCollectionNames().length);
print('   - Documentos en sensors: ' + db.sensors.countDocuments());
print('   - Documentos en ecommerce: ' + db.ecommerce.countDocuments());
print('   - Documentos en mobile_events: ' + db.mobile_events.countDocuments());
print('\n✅ MongoDB inicializado correctamente para el laboratorio!\n');

// ==================================================================================
// 🎓 NOTAS PARA ESTUDIANTES
// ==================================================================================
// 
// QUERIES DE EJEMPLO PARA PROBAR:
//
// 1. Listar todas las colecciones:
//    > show collections
//
// 2. Ver documentos de sensores:
//    > db.sensors.find().pretty()
//
// 3. Contar eventos por tipo:
//    > db.ecommerce.aggregate([
//        { $group: { _id: "$event_type", count: { $sum: 1 } } }
//      ])
//
// 4. Buscar sensores de una ciudad:
//    > db.sensors.find({ city: "Ciudad de México" })
//
// 5. Ver índices de una colección:
//    > db.sensors.getIndexes()
//
// 6. Query geoespacial (sensores cerca de un punto):
//    > db.sensors.find({
//        location: {
//          $near: {
//            $geometry: { type: "Point", coordinates: [-99.1332, 19.4326] },
//            $maxDistance: 10000  // 10km en metros
//          }
//        }
//      })
//
// ==================================================================================
