import argparse
from pathlib import Path
import pandas as pd
import json


## Command line
PARSER = argparse.ArgumentParser(description="Type --help for help")

PARSER.add_argument("-f", "--files", nargs="+", help="Specify specific files that should be converted from excel to json files")
PARSER.add_argument("-c", "--coefficient", action="store_false", help="If flag is used, coefficients won't be stored")
PARSER.add_argument("-l", "--lessons", action="store_false", help="If flag is used, number of lessons won't be stored")
PARSER.add_argument("-s", "-sublessons", action="store_false", help="If flag is used, sublessons won't be stored (= lessons that are made up of multiple lessons will only have the main lesson name saved but not the lessons it is composed from")

ARGS = PARSER.parse_args()
## / Command line /

EXCEL_FILE_CLASSIQUE : str = "Classique_Classes.xlsx"
EXCEL_FILE_GENERAL : str = ""
EXCEL_FILE_GERMANO_LUX : str = ""

#EXCEL_FILES : list = [EXCEL_FILE_CLASSIQUE, EXCEL_FILE_GENERAL, EXCEL_FILE_GERMANO_LUX]
EXCEL_FILES : list = [EXCEL_FILE_CLASSIQUE]




def parse_excel_file(file : str) -> None:
    print(f"[DEBUG]: Parsing file - {file}")

    ## Output
    json_data : list[dict[str, list[dict[str, float, float]]]] = []

    ## Read the excel file and replace NaN (=empty fields) 
    data = pd.read_excel(file)
    data.fillna("None", inplace=True)


    #data_x_length = data.shape[1]

    ## Get the names of the columns (ex.: ClassNames, SubjectName)
    column_names = data.axes[1].tolist()

    current_index = 0

    ## Get the "ClassNames" and other column names (ex.: ClassNames, ClassNames.1, ClassNames.2)
    classnames_str = [i for i in column_names if i.startswith('ClassNames')]
    subjectnames_str = [i for i in column_names if i.startswith('SubjectName')]
    subjectlessons_str = [i for i in column_names if i.startswith('SubjectLessons')]
    subjectcoefs_str = [i for i in column_names if i.startswith('SubjectCoef')]
    combinames_str = [i for i in column_names if i.startswith('CombiName')]
    combicoefs_str = [i for i in column_names if i.startswith('CombiCoef')]



    for block in range(len(classnames_str)):
        ## Get the data for the "ClassNames" and other columns 
        classnames = data[classnames_str[current_index]]
        subjectnames = data[subjectnames_str[current_index]]
        subjectlessons = data[subjectlessons_str[current_index]]
        subjectcoefs = data[subjectcoefs_str[current_index]]
        combinames = data[combinames_str[current_index]]
        combicoefs = data[combicoefs_str[current_index]]

        current_index += 1
        #print(f"[DEBUG]: Block Nr. {current_index}")

        line = 0
        class_start_line = None
        print(len(classnames.values))
        while line < len(classnames.values):
            if classnames.values[line] != "None" or line+1 == len(classnames.values):
                print(classnames.values[line])
                if class_start_line:
                    class_end_line = line
                    class_data = parse_class(class_start_line, class_end_line, classnames, subjectnames, subjectlessons, subjectcoefs, combinames, combicoefs)
                    json_data.append(class_data)
                    class_start_line = None
                if not class_start_line:
                    class_start_line = line
            
            line += 1
        

    with open("output/out.json", "w", encoding="utf-8") as _file:
        json.dump(json_data, _file, ensure_ascii=False)


def parse_class(startline:int, endline:int, classnames:pd.Series, subjectnames:pd.Series, subjectlessons:pd.Series, subjectcoefs:pd.Series, combinames:pd.Series, combicoefs:pd.Series) -> dict:
    _class : dict[str, list]= {
        "name": classnames.values[startline]
    }
    subjects : list[dict, dict] = []

    coefficient = None
    subject = {}
    endline += 1
    for line in range(endline-startline):
        ## If there is a coefficient (1st line and when it changes)
        if subjectcoefs.values[line] != "None":
            coefficient = subjectcoefs.values[line]
        
        ## If there is a subject
        if subjectnames.values[line] != "None":
            subject["name"] = subjectnames.values[line]
            subject["lessons"] = subjectlessons.values[line]
            subject["coef"] = coefficient
            subjects.append(subject)
            #print(subject)
            subject = {}

    print(f"ENDING CLASS AT LINE: {line}")
    _class["subjects"] = subjects
    print(_class)
    #print(_class)
    return _class

    # ## For each block of rows
    # for j in range(len(classnames_str)):

    #     ## Get the data for the "ClassNames" and other columns 
    #     classnames = data[classnames_str[current_index]]
    #     subjectnames = data[subjectnames_str[current_index]]
    #     subjectlessons = data[subjectlessons_str[current_index]]
    #     subjectcoefs = data[subjectcoefs_str[current_index]]
    #     combinames = data[combinames_str[current_index]]
    #     combicoefs = data[combicoefs_str[current_index]]

    #     classinfo : dict[str, list[str, float, float]] = {}
    #     coefficient : int = None
    #     combis = []
    #     subjects = []
        
    #     ## For each line in the row (y axis)
    #     for index in range(classnames.shape[0]):

    #         ## If there is a value in the first row (="ClassNames") create a new class
    #         if classnames.values[index] != "None":
    #             #classinfo["name"] = classname
    #             classinfo["subjects"] = subjects
    #             json_data.append(classinfo)

    #             classinfo = {}

    #             classinfo["name"] = classnames.values[index]
    #             subjects = []
    #             combis = []
    #             coefficient = None

    #         if subjectnames.values[index] != "None":
    #             subject = {}

    #             ## If this is the first subject with a coefficient store it for the subjects under this one
    #             if subjectcoefs.values[index] != "None":
    #                 coefficient = subjectcoefs.values[index]

    #             if combinames.values[index] != "None":
    #                 combis.append(
    #                     {
    #                         "name": combinames.values[index],
    #                         "coef": combicoefs.values[index]
    #                     }
    #                 )

    #                 index += 1
    #                 stop_iteration = False

    #                 while not stop_iteration:
    #                     ## If there is a subject in the combi section append it to the list
    #                     if combinames.values[index] != "None" and subjectnames.values[index] == "None":
    #                         combis.append(
    #                             {
    #                                 "name": combinames.values[index],
    #                                 "coef": combicoefs.values[index]
    #                             }
    #                         )
    #                     if subjectnames.values[index] != "None":
    #                         #print(subjectnames.values[index])
    #                         stop_iteration = True

    #                     index += 1
    #                     ## If there is a subject in the combi section one line lower and no new main subject at this line, redo the process but 1 line lower
    #                     #if combinames.values[temp_index+1] != "None" and subjectnames.values[temp_index+1] == "None":
    #                         #temp_index += 1
                        
    #                     ## If there is no combi subject below or if a new main subject started (which means that the combi subjects belong to the new main subject and no longer to this one)
    #                     #if combinames.values[temp_index+1] == "None" or subjectnames.values[temp_index+1] != "None":
    #                         #print(combis)
    #                         #print(combinames.values[temp_index+1], subjectnames.values[temp_index+1])
    #                         #stop_iteration = True

                
    #             print(combis)
    #             #if len(combis) > 0:
    #                 #json_data.append(combis)

    #             subject["name"] = subjectnames.values[index]
    #             subject["lessons"] = subjectlessons.values[index]
    #             subject["coef"] = coefficient
    #             subject["subsubjects"] = combis

    #             subjects.append(subject)





        ## Increase the current index after one block has been converted to get to the next block
        #current_index += 1


    #with open("output/out.json", "w", encoding="utf-8") as _file:
        #json.dump(json_data, _file, ensure_ascii=False)
    #print(json_data)


def get_combis(temp_combis, combinames, combicoefs, index:int) -> list[dict, dict]:
    temp_combis.append(
        {
            "name": combinames.values[index],
            "coef": combicoefs.values[index]
        }
    )

    if combinames.values[index+1] != "None":
        get_combis(temp_combis, combinames, combicoefs, index)





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

