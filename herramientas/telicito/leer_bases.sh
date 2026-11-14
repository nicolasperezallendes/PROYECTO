#!/usr/bin/env bash
# Lee bases de licitación con el motor de Telicito.cl (repositorio privado franciscomerysoler-ux/licitia).
#
#   bash herramientas/telicito/leer_bases.sh bases.pdf [anexos.zip ...] [--md salida.md] [--json salida.json]
#
# Busca el repositorio licitia en TELICITO_DIR o, si no está definida, junto a este repositorio (../licitia).
# Si falta, hay que agregarlo a la sesión y clonarlo; si no tiene dependencias, las instala.
set -euo pipefail

AQUI="$(cd "$(dirname "$0")" && pwd)"
RAIZ="$(cd "$AQUI/../.." && pwd)"
TELICITO="${TELICITO_DIR:-$(dirname "$RAIZ")/licitia}"

if [ ! -f "$TELICITO/src/lib/analysis/heuristic.ts" ]; then
  echo "No encuentro el repositorio licitia en $TELICITO." >&2
  echo "Agrégalo a la sesión (franciscomerysoler-ux/licitia, rama vigente) o define TELICITO_DIR." >&2
  exit 1
fi
if [ ! -d "$TELICITO/node_modules" ]; then
  echo "Instalando dependencias de licitia (solo la primera vez)..." >&2
  (cd "$TELICITO" && corepack enable >/dev/null 2>&1 || true; cd "$TELICITO" && pnpm install --frozen-lockfile --reporter=silent)
fi

# Las rutas de los archivos se resuelven desde donde se llamó al script, no desde licitia.
export LEER_BASES_CWD="$PWD"
cd "$TELICITO"
ENVFILE=()
[ -f .env ] && ENVFILE=(--env-file=.env)
exec pnpm -s exec tsx "${ENVFILE[@]}" --tsconfig tsconfig.json "$AQUI/leer_bases.ts" "$@"
