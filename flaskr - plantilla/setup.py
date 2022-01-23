
# We make our project installable by building a distribution file that can be installed in another environment.
# This makes deploying the project the same as installing any other library, so we are using all the standart Python tool to manage everything.

# This file, "setup.py" describes our project and the files that belong to it.

# We use "setuptools" to prepare our files.
from setuptools import find_packages, setup

# Command to create the single-file importable distribution format
setup(
    # Nombre of the folder to prepare
    name='flaskr',
    # Version of the distribution
    version='1.0.0',
    # We ask it to find packages inside our folder (by searching the __init__.py)
    packages=find_packages(),
    # Include all our data_files found in the packages. This means preparing a file called "MANIFEST.in".
    include_package_data=True,
    # Including the setup in a zipfile or not.
    zip_safe=False,
    # Establish the condition that "flask" must be installed before installing this distribution.
    install_requires=[
        'flask',
    ],
)

# In the MANIFEST.in file we wrote the following:

# include flaskr/schema.sql
## Include our sql schema of the db
# graft flaskr/static
# graft flaskr/templates
## Copy every file from "/static" and "/templates"
# global-exclude *.pyc
## Don't include any byte-code files.

# To install this project, we would use "pip install -e ." by being in its current directory. "-e" means we are installing in edit mode, so we can make changes to the local code
# and we will only need to reinstall if ywe change the metadata, such as its dependencies. 

# If we install it, as far as we have FLASK_APP set to "flaskr", "flask run" will run the application from anywhere, not just the "flask-tutorial" directory.
# We can check our installed modules with "pip list"

