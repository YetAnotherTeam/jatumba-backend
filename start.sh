#!/bin/bash
git pull
/home/jatumba/.virtualenvs/circus/bin/circusctl stop
ps aux | grep -i circus[d] | awk {'print $2'} | xargs kill -9
/home/jatumba/.virtualenvs/circus/bin/circusd circus/circus.ini --daemon
