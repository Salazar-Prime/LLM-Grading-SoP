"""
This script handles the data cleaning process for SoP entries.
It reads the excel file, cleans the statements of purpose, and saves the cleaned data
to a new excel file. This is meant to be run separately from the main OpenAI processing.
"""

import pandas as pd
from utils.cleanString import cleanString, getInstructionInJson
import os
from utils.utils import setupLogger


def clean_sop_data(input_file, instruction_file, output_file):
    # Setup logging
    logger = setupLogger("euroOutputs", "clean_data.log")

    # Read instructions
    jsonInstructions = getInstructionInJson(instruction_file)

    # Read input excel file
    df = pd.read_csv(input_file, encoding="utf-8")

    # Initialize output dataframe
    columns = [
        "first_name",
        "last_name",
        "guid",
        "original_sop",
        "cleaned_sop",
        "word_count",
        "logs",
        "skipped",
    ]
    cleanedData = pd.DataFrame(columns=columns)

    # Process each row
    for index, row in df.iterrows():
        try:
            SoP = row["statement_of_purpose"]

            # Clean the statement
            cleaned_sop, word_count, logs = cleanString(SoP, jsonInstructions)

            # Determine if entry should be skipped (word count > 1000)
            skipped = word_count > 1500

            # Create new row
            new_row = {
                "first_name": row["first_name"],
                "last_name": row["last_name"],
                "guid": row["guid"],
                "original_sop": SoP,
                "cleaned_sop": cleaned_sop,
                "word_count": word_count,
                "logs": logs,
                "skipped": skipped,
            }

            # Add to cleaned data
            cleanedData.loc[len(cleanedData)] = new_row

            # Print and log progress
            logger.info(
                f"Processed row {index}: {row['first_name']} {row['last_name']}"
            )
            logger.info(f"Word count: {word_count}")
            if logs:
                logger.info("Cleaning logs:", logs)
            logger.info("-" * 50)

        except Exception as e:
            logger.error(f"Error processing row {index}: {str(e)}")

    # Save to excel
    os.makedirs("euroOutputs", exist_ok=True)
    cleanedData.to_excel(os.path.join("euroOutputs", output_file), index=False)
    logger.info(f"\nCleaning complete. Results saved to {output_file}")

    # Print summary
    total_processed = len(cleanedData)
    skipped_entries = len(cleanedData[cleanedData["skipped"]])
    logger.info(f"\nSummary:")
    logger.info(f"Total entries processed: {total_processed}")
    logger.info(f"Entries marked for review (>1500 words): {skipped_entries}")


if __name__ == "__main__":
    INPUT_FILE = "High Priority Pool.csv"
    INSTRUCTION_FILE = "instrucitonSoP.txt"
    OUTPUT_FILE = "cleanedData.xlsx"

    clean_sop_data(INPUT_FILE, INSTRUCTION_FILE, OUTPUT_FILE)
