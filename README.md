# Wikidata Literary Canon

This repository contains the programming code (Python and Orange Data Mining) and data to build a literary canon from Wikidata and Wikipedia.

Introduction
============

The repository includes all the scripts needed to collect data from Wikidata through SPARQL queries, retrieve data from Wikipedia articles using XTools, and calculate a metric that allows building a ranking of encyclopedic objects. Although it is designed to process items from literary works, it could also be adapted to any other domain by modifying the SPARQL queries.

Files and folders
=================
* orange: carpeta con el código y ficheros de procesamiento de datos de Orange Data Mining.
* python: código Python para recuperar los números de palabras de todos los artículos de Wikipedia de obras literarias recopiladas de Wikidata (get-xtools-api.py) y procesar todos los datos (process.py).
* orange: Folder with the Orange Data Mining code and data processing files.
* python: Python code to retrieve the word counts of all Wikipedia articles of literary works collected from Wikidata (get-xtools-api.py) and process all the data (process.py).
* canon-list.pdf: Final list with the proposed literary canon.
* clustered-items.csv: Result of applying K-Means++ to perform clustering on literary works.
* results.zip: Data resulting from running process.py
* source-dataset.zip: Data needed to run process.py
* sparql-and-curl-queries.txt: SPARQL queries to retrieve data on literary works from Wikidata.
Authors
=======
* Juan-Antonio Pastor-Sánchez (University of Murcia, Spain)
* Tomás Saorín (University of Murcia, Spain)

License
=======
Python code is available under GNU General Public LIcense v3.0. Data is available under Creative Commons BY-SA 4.0
