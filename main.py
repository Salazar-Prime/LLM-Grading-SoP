"""
This script handles the OpenAI API processing of cleaned SoP data.
It reads the cleaned data from the excel file and sends it to OpenAI API for evaluation.
"""

import pandas as pd
from utils.openaiApi import getResponse
import json
import os
from utils.utils import setupLogger


def load_json_schema():
    with open("jsonSchema.json", "r") as file:
        return json.load(file)


def mergeResponseWithOriginalData(response, row, originalFileDF, model):
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
        ]["score"],
        "score_learning_reflection": evaluation["resilience"][
            "reflection_on_learning_through_experience"
        ]["score"],
        "score_problem_solving": evaluation["resilience"]["problem_solving"]["score"],
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
        "rationale_learning_reflection": evaluation["resilience"][
            "reflection_on_learning_through_experience"
        ]["rationale"],
        "rationale_problem_solving": evaluation["resilience"]["problem_solving"][
            "rationale"
        ],
    }

    # Update the original DataFrame with new columns
    for column, value in {**scores, **rationales}.items():
        originalFileDF.at[row_index, column] = value

    return originalFileDF


def process_cleaned_data(
    input_file, json_schema, model, start_index=0, max_entries=None
):
    # Create output directory if it doesn't exist
    os.makedirs("euroOutputs", exist_ok=True)
    os.makedirs("euroOutputs/jsonOutputs", exist_ok=True)

    # Check if combined results already exist
    combined_output = os.path.join("euroOutputs", "combined_results.xlsx")
    if os.path.exists(combined_output):
        # Load existing combined results to preserve previous data
        combined_df = pd.read_excel(combined_output)
        df = pd.read_excel(input_file)  # Still need original for iteration
        logger.info(f"Loaded existing combined results from {combined_output}")
    else:
        # Read the cleaned data and create new combined_df
        df = pd.read_excel(input_file)
        combined_df = df.copy()
        logger.info("No existing combined results found, creating new DataFrame")

    end_index = min(start_index + max_entries, len(df))

    # Counter for tracking processed entries
    processed_count = 0

    # Process entries within the specified range
    for index, row in df.iloc[start_index:end_index].iterrows():
        logger.info(f"Processing {row['first_name']} {row['last_name']}")

        try:
            # Get response from OpenAI
            response = getResponse(row["cleaned_sop"], json_schema, model=model)

            guid = row["guid"].replace("/", "_")
            # Save the individual response as JSON
            output_filename = os.path.join(
                "euroOutputs",
                "jsonOutputs",
                f"{row['first_name']}_{row['last_name']}_{guid}.json",
            )
            with open(output_filename, "w") as f:
                json.dump(response, f, indent=4)

            # print out the summary line with score in each category and add it some logs that will be saved as a file
            summary_line = f"{row['first_name']} {row['last_name']} - {response['response']['evaluation']['passion']['motivation_for_scientific_research']['score']} - {response['response']['evaluation']['passion']['initiative']['score']} - {response['response']['evaluation']['clarity_of_purpose']['program_expectations_and_benefits']['score']} - {response['response']['evaluation']['clarity_of_purpose']['alignment_with_future_endeavors_and_career_direction']['score']} - {response['response']['evaluation']['resilience']['reflection_on_learning_through_experience']['score']} - {response['response']['evaluation']['resilience']['problem_solving']['score']}"
            logger.info(summary_line)

            # Merge response with original data
            combined_df = mergeResponseWithOriginalData(
                response, row, combined_df, model
            )

            logger.info(f"Response saved to {output_filename}")

            # Increment processed count
            processed_count += 1

            # Save intermittently every 10 entries
            if processed_count % 10 == 0:
                combined_output = os.path.join("euroOutputs", "combined_results.xlsx")
                combined_df.to_excel(combined_output, index=False)
                logger.info(
                    f"Intermediate results saved after processing {processed_count} entries"
                )

        except Exception as e:
            logger.error(
                f"Error processing {row['first_name']} {row['last_name']}: {e}"
            )

    # Save the final combined results to an Excel file
    combined_output = os.path.join("euroOutputs", "combined_results.xlsx")
    combined_df.to_excel(combined_output, index=False)
    logger.info(f"Final combined results saved to {combined_output}")

    logger.info(
        f"Processed {end_index - start_index} entries from index {start_index} to {end_index}"
    )


if __name__ == "__main__":
    INPUT_FILE = "euroOutputs/cleanedData.xlsx"
    model = "gpt-4o"
    logger = setupLogger("euroOutputs", "process_cleaned_data.log")
    logger.info(f"Processing {INPUT_FILE} with model {model}")
    try:
        json_schema = load_json_schema()
        logger.info("JSON schema loaded successfully")
    except Exception as e:
        logger.error(f"Error loading JSON schema: {e}")
        raise

    # Default to processing first 100 entries
    process_cleaned_data(
        INPUT_FILE,
        json_schema,
        model,
        start_index=0,
        max_entries=3,
    )
