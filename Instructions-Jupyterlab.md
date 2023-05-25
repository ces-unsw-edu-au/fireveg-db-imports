# Jupyter Lab

These are the steps I followed to configure a Jupyter Lab environment.

## Create and activate python environment

### with venv

Use an specific version of python3...

```sh
conda deactivate
mkdir -p $HOME/venv
/usr/local/bin/python3 -m venv $HOME/venv/jptr
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



## Install python libraries

### common ones
```sh
pip install openpyxl pandas
pip install pyprojroot
```

### connect to postgresql

To connect to postgresql database we need to have a client in the local computer. 

For postgresql connection on mac, use: https://postgresapp.com, download and then 
```sh
sudo mkdir -p /etc/paths.d &&
echo /Applications/Postgres.app/Contents/Versions/latest/bin | sudo tee /etc/paths.d/postgresapp
```

Restart the terminal, then:

```sh
source $HOME/venv/jptr/bin/activate
pip install psycopg2
```



## Adding the R kernel

Activate the right R kernel...

```{r}
#R --vanilla
install.packages('IRkernel')
IRkernel::installspec()
```


## Start the jupyter lab interface with pythonpath

If we want to have shared functions in different workbooks:


```sh
cd $HOME/proyectos/fireveg/fire-veg-aust
## conda activate jptr
##or 
## source $HOME/venv/jptr/bin/activate
##or 
## source ~/proyectos/venv/jupyterlab/bin/activate
## then:
env PYTHONPATH=$HOME/proyectos/fireveg/fire-veg-aust jupyter-lab
```


## Hidden directories

To run the code in this repository we use two hidden directories to host database connection parameters and input data folders.

These folders need to be created first:

```{sh}
cd $HOME/proyectos/fireveg/fire-veg-aust 
mkdir -p secrets
mkdir -p data
```

These folders are not tracked by git (check entries in .gitignore).