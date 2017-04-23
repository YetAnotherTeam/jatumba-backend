#!/bin/bash
set -e
git pull
pipenv install --dev
/home/jatumba/.virtualenvs/circus/bin/circusctl restart
