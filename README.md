# Repast4pyModels

This is a repository containing scripts to setup the Repast4py environment in GMU's Hopper high performance cluster. The goal being to run several distributed agent based models.

## Sub Project: Deer Covid modelling
Covid-19 has been detected in a local deer population. This project aims to combine deer behaviour models and human population models in order to run scenarious of human <> deer infections. 

# Quick Start

This guide is for GMU members who have access to the Slurm/Hopper cluster.

### With miniconda:

Here's how you run this on Hopper:
- [Log into Hopper](https://wiki.orc.gmu.edu/mkdocs/Logging_Into_Hopper/)
- [Install miniconda](https://wiki.orc.gmu.edu/mkdocs/Conda_Environments_on_Hopper/) 
- Load Git module and pull repo:
```
module load git
git clone https://github.com/heykuldip/Repast4pyModels.git
```
- Setup conda environment: 
- Run demo script

### With Docker/Singularity

To run this on the Hopper HPC you need to pull the Repast4Py docker container, convert it to a Singularity file, and run the code in this repo using the Singularity file.

```

```

# How to Contribute
Here's how you contribute to this project:
 - Create a branch
 - Add some code
 - Request that your branch get merged into main

# Containers 
Hopper can use singularity containers to run code. It also looks like it's not too difficult to convert Docker containers to Singularity containers. The best place to start seems to be with a Nvidia GPU optimised container and add code to there (even if you're not going to use the GPU)

* [Hopper Singularity README](https://wiki.orc.gmu.edu/mkdocs/Containerized_jobs_on_Hopper/)
* [Nvidia Python Containers](https://catalog.ngc.nvidia.com/orgs/nvidia/teams/distroless/containers/python/tags)
* [Building your own](https://wiki.orc.gmu.edu/mkdocs/Containerized_jobs_on_Hopper/#building-your-own-containers)
* [NASA guide on converting Docker > Singularity](https://www.nas.nasa.gov/hecc/support/kb/converting-docker-images-to-singularity-for-use-on-pleiades_643.html)

