# 🧭 Guía de MongoDB Compass

## ¿Qué es MongoDB Compass?

MongoDB Compass es la interfaz gráfica oficial de MongoDB que te permite visualizar y manipular datos de forma visual.

## 📥 Instalación

1. Descarga desde: https://www.mongodb.com/try/download/compass
2. Instala el programa
3. Abre MongoDB Compass

## 🔌 Conexión

### Conectar a tu Base de Datos Local:

1. Abre MongoDB Compass
2. En "New Connection", ingresa:
   ```
   mongodb://localhost:27017
   ```
3. Haz clic en "Connect"

### Explorar la Base de Datos:

```
Conexiones
└── localhost:27017
    └── casm83 (tu base de datos)
        └── test_sessions (tu colección)
```

## 🔍 Operaciones Comunes

### Ver Todos los Documentos:

1. Selecciona la colección `test_sessions`
2. Verás todos los documentos en formato visual

### Filtrar Documentos:

En el campo "Filter", ingresa:

```json
// Ver solo sesiones masculinas
{"sex": "masculino"}

// Ver solo sesiones completadas
{"completed": true}

// Ver sesiones femeninas completadas
{"sex": "femenino", "completed": true}
```

### Buscar por ID:

```json
{"id": "tu-session-id-aqui"}
```

### Ordenar Resultados:

```json
// Ordenar por fecha de creación (más reciente primero)
Sort: {"created_at": -1}
```

### Exportar Datos:

1. Selecciona la colección
2. Haz clic en "Export Data"
3. Elige formato: JSON, CSV
4. Guarda el archivo

### Importar Datos:

1. Selecciona la colección
2. Haz clic en "Add Data" > "Import File"
3. Selecciona tu archivo JSON o CSV
4. Configura las opciones
5. Haz clic en "Import"

## 📊 Visualizar Estadísticas:

1. Selecciona la colección `test_sessions`
2. Ve a la pestaña "Schema"
3. Verás estadísticas sobre:
   - Tipos de datos
   - Valores más comunes
   - Distribución de datos

## 🔧 Consultas Avanzadas

### Aggregations (Pipeline):

```javascript
[
  // Contar sesiones por sexo
  {
    $group: {
      _id: "$sex",
      count: { $sum: 1 }
    }
  }
]
```

```javascript
[
  // Obtener promedio de respuestas por sesión
  {
    $project: {
      sex: 1,
      numResponses: { $size: "$responses" }
    }
  },
  {
    $group: {
      _id: "$sex",
      avgResponses: { $avg: "$numResponses" }
    }
  }
]
```

## ⚡ Atajos de Teclado

- `Ctrl + K`: Abrir paleta de comandos
- `Ctrl + Shift + P`: Abrir conexiones
- `Ctrl + F`: Buscar en documentos
- `Ctrl + E`: Exportar colección

## 🎨 Ventajas de MongoDB Compass

✅ Interfaz visual intuitiva
✅ No necesitas memorizar comandos
✅ Validación de esquema visual
✅ Generación automática de consultas
✅ Importación/exportación fácil
✅ Análisis de rendimiento

## 💡 Consejos

1. **Indexación**: Compass te ayuda a crear índices para mejorar el rendimiento
2. **Backup**: Exporta regularmente tus datos
3. **Validación**: Usa la pestaña "Validation" para definir reglas de esquema
4. **Agregación**: Usa el builder visual para crear pipelines complejos sin código
