#!/usr/bin/env python3
"""
Script para insertar datos de prueba en la base de datos MongoDB
"""

from pymongo import MongoClient
import uuid
from datetime import datetime, timezone

# Conexión a MongoDB
MONGO_URL = "mongodb://localhost:27017"
client = MongoClient(MONGO_URL)
db = client.casm83

def create_sample_session(sex, num_responses=143):
    """Crear una sesión de prueba con respuestas aleatorias"""
    import random
    
    session_id = str(uuid.uuid4())
    
    # Generar respuestas aleatorias
    responses = []
    for i in range(1, num_responses + 1):
        # Elegir aleatoriamente: A, B, ambas, o ninguna
        choice = random.choice([
            ["A"],
            ["B"],
            ["A", "B"],
            []
        ])
        responses.append({
            "question_number": i,
            "response": choice
        })
    
    # Crear documento de sesión
    session = {
        "id": session_id,
        "sex": sex,
        "responses": responses,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "completed": True,
        "completed_at": datetime.now(timezone.utc).isoformat()
    }
    
    return session

def seed_database():
    """Insertar datos de prueba en la base de datos"""
    
    print("🌱 Insertando datos de prueba en MongoDB...")
    print(f"📊 Base de datos: casm83")
    print(f"📁 Colección: test_sessions")
    print()
    
    # Limpiar datos existentes (opcional)
    response = input("¿Deseas eliminar datos existentes? (s/n): ")
    if response.lower() == 's':
        db.test_sessions.delete_many({})
        print("🗑️  Datos existentes eliminados")
    
    # Crear sesiones de prueba
    sessions = []
    
    # 3 sesiones masculinas
    for i in range(3):
        session = create_sample_session("masculino")
        sessions.append(session)
        print(f"✅ Sesión {i+1}/6 creada (Masculino)")
    
    # 3 sesiones femeninas
    for i in range(3):
        session = create_sample_session("femenino")
        sessions.append(session)
        print(f"✅ Sesión {i+4}/6 creada (Femenino)")
    
    # Insertar en MongoDB
    result = db.test_sessions.insert_many(sessions)
    
    print()
    print(f"✅ {len(result.inserted_ids)} sesiones insertadas exitosamente")
    print()
    
    # Mostrar estadísticas
    total = db.test_sessions.count_documents({})
    masculino = db.test_sessions.count_documents({"sex": "masculino"})
    femenino = db.test_sessions.count_documents({"sex": "femenino"})
    completados = db.test_sessions.count_documents({"completed": True})
    
    print("📊 Estadísticas de la Base de Datos:")
    print(f"   Total de sesiones: {total}")
    print(f"   Masculino: {masculino}")
    print(f"   Femenino: {femenino}")
    print(f"   Completados: {completados}")
    print()
    print("🎉 ¡Datos de prueba insertados exitosamente!")
    print()
    print("🔍 Para ver los datos, ejecuta:")
    print("   mongosh")
    print("   use casm83")
    print("   db.test_sessions.find().pretty()")

if __name__ == "__main__":
    try:
        seed_database()
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        print()
        print("Asegúrate de que:")
        print("1. MongoDB esté corriendo (mongod)")
        print("2. pymongo esté instalado (pip install pymongo)")
