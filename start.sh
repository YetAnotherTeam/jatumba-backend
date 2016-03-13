#!/bin/bash
git pull
killall -9 gunicorn
gunicorn TPD.wsgi:application --access-logfile /home/bulat/log/access.log --error-logfile /home/bulat/log/error.log --log-level debug --bind=unix:/tmp/gunicorn.sock &
