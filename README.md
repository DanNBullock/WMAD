# WMAD
White Matter Anatomy Database
Cataloging accounts of white matter tracts and their anatomy throughout the literature.

## Production Info

### Author
[Dan Bullock](https://github.com/DanNBullock/) (bullo092@umn.edu)

### Contributors/Curators

Elena Hayday

Sylvia Bindas

### PI
[Sarah Heilbronner](https://med.umn.edu/bio/department-of-neuroscience/sarah-heilbronner) (heilb028@umn.edu)

### Funding Information
[This section needs expansion. You can help by adding to it.]

## Project Scope

### The target problem
In the field of white matter anatomy there are a range of conflicting accounts of anatomical characteristics and associated terminology for white matter tracts (bundles of axons that connect parts of the brain).  This problem has been highlighted in several recent publications including [Bullock et al. 2021](https://psyarxiv.com/fvk5r/) and [Schilling et al 2021](https://doi.org/10.1016/j.neuroimage.2021.118502).  Currently, individual researchers must expend great effort to locate and examine even a fraction of the accounts which are pertinent to their structure(s) of interest.  Furthermore, due to the aforementioned terminological and descriptive challenges even the most dedicated investigators will only encounter a portion of the work that could speak to their research.

### The proposed solution
In order to provide researchers with the ability to explore and consider pertinent accounts of specific white matter structures of interest we present the White Matter Anatomy Database (WMAD) resource.  Instead of having to manually search each candidate research article that may be relevant to a researchers interest, here we have curated a database which localizes the _precise_ text sections (via [regex](https://en.wikipedia.org/wiki/Regular_expression) bounds) describing any given white matter structure, along with links to images depicting those white matter structures.  Using our [jupyter notebook interface](https://github.com/DanNBullock/WMAD/blob/main/Notebooks/Interact_With_WMAD.ipynb) on [platform] users can view the text excerpts and images associated with structures specified by the user from multiple publications all alongside one another in order to facilitate efficient comparison and consideration.

## Repository Contents
Below you will find a description of the various directories’ contents, beginning with the [primary jupyter notebook](https://github.com/DanNBullock/WMAD/blob/main/Notebooks/Interact_With_WMAD.ipynb) itself.

### Notebooks 
A directory containing the notebook itself.  Required packages can be found in the [requirements.txt](https://github.com/DanNBullock/WMAD/blob/main/requirements.txt) file.

### CompleteExample
An example of a completed article distillation, with the relevant excel files and directory structure formatted in the standardized fashion.

### Excel files
Template versions of the excel formats (i.e. blank).

### JSON_examples
Examples of the JSON structure formats we will distill from the excel files.  Provided both in template and example form.

### pyWMAD
Python code used to convert the excel file entries (organized in the appropriate directory structures) into amalgamated JSON file outputs, on a per document/article basis.

### completedArticles
A directory containing directories corresponding to each article that has been distilled/processed.  Each of these subdirectories is structured in accordance with the example found in the **CompleteExample** directory.

### dbStore
This directory contains the JSON file that corresponds to the most recently amalgamated version of the excel articles stored in **completedArticles** and thereby functions as the primary database object for WMAD.
