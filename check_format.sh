#!/usr/bin/env bash

mypy papeles/
pylint -j 4 --rcfile=.pylintrc papeles/*
yapf -vv -pri ./papeles
