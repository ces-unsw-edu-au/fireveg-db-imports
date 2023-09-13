# Fire Ecology Traits for Plants

The ***Fire Ecology Traits for Plants*** project is being developed by  [José R. Ferrer-Paris](https://github.com/jrfep) and David Keith in the Centre for Ecosystem Science, University of New South Wales

Please cite this work as:

> Ferrer-Paris, J. R. and Keith, D. A. (2022) Fire Ecology Traits for Plants: A database for fire research and management. Version 1.00. Centre for Ecosystem Science, University of New South Wales, Sydney, Australia.


This work has been supported by:

- [University of New South Wales](https://www.unsw.edu.au/)
- [NSW Bushfire Research Hub](https://www.bushfirehub.org/)
- [NESP Threatened Species Recovery Hub](https://www.nespthreatenedspecies.edu.au/)
- [NSW Department of Planning & Environment](https://www.planning.nsw.gov.au/)

## Components of the project

### SQL structure of the database

Code for defining the structure of the tables in a PostgreSQL database is available in the [fireveg-db](https://github.com/ces-unsw-edu-au/fireveg-db) repository.


### Database content

An export of the SQL structure and iniitial data is available in Figshare:

> Ferrer-Paris, José R.; Keith, David A. (2023). Fire Ecology Traits for Plants: Database snapshot (SQL dump). figshare. Dataset. https://doi.org/10.6084/m9.figshare.23361002.v1

### WebApp

Code for running a Flask webapp available in the [fireveg-webapp](https://github.com/ces-unsw-edu-au/fireveg-webapp) repository.

### Code for managing the database

This repository contains several [Jupyter notebooks](https://jupyter.org/try) with code and instruction to perform several tasks in the database.

Visualisation of the notebooks is possible in GitHub, or in the [Jupyter Notebook Viewer](https://nbviewer.org/).

#### Repository structure

- Folder [python/](/python/). Most code is written in [python](https://www.python.org/).
   - [Field-forms/](/python/Field-forms): code for reading field-work data from excel documents
   - [Import-austraits/](/python/mport-austraits)
   - [Import-NSWFRD/](/python/Import-NSWFRD)
   - [Input-forms/](/python/Input-forms)
   - [Literature-review/](/python/Literature-review)
   - [Report-output/](/python/Report-output): code for writing output `xlsx` documents with summaries of fire ecology traits for plants

- Folder [R/](/R). Some scripts in [R](https://www.r-project.org/) are also available.
