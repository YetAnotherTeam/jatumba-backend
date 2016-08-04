#!/bin/bash
git pull
pip install -r requirements.txt
/home/jatumba/.virtualenvs/circus/bin/circusctl restart
