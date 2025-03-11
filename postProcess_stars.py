import pandas as pd
import os, re, json
from utils.utils import setupLogger

def mergeJsonDataIntoStudentCoverLetter(jsonDir, inputFileStudentCoverLetter, outputFileName):
    # read the student cover letter data
    df_student = pd.read_excel(inputFileStudentCoverLetter)
    
    # Ensure Record ID is integer type
    if "Record ID" in df_student.columns:
        df_student["Record ID"] = pd.to_numeric(df_student["Record ID"], errors='coerce').astype('Int64')
        logger.info(f"Converted Record ID column to integer type. Available IDs: {df_student['Record ID'].tolist()}")
    else:
        logger.error("Record ID column not found in the input Excel file")
        return df_student

    # iteratre over each json file in the jsonDir
    for file in os.listdir(jsonDir):
        try:
            # get record ID from json file name *_<Record ID>.json
            recordID = int(re.search(r'(_)(\d+)(.json)', file).group(2))
            logger.info(f"Processing file {file} with Record ID: {recordID}")

            # Check if record ID exists in DataFrame
            if recordID not in df_student["Record ID"].values:
                logger.error(f"Record ID {recordID} not found in Excel file")
                continue

            # read the json data as a dictionary
            with open(os.path.join(jsonDir, file), 'r') as f:
                try:
                    json_data = json.load(f)
                except json.JSONDecodeError as e:
                    logger.error(f"Error parsing JSON file {file}: {str(e)}")
                    continue

            # Skip if json_data is an error message
            if isinstance(json_data, dict) and 'error' in json_data:
                logger.error(f"Error in JSON data for file {file}: {json_data['error']}")
                continue

            # get the evaluation data from the json data
            try:
                evaluation = json_data["response"]["evaluation"]
                # add the evaluation data to the student cover letter data using loc
                mask = df_student["Record ID"] == recordID
                df_student.loc[mask, "Motivation"] = evaluation["passion"]["motivation_for_scientific_research"]["score"]
                df_student.loc[mask, "Initiative"] = evaluation["passion"]["initiative"]["score"]
                df_student.loc[mask, "Program Expectations"] = evaluation["clarity_of_purpose"]["program_expectations_and_benefits"]["score"]
                df_student.loc[mask, "Future Alignment"] = evaluation["clarity_of_purpose"]["alignment_with_future_endeavors_and_career_direction"]["score"]
                df_student.loc[mask, "Motivation Rationale"] = evaluation["passion"]["motivation_for_scientific_research"]["rationale"]
                df_student.loc[mask, "Initiative Rationale"] = evaluation["passion"]["initiative"]["rationale"]
                df_student.loc[mask, "Program Expectations Rationale"] = evaluation["clarity_of_purpose"]["program_expectations_and_benefits"]["rationale"]
                df_student.loc[mask, "Future Alignment Rationale"] = evaluation["clarity_of_purpose"]["alignment_with_future_endeavors_and_career_direction"]["rationale"]
                

                # get the stars track choice data from the json data
                stars_track_choice = json_data["response"]["stars_track_choice"]

                # add the stars track choice data to the student cover letter data
                df_student.loc[mask, "Stars Track Choice"] = stars_track_choice["track"]
                df_student.loc[mask, "Stars Track Rationale"] = stars_track_choice["rationale"]
                
                logger.info(f"Successfully processed file {file}")
            except KeyError as e:
                logger.error(f"Missing key in JSON data for file {file}: {str(e)}")
                continue
        except Exception as e:
            logger.error(f"Unexpected error processing file {file}: {str(e)}")
            continue

    return df_student

def addTotalScore(df_student):
    # add the total score to the student cover letter data right after rationale columns
    df_student.insert(df_student.columns.get_loc("Future Alignment Rationale") + 1, "Total Score", df_student[["Motivation", "Initiative", "Program Expectations", "Future Alignment"]].sum(axis=1))
    # sort by total score descending
    df_student = df_student.sort_values(by="Total Score", ascending=False)
    return df_student

if __name__ == "__main__":
    # User variables
    inputFileStudentCoverLetter = "euroOutputs/cover_letters_temp.xlsx"
    inputFileLLMOutput = "euroOutputs/combined_results.xlsx"
    # inputFileStudentData = "euroOutputs/High Priority Pool.xlsx"
    jsonDir = "euroOutputs/jsonOutputs"
    outputFileName = "STARS25-Evaluation-Details.xlsx"
    logFileName = "postProcess_stars.log"
    outputDir = "euroOutputs"
    
    # Setup logging
    logger = setupLogger(outputDir, logFileName)

    # populate json data into the student cover letter data
    df_student = mergeJsonDataIntoStudentCoverLetter(jsonDir, inputFileStudentCoverLetter, outputFileName)

    # add the total score to the student cover letter data
    df_student = addTotalScore(df_student)

    # save the merged data
    df_student.to_excel(os.path.join(outputDir, outputFileName), index=False)
