FROM python:3.11
# Taken from: https://github.com/Repast/repast4py/blob/master/Dockerfile

RUN apt-get update && \
    apt-get install -y  mpich \
        && rm -rf /var/lib/apt/lists/*

# Install the python requirements
COPY ./requirements.txt ./requirements.txt
RUN pip install -r ./requirements.txt

# Install repast4py
RUN env CC=mpicxx CXX=mpicxx pip install repast4py

# RUN apt-get update \        
#     apt-get install -y git

# RUN mkdir -p /repos && \
#     cd /repos && \
#     git clone --depth 1 https://github.com/networkx/networkx-metis.git && \
#     cd /repos/networkx-metis && \
#     python setup.py install

# Set the PYTHONPATH to include the /repast4py folder which contains the core folder
ENV PYTHONPATH=/repast4py/src