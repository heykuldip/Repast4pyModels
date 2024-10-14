#!/bin/bash
# This is to setup the Hopper environment in order to run the repast models
# It's a bit of a chicken/egg situation since you have to load git first
# in order to get this script in order to load git...

echo "=============================="
echo "== Running Repast Script... =="
echo "==============================" 

echo "Building Container..."
docker build -t repast-test .

echo "Running repast4py script in local docker env..."
docker run -it --rm --name repast-local-docker repast-test