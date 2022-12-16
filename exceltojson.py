import argparse
from pathlib import Path
import pandas as pd

PARSER = argparse.ArgumentParser(description="Type --help for help")

PARSER.add_argument("-f", "--files", nargs="+", help="Specify specific files that should be converted from excel to json files")
PARSER.add_argument("-c", "--coefficient", action="store_false", help="If flag is used, coefficients won't be stored")
PARSER.add_argument("-l", "--lessons", action="store_false", help="If flag is used, number of lessons won't be stored")
PARSER.add_argument("-s", "-sublessons", action="store_false", help="If flag is used, sublessons won't be stored (= lessons that are made up of multiple lessons will only have the main lesson name saved but not the lessons it is composed from")

ARGS = PARSER.parse_args()


EXCEL_FILE_CLASSIQUE : str = "Classique_Classes.xlsx"
EXCEL_FILE_GENERAL : str = ""
EXCEL_FILE_GERMANO_LUX : str = ""

#EXCEL_FILES : list = [EXCEL_FILE_CLASSIQUE, EXCEL_FILE_GENERAL, EXCEL_FILE_GERMANO_LUX]
EXCEL_FILES : list = [EXCEL_FILE_CLASSIQUE]


def parse_excel_file(file : str) -> None:
    print(f"[PARSER]: Parsing file - {file}")

    ## Read the excel file and replace NaN (=empty fields) 
    data = pd.read_excel(file)
    data.fillna("None", inplace=True)

    #data_x_length = data.shape[1]
    header_names = data.axes[1].tolist()

    current_index = 0

    classnames_str = [i for i in header_names if i.startswith('ClassNames')]
    subjectnames_str = [i for i in header_names if i.startswith('SubjectName')]
    subjectlessons_str = [i for i in header_names if i.startswith('SubjectLessons')]
    subjectcoefs_str = [i for i in header_names if i.startswith('SubjectCoef')]
    combinames_str = [i for i in header_names if i.startswith('CombiName')]
    combicoefs_str = [i for i in header_names if i.startswith('CombiCoef')]

    classnames = data[classnames_str[current_index]]
    subjectnames = data[subjectnames_str[current_index]]
    subjectlessons = data[subjectlessons_str[current_index]]
    subjectcoefs = data[subjectcoefs_str[current_index]]
    combinames = data[combinames_str[current_index]]
    combicoefs = data[combicoefs_str[current_index]]

    #print(data.axes[1].tolist())
    #for i in range(len(classnames)):
        #print(classnames)




if __name__ == "__main__":
    ## If user wants to parse specific files
    if ARGS.files:
        for file in ARGS.files:
            filepath = Path(file)
            if filepath.is_file():
                parse_excel_file(str(file))
            else:
                print(f"[Invalid File]: The following file was skipped as the path is incorrect '{file}'")
    else:
        for file in EXCEL_FILES:
            filepath = Path(file)
            if filepath.is_file():
                parse_excel_file(str(file))
            else:
                print(f"[Invalid File]: The following file was skipped as the path is incorrect '{file}'")

