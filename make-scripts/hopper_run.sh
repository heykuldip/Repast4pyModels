#!/bin/bash
# Script to run the repast script in hopper

echo "Setting up Slurm..."
salloc -p normal -q normal -n 1 --ntasks-per-node=24 --mem=50GB

echo "Running repast4py script on Hopper..."
cd ./repast4py
mpirun -n 4 python rndwalk.py random_walk.yaml
