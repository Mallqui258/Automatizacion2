#!/usr/bin/env bash

set -euo pipefail

#ir al directorio del frontend
cd "$(dirname "$0")/frontend"

# INFO útil en logs
#echo "Node: $(node -v)"
#echo "NPM:  $(npm -v)"

#instalar dependencias (incluyendo dev)
#npm ci --include=dev

#compilar la aplicacion
#npm run build

# Servir en 0.0.0.0:<PORT o 3000> (necesario para que el dominio público conecte)
#exec npx serve -s build -l "tcp://0.0.0.0:${PORT:-3000}"



#Se comenta para evitar errores en despliegue

if [ -f "yarn.lock" ]; then
    corepack enable || true
    yarn install --frozen-lockfile
else
    npm ci
fi

npm run build || yarn build
npx serve -s build -l $PORT