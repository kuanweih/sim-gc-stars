#!/bin/bash
#SBATCH  --export=NONE
#SBATCH  --partition=long
#SBATCH  --constraint=intel_e5_v4
#SBATCH  --ntasks-per-node=16
#SBATCH  --time=24:00:00
#SBATCH  --job-name=sim-gcs


# use py3 on coma (don't need this if already using py3)
source  activate  mypython3

python  -W  ignore  sim_isochrone.py
