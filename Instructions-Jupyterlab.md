# Jupyter Lab

These are the steps I followed to configure a Jupyter Lab environment.

## create and activate python environment

### with venv

```sh
conda deactivate
mkdir -p $HOME/venv
python3 -m venv $HOME/venv/jptr
source $HOME/venv/jptr/bin/activate
```

Check python version
```sh
python --version
```

Update and install modules
```sh
pip install --upgrade pip
#/usr/local/opt/python@3.9/bin/python3.9 -m pip install --upgrade pip
pip3 install jupyterlab

```


### Conda
Create a new environment with conda:

```sh
conda create --name jptr
```

Activate the environment and install R (with RPostgreSQL package) and jupyter lab:

```{bash}
conda activate jptr
conda install -c conda-forge r-rpostgresql r-readxl devtools
conda install -c conda-forge jupyterlab
```

## Activate the right R kernel...

Within the environment

```{r}
#R --vanilla
IRkernel::installspec()
```

## Install additional libraries

Install python libraries with pip

```{bash}
pip install openpyxl psycopg2-binary
pip install pandas SQLAlchemy
pip install pybtex
#pip install postgis
```

## Start the jupyter lab interface:

```sh
cd ~/proyectos/fireveg/fire-veg-aust
## conda activate jptr
##or 
## source $HOME/venv/jptr/bin/activate
## then:
jupyter-lab
```
