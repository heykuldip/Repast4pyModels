# Use an official Python runtime as a parent image
FROM ghcr.io/gmu-geosciences/repast4py-container:latest

# Set the working directory in the container
WORKDIR /usr/src/app

# Copy the current directory contents into the container at /usr/src/app
COPY ./repast4py .

# Run python.py when the container launches
# mpirun -n 4 python rndwalk.py random_walk.yaml
CMD ["mpirun","-n","4", "python", "./rndwalk.py", "random_walk.yaml"]