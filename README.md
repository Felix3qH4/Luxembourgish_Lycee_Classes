# Luxembourgish Lycée Classes
Contains all classes which are in the Horaire et Programme and have their lessons with the respective coefficient written in the document.
Classes where there are no coefficients available are not in this collection.

The data is available as .xlsx file or .json file.
In the json file, each class, each subject and each subsubject have an UUID from [python uuid module](https://docs.python.org/3/library/uuid.html).

Missing:
- Classique:
    - 2BI-FR
    - 1BI-FR
    - 2BI-EN
    - 1BI-EN

- Technique:
    - All

- Enseignement Germano-Luxembourgeois:
    - All


<br>
<br>
<br>


### Exceltojson.py - Usage:

This script converts the .xlsx file to a .json file and adds the UUID if asked for.
To use it, open a terminal in the directory of the file and enter 'python exceltojson.py' followed by the arguments you want.
Available arguments are:
- -f {filename}
    - To pass the files you want to convert to json files. If not used, the files that will be converted are:
        - 'Classique_Classes.xlsx'
- -c
    - If used, the coefficients of the subjects will not be stored in the json file
- -l
    - If used, the number of lessons per subject won't be stored in the json file
- -s
    - If used, no subsubjects will be stored but only the main subject that is composed of the subsubjects
- -u
    - If used, each class, subject and subsubject will get an UUID in the json file like follows: 'id': 'UUID'
