#!/usr/bin/env bash

set -euo pipefail

#ir al directorio del frontend
cd "$(dirname "$0")"/frontend

# INFO útil en logs
echo "Node: $(node -v)"
echo "NPM:  $(npm -v)"

#instalar dependencias (incluyendo dev)
npm ci --include=dev

#compilar la aplicacion
npm run build

# Escucha explícitamente en 0.0.0.0 y puerto fijo
PORT_TO_USE="${PORT:-3000}"
echo "Serving on 0.0.0.0:${PORT_TO_USE}"

# Usa formato host:puerto (más compatible que 'tcp://...')
exec npx serve -s build -l "0.0.0.0:${PORT_TO_USE}"



#Se comenta para evitar errores en despliegue

#if [ -f "yarn.lock" ]; then
#    corepack enable || true
#    yarn install --frozen-lockfile
#else
#    npm ci
#fi

#npm run build || yarn build
#npx serve -s build -l $PORT