## Hidden directories

To run the code in this repository we use two hidden directories to host database connection parameters and input data folders.

These folders need to be created first:

```{sh}
cd $HOME/proyectos/fireveg/fire-veg-aust 
mkdir -p secrets
mkdir -p data/input-field-form
mkdir -p data/output-report

```

These folders are not tracked by git (check entries in .gitignore).