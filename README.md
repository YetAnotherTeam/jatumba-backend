[![Build Status](https://travis-ci.org/YetAnotherTeam/jatumba-backend.svg?branch=master)](https://travis-ci.org/YetAnotherTeam/jatumba-backend)

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
$ pipenv --three
$ pipenv install --dev
```
Install `circus`.
```bash
$ mkvirtualenv circus --python=python2.7
$ pip install -r circus/requirements.txt
```

## Usage
This script run `daphne`, `gunicorn`, `workers` and `circus`, `redis` web interaces.
```bash
$ workon circus
$ circusd circus/circus.ini --daemon
```
