#!/bin/bash
git pull
pipenv install --dev
/home/jatumba/.virtualenvs/circus/bin/circusctl restart
