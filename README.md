# INFOMR
Multimedia Retrival project

How to build:
- install on python 3.6.8 environment the libraries in the freeze.txt file with:

    pip install -r /path/to/freeze.txt
- create a postgresql database and load in it infomr_final.pgsql
- change user, database name and password in database_classes.py with the information from the newly created
- run Annoy.py
- run GUI.py


Info:
- The main.py file contains evaluation and database update functions
- The Mesh.py file contains the Mesh class object which is used to normalise and create silhouettes from an off file
- The Mesh2D.py file contains Mesh2D class object which computes the feature vector for the given mesh
- The Annoy.py file contains function to create and update the ANN index
- The GUI.py file contains the gui. Running this script let the user access the system. If no ANN is present in project directory, run Annoy.py
- The database_classes.py contains the ORM mapping to the database
- The database is stored in infomr_final.pgsql file.
