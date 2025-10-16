#!/usr/bin/env bash

set -euo pipefail

cd "$(dirname "$0")"/frontend

if [ -f "yarn.lock"]; then
    corepack enable || true
    yarn install --frozen-lockfile
else
    npm ci
fi

npm run build || yarn build
npx serve -s build -l $PORT