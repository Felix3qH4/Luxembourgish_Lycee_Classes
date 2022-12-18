import argparse
from pathlib import Path
import pandas as pd
import json


# Command line
PARSER = argparse.ArgumentParser(description="Type --help for help")

# Add arguments '-f', '-c', '-l', '-s'
PARSER.add_argument("-f", "--files", nargs="+",
                    help="Specify specific files that should be converted from excel to json files")
PARSER.add_argument("-c", "--coefficient", action="store_false",
                    help="If flag is used, coefficients won't be stored")
PARSER.add_argument("-l", "--lessons", action="store_false",
                    help="If flag is used, number of lessons won't be stored")
PARSER.add_argument("-s", "--sublessons", action="store_false",
                    help="If flag is used, sublessons won't be stored (= lessons that are made up of multiple lessons will only have the main lesson name saved but not the lessons it is composed from")

ARGS = PARSER.parse_args()
# / Command line /

# Default excel files
EXCEL_FILE_CLASSIQUE: str = "Classique_Classes.xlsx"
EXCEL_FILE_GENERAL: str = ""
EXCEL_FILE_GERMANO_LUX: str = ""

#EXCEL_FILES : list = [EXCEL_FILE_CLASSIQUE, EXCEL_FILE_GENERAL, EXCEL_FILE_GERMANO_LUX]
EXCEL_FILES: list = [EXCEL_FILE_CLASSIQUE]


def parse_excel_file(file: str) -> None:
    """
    This is where the file will be broken down into 1st the blocks (ex.: 7ème, 6ème) and then the different classes (ex.: 7C, 7I-EN)

    :param file: Name of the file that should be parsed (str)
    :returns None
    """

    print(f"[DEBUG]: Parsing file - {file}")

    # Output data that will be written to the file
    json_data: list[dict[str, list[dict[str, float, float]]]] = []

    # Read the excel file and replace NaN (=empty fields)
    data = pd.read_excel(file)
    data.fillna("None", inplace=True)

    # Get the names of the columns (ex.: ClassNames, SubjectName)
    column_names = data.axes[1].tolist()

    current_index = 0

    # Get the "ClassNames" and other column names (ex.: ClassNames, ClassNames.1, ClassNames.2)
    classnames_str = [i for i in column_names if i.startswith('ClassNames')]
    subjectnames_str = [i for i in column_names if i.startswith('SubjectName')]
    subjectlessons_str = [i for i in column_names if i.startswith('SubjectLessons')]
    subjectcoefs_str = [i for i in column_names if i.startswith('SubjectCoef')]
    combinames_str = [i for i in column_names if i.startswith('CombiName')]
    combicoefs_str = [i for i in column_names if i.startswith('CombiCoef')]

    # 'pyclasses' or 'pyclass' stands for the classes inside python, to not mix it up with 'classes' in the schools
    # A list of all the pyclasses CLASS() representing the different real classes
    classes = []

    # For each 'block' (ex.: 7ème classes or 6ème classes), check when a new class starts and create a CLASS() class for that pyclass
    for block in range(len(classnames_str)):
        # Get the data for the "ClassNames" and other columns
        classnames = data[classnames_str[current_index]]
        subjectnames = data[subjectnames_str[current_index]]
        subjectlessons = data[subjectlessons_str[current_index]]
        subjectcoefs = data[subjectcoefs_str[current_index]]
        combinames = data[combinames_str[current_index]]
        combicoefs = data[combicoefs_str[current_index]]

        current_index += 1
        print(f"[DEBUG]: Block Nr. {current_index}")

        # Starting line for parsing the data for class names
        line: int = 0
        # Starting line of a new class
        class_start_line: int = None
        # While the line we are at is smaller than the number of lines there are, parse
        while line < len(classnames.values):
            # If there is a new class
            if classnames.values[line] != "None" or line+1 == len(classnames.values):
                print(classnames.values[line])
                # If there was a class before this one, set the endline of the class before
                if class_start_line:
                    class_end_line = line
                    new_class = CLASS(class_start_line, class_end_line, classnames,
                                      subjectnames, subjectlessons, subjectcoefs, combinames, combicoefs)
                    classes.append(new_class)
                    class_start_line = None

                # If there was no class before, set the startline of this class (also when the class before was finished)
                if not class_start_line:
                    class_start_line = line

            # Go to the next line
            line += 1

    # For each pyclass in the list, get the class representation and add it to the output for the json file
    for _class in classes:
        json_data.append(_class.__repr__())

    with open("output/out.json", "w", encoding="utf-8") as _file:
        json.dump(json_data, _file, ensure_ascii=False)


##########################
## Class representation ##
##########################
class CLASS():
    def __init__(self, startline: int, endline: int, classnames: pd.Series, subjectnames: pd.Series, subjectlessons: pd.Series, subjectcoefs: pd.Series, combinames: pd.Series, combicoefs: pd.Series):
        self.startline = startline
        self.endline = endline
        self.classnames = classnames
        self.subjectnames = subjectnames
        self.subjectlessons = subjectlessons
        self.subjectcoefs = subjectcoefs
        self.combinames = combinames
        self.combicoefs = combicoefs

        self.current_coef: int = None
        self.current_subject: dict = {}
        self.subjects = []
        self.current_combis = []

        # Representation of the class which will then be written to the output file
        self.class_repr = {
            "name": self.classnames.values[startline], "subjects": self.subjects}

        # Parse the lines to complete the data about this class
        self.build()

    def __repr__(self) -> str:
        return self.class_repr

    def build(self):
        # The current line we are processing
        line: int = self.startline

        # For i in range(number of lines that contain data for this class)
        for i in range((self.endline)-self.startline):
            subject = self.subjectnames.values[line]
            lessons = self.subjectlessons.values[line]
            coef = self.subjectcoefs.values[line]
            combiname = self.combinames.values[line]
            combicoef = self.combicoefs.values[line]

            # If there is a subject
            if subject != "None":
                # If there were combi subjects in the subject before, save them and reset combi subjects list
                if len(self.current_combis) > 0:
                    if ARGS.sublessons:
                        self.current_subject["subsubjects"] = self.current_combis
                    self.current_combis = []
                    self.current_subject = {}

                # Update the coefficient if there is a new one
                if coef != "None":
                    self.current_coef = coef

                self.current_subject["name"] = subject
                if ARGS.lessons:
                    self.current_subject["lessons"] = lessons

                if ARGS.coefficient:
                    self.current_subject["coef"] = self.current_coef

                # If there is a combi subject
                if combiname != "None":
                    self.current_combis.append({
                        "name": combiname,
                        "coef": combicoef
                    })


                self.subjects.append(self.current_subject)

                # If this subject does not have any combi subjects, clear it so we can proceed to the next subject
                if len(self.current_combis) < 1:
                    self.current_subject = {}

            # If there is no subject but a combi subject, add it to the last known subject as combi subject
            if subject == "None":
                if combiname != "None":
                    self.current_combis.append({
                        "name": combiname,
                        "coef": combicoef
                    })

            # Go to the next line
            line += 1


if __name__ == "__main__":
    # If user wants to parse specific files
    if ARGS.files:
        for file in ARGS.files:
            filepath = Path(file)
            if filepath.is_file():
                parse_excel_file(str(file))
            else:
                print(
                    f"[Invalid File]: The following file was skipped as the path is incorrect '{file}'")
    else:
        for file in EXCEL_FILES:
            filepath = Path(file)
            if filepath.is_file():
                parse_excel_file(str(file))
            else:
                print(
                    f"[Invalid File]: The following file was skipped as the path is incorrect '{file}'")
