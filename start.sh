#!/usr/bin/env bash

set -euo pipefail

#ir al directorio del frontend
cd "$(dirname "$0")/frontend"


# Info útil en logs
echo "Node: $(node -v)"
echo "NPM:  $(npm -v)"

# Instala dependencias (incluye dev por CRACO)
npm ci --include=dev

# Compila
npm run build

ls -la build || true
# Arranca el servidor Express escuchando en 0.0.0.0:PORT
exec node server.js