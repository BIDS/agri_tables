#!/usr/bin/env bash
echo
echo "------------------------------------------------------------"
docker-compose run --rm extractor python run.py $1
