#!/usr/bin/env bash
# Démarrage en une commande (Mac / Linux) :  ./demarrer.sh
# - crée un environnement Python isolé (.venv) la première fois
# - installe les dépendances
# - charge les données de démonstration si la base est vide
# - lance le serveur et ouvre le navigateur
set -euo pipefail
cd "$(dirname "$0")/backend"

if ! command -v python3 >/dev/null 2>&1; then
  echo "Python 3 est introuvable. Sur Mac : installez-le avec  brew install python  ou depuis https://www.python.org/downloads/"
  exit 1
fi
PYV=$(python3 -c 'import sys; print(sys.version_info >= (3, 11))')
if [ "$PYV" != "True" ]; then
  echo "Python 3.11 ou plus est requis (version actuelle : $(python3 --version)). Sur Mac :  brew install python"
  exit 1
fi

if [ ! -d .venv ]; then
  echo "▶ Création de l'environnement Python (.venv)…"
  python3 -m venv .venv
fi
# shellcheck disable=SC1091
source .venv/bin/activate
pip install -q --upgrade pip
pip install -q -e ".[dev]"

if [ ! -f ../.env ]; then
  cp ../.env.example ../.env
  echo "▶ Fichier .env créé à partir de .env.example (mode démonstration, aucun envoi réel)."
fi
export $(grep -v '^#' ../.env | grep -v '^\s*$' | xargs) 2>/dev/null || true

if [ ! -f data/bureau.db ]; then
  echo "▶ Chargement des données de démonstration…"
  python -m app.seed
fi

echo
echo "✅ Bureau du Pasteur démarre sur http://localhost:8000"
echo "   Identifiants : ${ADMIN_EMAIL:-pasteur@exemple.org} / ${ADMIN_PASSWORD:-changez-moi}"
echo "   Arrêt : Ctrl + C"
echo
( sleep 2 && (command -v open >/dev/null && open http://localhost:8000 || true) ) &
exec uvicorn app.main:app --host 127.0.0.1 --port 8000
