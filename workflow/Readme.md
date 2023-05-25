# workflow folder

All the script are saved as Jupyter Notebooks and include minimal documentation and comments on each step. 

I am in the process of moving shared functions to a module in folder `lib` to ensure consistency in the use of the functions, more generalised and customizable functions, and also streamline the documentation of steps in the notebooks.

## Subfolders

### `Field-forms`

Scripts to import field data from spreadsheets. Spreadsheets or Workbooks in XLSX format provided by Prof. David Keith, [FAA](https://www.science.org.au/profile/david-keith), but created by different observers. Scripts were adapted to import spreadsheets as given, with minimum editing of original files. 

### `Import-...` scripts

- `Import-austraits`:
- `Import-austraits-build`:
- `Import-NSWFRD`:

These scripts were created to import existing data. 
`NSWFRD` refers to the New South Wales Flora Fire Response Database and is a static spreadsheet. We are using the most recent available version (). 
`austraits` refers to the austraits project and is an active repository. Scripts were tested with version ... from ... We expect to adapt the code as new versions become available. 
`austraits-build` contain source data and source code to build the complete austraits database. It allows to import observation directly from original data sources. 

### `Input-forms`

Code to create the template of input forms for fire ecology traits from the literature.

### `Literature-review`

Miscellaneous code, check literature records (name is a bit misleading, will change soon)

### `Report-output`

Code for exporting data in spreadsheet format.

