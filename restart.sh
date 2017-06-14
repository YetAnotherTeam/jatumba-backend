#!/bin/bash
set -e
git pull
pipenv lock -r > requirements.txt
/home/jatumba/.virtualenvs/jatumba-backend/bin/pip install -r requirements.txt
/home/jatumba/.virtualenvs/circus/bin/circusctl restart
