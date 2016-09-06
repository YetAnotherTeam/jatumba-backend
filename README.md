JATumba backend
===============
Server-side for `JATumba` application
## Required
* Python Version >=3.5 for `JATumba` application
* Python Version >=2.7 for `circus`
* Nginx
* Postgresql Version >=9.5
* NPM


## Installation
Install
```bash
$ sudo npm install -g redis-commander
```
Install `JATumba` application.
```bash
$ mkvirtualenv jatumba --python=python3.5
$ pip install -r requirements.txt
```
Install `circus`.
```bash
$ mkvirtualenv circus --python=python2.7
$ pip install -r circus/requirements.txt
```

## Usage
This script run `daphne`, `gunicorn`, `workers` and `circus`, `redis` web interaces.
```bash
$ ./start.sh
```