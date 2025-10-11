# 📚 Documentación Completa: Base de Datos y Configuración

## 🗄️ 1. Estructura de la Base de Datos MongoDB

### Nombre de la Base de Datos:
```
casm83
```

### Colecciones (Tablas):

#### **Collection: `test_sessions`**

Esta es la única colección principal que almacena todas las sesiones de prueba.

**Estructura del documento:**

```javascript
{
  "_id": ObjectId("68e60414dc8618bbb6e2c76c"),  // ID interno de MongoDB
  "id": "894a7645-aeb8-4314-b0f9-671413a07ed9", // UUID único para la sesión
  "sex": "masculino",  // o "femenino"
  "responses": [
    {
      "question_number": 1,
      "response": ["A"]  // puede ser ["A"], ["B"], ["A", "B"], o []
    },
    {
      "question_number": 2,
      "response": ["B"]
    },
    {
      "question_number": 3,
      "response": ["A", "B"]  // ambas opciones marcadas
    },
    {
      "question_number": 4,
      "response": []  // ninguna opción marcada
    }
    // ... hasta 143 preguntas
  ],
  "created_at": "2025-10-08T06:26:28.461039+00:00",
  "completed": true,
  "completed_at": "2025-10-08T06:26:28.754558+00:00"
}
```

### 📊 Diagrama de Base de Datos

```
┌─────────────────────────────────────────────────────────────┐
│                    Database: casm83                         │
└─────────────────────────────────────────────────────────────┘
                              │
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│            Collection: test_sessions                        │
├─────────────────────────────────────────────────────────────┤
│ Campos:                                                     │
│                                                             │
│  • _id (ObjectId)          - ID interno de MongoDB         │
│  • id (String/UUID)        - ID único de la sesión         │
│  • sex (String)            - "masculino" o "femenino"      │
│  • responses (Array)       - Array de respuestas           │
│      └─ question_number (Number) - Número de pregunta      │
│      └─ response (Array)   - ["A"], ["B"], ["A","B"], []   │
│  • created_at (String)     - Fecha de creación (ISO)       │
│  • completed (Boolean)     - Estado de completado          │
│  • completed_at (String)   - Fecha de finalización (ISO)   │
│                                                             │
├─────────────────────────────────────────────────────────────┤
│ Índices:                                                    │
│  • _id (unique)                                             │
│  • id (usado para búsquedas)                               │
└─────────────────────────────────────────────────────────────┘
```

### 🔗 Relaciones de Datos

```
┌─────────────────┐
│  test_sessions  │
└────────┬────────┘
         │
         │ 1 session tiene
         │ múltiples responses
         ▼
    ┌─────────────────┐
    │   responses[]   │
    │  (embedded)     │
    └─────────────────┘
```

**Nota:** MongoDB es una base de datos NoSQL, por lo que no usa tablas relacionales tradicionales. Los `responses` están **embebidos** dentro de cada documento de sesión.

---

## 🔌 2. Conexión a MongoDB Local

### Paso 1: Verificar que MongoDB esté instalado

Abre tu terminal y ejecuta:

```bash
mongod --version
```

Si ves la versión, MongoDB está instalado correctamente.

### Paso 2: Iniciar MongoDB

**En Windows:**
```bash
# Iniciar servicio
net start MongoDB

# O ejecutar directamente
mongod
```

**En macOS/Linux:**
```bash
# Iniciar servicio
sudo systemctl start mongod

# O con brew (macOS)
brew services start mongodb-community
```

### Paso 3: Configurar la conexión en el proyecto

Edita el archivo `/app/backend/.env`:

```env
# Conexión local (puerto por defecto 27017)
MONGO_URL=mongodb://localhost:27017
```

**Si MongoDB requiere autenticación:**
```env
MONGO_URL=mongodb://usuario:contraseña@localhost:27017
```

### Paso 4: Verificar la conexión

Puedes verificar que MongoDB está corriendo:

```bash
# Conectar a MongoDB shell
mongosh

# Ver bases de datos
show dbs

# Usar la base de datos casm83
use casm83

# Ver colecciones
show collections

# Ver documentos en test_sessions
db.test_sessions.find().pretty()
```

---

## 🚀 3. Cómo Correr la Aplicación desde GitHub

### Requisitos Previos:

- **Node.js** (v16 o superior) - [Descargar](https://nodejs.org/)
- **Python** (v3.8 o superior) - [Descargar](https://www.python.org/)
- **MongoDB** (v5.0 o superior) - [Descargar](https://www.mongodb.com/try/download/community)
- **Git** - [Descargar](https://git-scm.com/)

---

### 📥 Instalación Paso a Paso:

#### **1. Clonar el repositorio**

```bash
git clone https://github.com/tu-usuario/casm83-app.git
cd casm83-app
```

#### **2. Configurar el Backend**

```bash
# Ir a la carpeta backend
cd backend

# Crear entorno virtual de Python
python -m venv venv

# Activar entorno virtual
# En Windows:
venv\Scripts\activate
# En macOS/Linux:
source venv/bin/activate

# Instalar dependencias
pip install -r requirements.txt

# Crear archivo .env
# Crear un archivo llamado .env con el siguiente contenido:
```

**Contenido de `backend/.env`:**
```env
MONGO_URL=mongodb://localhost:27017
```

#### **3. Configurar el Frontend**

```bash
# Volver a la raíz del proyecto
cd ..

# Ir a la carpeta frontend
cd frontend

# Instalar dependencias con Yarn
yarn install

# O si usas npm:
npm install

# Crear archivo .env
# Crear un archivo llamado .env con el siguiente contenido:
```

**Contenido de `frontend/.env`:**
```env
REACT_APP_BACKEND_URL=http://localhost:8001
```

#### **4. Iniciar MongoDB**

Asegúrate de que MongoDB esté corriendo:

```bash
# Windows
net start MongoDB

# macOS/Linux
sudo systemctl start mongod
```

#### **5. Iniciar el Backend**

En una terminal (dentro de la carpeta `backend`):

```bash
# Activar entorno virtual si no está activo
# Windows: venv\Scripts\activate
# macOS/Linux: source venv/bin/activate

# Iniciar servidor FastAPI
uvicorn server:app --host 0.0.0.0 --port 8001 --reload
```

Deberías ver:
```
INFO:     Uvicorn running on http://0.0.0.0:8001 (Press CTRL+C to quit)
INFO:     Started reloader process
```

#### **6. Iniciar el Frontend**

En otra terminal (dentro de la carpeta `frontend`):

```bash
# Iniciar aplicación React
yarn start

# O con npm:
npm start
```

Deberías ver:
```
Compiled successfully!

You can now view the app in the browser.

  Local:            http://localhost:3000
```

---

## 🌐 7. Acceder a la Aplicación

Abre tu navegador y ve a:

```
http://localhost:3000
```

¡La aplicación CASM-83 R2014 debería estar funcionando! 🎉

---

## 📁 8. Estructura de Carpetas del Proyecto

```
casm83-app/
├── backend/
│   ├── server.py              # Servidor FastAPI
│   ├── requirements.txt       # Dependencias Python
│   ├── .env                   # Variables de entorno (crear)
│   └── venv/                  # Entorno virtual Python
│
├── frontend/
│   ├── public/
│   │   └── index.html
│   ├── src/
│   │   ├── App.js             # Componente principal
│   │   ├── App.css            # Estilos
│   │   └── index.js           # Punto de entrada
│   ├── package.json           # Dependencias Node.js
│   ├── .env                   # Variables de entorno (crear)
│   └── node_modules/          # Dependencias instaladas
│
└── README.md                  # Documentación
```

---

## 🔧 9. Comandos Útiles de MongoDB

### Ver datos en la base de datos:

```bash
# Conectar a MongoDB
mongosh

# Usar la base de datos
use casm83

# Ver todas las sesiones
db.test_sessions.find().pretty()

# Contar sesiones
db.test_sessions.countDocuments()

# Ver solo sesiones completadas
db.test_sessions.find({completed: true}).pretty()

# Ver una sesión específica por ID
db.test_sessions.findOne({id: "tu-session-id-aqui"})

# Eliminar todas las sesiones (CUIDADO)
db.test_sessions.deleteMany({})

# Exportar datos a JSON
mongoexport --db=casm83 --collection=test_sessions --out=backup.json
```

---

## 🐛 10. Solución de Problemas Comunes

### ❌ "Cannot connect to MongoDB"

**Solución:**
```bash
# Verificar que MongoDB esté corriendo
mongosh

# Si no está corriendo, iniciarlo:
# Windows: net start MongoDB
# macOS/Linux: sudo systemctl start mongod
```

### ❌ "Port 8001 already in use"

**Solución:**
```bash
# Encontrar proceso usando el puerto
# Windows:
netstat -ano | findstr :8001
taskkill /PID <PID> /F

# macOS/Linux:
lsof -i :8001
kill -9 <PID>
```

### ❌ "Module not found" en Backend

**Solución:**
```bash
cd backend
pip install -r requirements.txt
```

### ❌ "Module not found" en Frontend

**Solución:**
```bash
cd frontend
yarn install
# o
npm install
```

---

## 📊 11. Exportar Datos para Machine Learning

Para exportar los datos recopilados para entrenar modelos ML:

### Opción 1: Usar el endpoint de la API

```bash
# Obtener todos los datos en formato JSON
curl http://localhost:8001/api/all-sessions > data.json
```

### Opción 2: Usar mongoexport (CSV)

```bash
mongoexport --db=casm83 --collection=test_sessions --type=csv --fields=id,sex,completed --out=sessions.csv
```

### Opción 3: Desde MongoDB Compass (GUI)

1. Descarga [MongoDB Compass](https://www.mongodb.com/products/compass)
2. Conecta a `mongodb://localhost:27017`
3. Selecciona la base de datos `casm83`
4. Selecciona la colección `test_sessions`
5. Exporta como JSON, CSV o BSON

---
