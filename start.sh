#!/bin/sh
set -eu

echo "--- START.SH RUNNING ---"
echo "Shell: $(ps -p $$ -o comm= 2>/dev/null || echo unknown)"
echo "Pwd: $(pwd)"

# Ir a la carpeta del frontend
cd "$(dirname "$0")/frontend"
echo "Now in: $(pwd)"
echo "Node: $(node -v)  NPM: $(npm -v)"

# Instala deps (incluye dev por CRACO)
npm ci --include=dev

# Compila
npm run build

# Verifica que exista el build
echo "Build content:"
ls -la build || true

# Arranca Express (frontend/server.js)
exec node server.js
