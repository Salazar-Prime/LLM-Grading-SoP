"""
This script handles the data cleaning process for SoP entries.
It reads the excel file, cleans the statements of purpose, and saves the cleaned data
to a new excel file. This is meant to be run separately from the main OpenAI processing.
"""

import pandas as pd
from utils.cleanString import cleanString, getInstructionInJson


def clean_sop_data(input_file, instruction_file, output_file):
    # Read instructions
    jsonInstructions = getInstructionInJson(instruction_file)

    # Read input excel file
    df = pd.read_excel(input_file)

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
            skipped = word_count > 1000

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

            # Print progress
            print(f"Processed row {index}: {row['first_name']} {row['last_name']}")
            print(f"Word count: {word_count}")
            if logs:
                print("Cleaning logs:", logs)
            print("-" * 50)

        except Exception as e:
            print(f"Error processing row {index}: {str(e)}")

    # Save to excel
    cleanedData.to_excel(output_file, index=False)
    print(f"\nCleaning complete. Results saved to {output_file}")

    # Print summary
    total_processed = len(cleanedData)
    skipped_entries = len(cleanedData[cleanedData["skipped"]])
    print(f"\nSummary:")
    print(f"Total entries processed: {total_processed}")
    print(f"Entries marked for review (>1000 words): {skipped_entries}")


if __name__ == "__main__":
    INPUT_FILE = "High Priority Pool.xlsx"
    INSTRUCTION_FILE = "instrucitonSoP.txt"
    OUTPUT_FILE = "cleanedData.xlsx"

    clean_sop_data(INPUT_FILE, INSTRUCTION_FILE, OUTPUT_FILE)
