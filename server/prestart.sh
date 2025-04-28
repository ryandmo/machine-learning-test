#! /usr/bin/env sh

echo "Running inside /app/prestart.sh, you could add migrations to this file, e.g.:"

echo "
#! /usr/bin/env bash

# Let the DB start
sleep 10;
# Run migrations
alembic upgrade head
"
export PORT=8002
export HOST=0.0.0.0
export PYTHONPATH=/app/utils:$PYTHONPATH
echo $PYTHONPATH

pip install --upgrade pip
pip install -r requirements.txt