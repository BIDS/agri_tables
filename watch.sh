#!/usr/bin/env bash
# depends on entr: http://entrproject.org/
find . -name '*.py' | entr ./run.sh $1
