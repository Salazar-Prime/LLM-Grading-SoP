"""
This script handles the OpenAI API processing of cleaned SoP data.
It reads the cleaned data from the excel file and sends it to OpenAI API for evaluation.
"""

import pandas as pd
from utils.openaiApi import getResponse
import json
import os
import logging
from utils.utils import setupLogger


def load_json_schema():
    with open("jsonSchema.json", "r") as file:
        return json.load(file)


def mergeResponseWithOriginalData(response, row, originalFileDF, model, stars_track_choice):
    # Get the index of the current row in the original DataFrame
    row_index = row.name

    # Extract scores and rationales from the response
    evaluation = response["response"]["evaluation"]

    # Extract all scores and rationales
    scores = {
        "model": model,  # Add model name as a column
        "score_motivation": evaluation["passion"]["motivation_for_scientific_research"][
            "score"
        ],
        "score_initiative": evaluation["passion"]["initiative"]["score"],
        "score_program_expectations": evaluation["clarity_of_purpose"][
            "program_expectations_and_benefits"
        ]["score"],
        "score_future_alignment": evaluation["clarity_of_purpose"][
            "alignment_with_future_endeavors_and_career_direction"
        ]["score"]
    }

    rationales = {
        "rationale_motivation": evaluation["passion"][
            "motivation_for_scientific_research"
        ]["rationale"],
        "rationale_initiative": evaluation["passion"]["initiative"]["rationale"],
        "rationale_program_expectations": evaluation["clarity_of_purpose"][
            "program_expectations_and_benefits"
        ]["rationale"],
        "rationale_future_alignment": evaluation["clarity_of_purpose"][
            "alignment_with_future_endeavors_and_career_direction"
        ]["rationale"],
        }

    # Update the original DataFrame with new columns
    for column, value in {**scores, **rationales}.items():
        originalFileDF.at[row_index, column] = value

    originalFileDF.at[row_index, "stars_track_choice"] = stars_track_choice["track"]
    originalFileDF.at[row_index, "rationale_stars_track_choice"] = stars_track_choice["rationale"]

    return originalFileDF


def process_cleaned_data(
    input_file, outputDir, json_schema, model, start_index=0, max_entries=None, logger=None, prompt_file=None, output_file=None
):
    if logger is None:
        logger = logging.getLogger(__name__)

    # Read the cleaned data
    logger.info(f"Reading data from {input_file}")
    df = pd.read_excel(input_file)
    end_index = min(start_index + max_entries, len(df)) if max_entries else len(df)
    logger.info(f"Processing entries from index {start_index} to {end_index}")

    # Create output directory if it doesn't exist
    os.makedirs(outputDir, exist_ok=True)
    os.makedirs(outputDir + "/jsonOutputs", exist_ok=True)
    logger.info(f"Created output directories in {outputDir}")

    # Create a copy of the original DataFrame to store combined results
    combined_df = df.copy()

    # Counter for tracking processed entries
    processed_count = 0

    # Process entries within the specified range
    for index, row in df.iloc[start_index:end_index].iterrows():
        logger.info(f"Processing entry for student: {row['Student Name']}")

        try:
            # Get response from OpenAI
            logger.info(f"Sending request to OpenAI API for {row['Student Name']}")
            response = getResponse(row["Text"], json_schema, model=model, prompt_file=prompt_file)

            recordID = row["Record ID"]
            # Save the individual response as JSON
            output_filename = os.path.join(
                outputDir,
                "jsonOutputs",
                f"{row['Student Name']}_{recordID}.json",
            )
            with open(output_filename, "w") as f:
                json.dump(response, f, indent=4)

            # Log scores for each category
            evaluation = response['response']['evaluation']
            logger.info(
                f"Scores for {row['Student Name']}: "
                f"Motivation: {evaluation['passion']['motivation_for_scientific_research']['score']}, "
                f"Initiative: {evaluation['passion']['initiative']['score']}, "
                f"Program Expectations: {evaluation['clarity_of_purpose']['program_expectations_and_benefits']['score']}, "
                f"Future Alignment: {evaluation['clarity_of_purpose']['alignment_with_future_endeavors_and_career_direction']['score']}"
            )
            stars_track_choice = response['response']['stars_track_choice']
            logger.info(f"Stars Track Choice: {stars_track_choice['track']}")

            # Merge response with original data
            combined_df = mergeResponseWithOriginalData(
                response, row, combined_df, model, stars_track_choice
            )

            logger.info(f"Response saved to {output_filename}")

            # Increment processed count
            processed_count += 1

            # Save intermittently every 10 entries
            if processed_count % 10 == 0:
                combined_output = os.path.join(outputDir, output_file)
                combined_df.to_excel(combined_output, index=False)
                logger.info(
                    f"Intermediate results saved after processing {processed_count} entries"
                )

        except Exception as e:
            logger.error(f"Error processing {row['Student Name']}: {str(e)}")

    # Save the final combined results to an Excel file
    combined_output = os.path.join(outputDir, output_file)
    combined_df.to_excel(combined_output, index=False)
    logger.info(f"Final combined results saved to {combined_output}")

    logger.info(
        f"Successfully processed {processed_count} entries from index {start_index} to {end_index}"
    )


if __name__ == "__main__":
    # User variables
    # INPUT_FILE = "euroOutputs/cover_letters_temp.xlsx"
    INPUT_FILE = "euroOutputs/cover_letters_march26.xlsx"
    OUTPUT_DIR = "euroOutputs"
    OUTPUT_FILE = "combined_results_march26.xlsx"
    model = "gpt-4o"
    continueWithLastFile = False
    LOG_FILE = "processLLM_stars_march26.log"
    PROMPT_FILE = "systemPromptStars_v2.txt"

    # Setup logging
    logger = setupLogger(OUTPUT_DIR, LOG_FILE, continueWithLastFile=continueWithLastFile)
    
    try:
        json_schema = load_json_schema()
        logger.info("JSON schema loaded successfully")

        # Default to processing first 100 entries
        process_cleaned_data(
            INPUT_FILE,
            OUTPUT_DIR,
            json_schema,
            model,
            start_index=0,
            max_entries=22,
            logger=logger,
            prompt_file=PROMPT_FILE,
            output_file=OUTPUT_FILE
        )
    except Exception as e:
        logger.error(f"Error in main execution: {str(e)}")
        raise
