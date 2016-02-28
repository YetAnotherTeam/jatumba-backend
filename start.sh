#!/bin/bash
killall -9 gunicorn
gunicorn TPD.wsgi:application &
