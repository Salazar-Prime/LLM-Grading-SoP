"""
This script merges the original High Priority Pool data with the evaluation results
from the combined_results.xlsx file, matching records based on guid.
"""

import pandas as pd
import os


def merge_evaluation_results():
    # Read the original High Priority Pool file
    original_df = pd.read_csv("High Priority Pool.csv", encoding="utf-8")

    # Read the combined results file
    # results_df = pd.read_excel("euroOutputs/combined_results.xlsx")
    # results_df = pd.read_excel("euroOutputs/combined_results_gpt-5.2.xlsx")
    results_df = pd.read_excel("euroOutputs/combined_results-gpt52-mini.xlsx")

    # Score columns for calculating total
    score_columns = [
        "score_motivation",
        "score_initiative",
        "score_program_expectations",
        "score_future_alignment",
        "score_learning_reflection",
        "score_problem_solving",
    ]

    # Columns to copy from results_df
    columns_to_copy = [
        "cleaned_sop",
        "word_count",
        "skipped",
        "model",  # E
        "score_motivation",  # F
        "score_initiative",  # G
        "score_program_expectations",  # H
        "score_future_alignment",  # I
        "score_learning_reflection",  # J
        "score_problem_solving",  # K
        "rationale_motivation",  # L
        "rationale_initiative",  # M
        "rationale_program_expectations",  # N
        "rationale_future_alignment",  # O
        "rationale_learning_reflection",  # P
        "rationale_problem_solving",  # Q
    ]

    # Merge the dataframes based on guid
    merged_df = pd.merge(
        original_df, results_df[["guid"] + columns_to_copy], on="guid", how="left"
    )

    # Calculate total score
    merged_df["total_score"] = merged_df[score_columns].sum(axis=1)

    # Reorder columns to insert new columns after column C
    cols = list(merged_df.columns)
    # Get all columns up to and including column C
    base_cols = cols[:3]

    # Define the final order of new columns
    new_cols = [
        "guid",
        "cleaned_sop",
        "word_count",
        "skipped",
        "model",
        "score_motivation",
        "score_initiative",
        "score_program_expectations",
        "score_future_alignment",
        "score_learning_reflection",
        "score_problem_solving",
        "total_score",  # Insert total_score after individual scores
        "rationale_motivation",
        "rationale_initiative",
        "rationale_program_expectations",
        "rationale_future_alignment",
        "rationale_learning_reflection",
        "rationale_problem_solving",
    ]

    # Get remaining columns from original file (excluding the ones we just added)
    remaining_cols = [col for col in cols[3:] if col not in new_cols + ["guid"]]

    # Reorder columns
    final_cols = base_cols + new_cols + remaining_cols
    merged_df = merged_df[final_cols]

    # Save the merged results
    output_file = "outputs/High Priority Pool - Graded.xlsx"
    merged_df.to_excel(output_file, index=False)
    print(f"Merged results saved to {output_file}")

    # Print some statistics
    print(f"\nMerge Statistics:")
    print(f"Original records: {len(original_df)}")
    print(f"Evaluated records: {len(results_df)}")
    print(f"Successfully merged records: {len(merged_df[merged_df['model'].notna()])}")
    print(f"Records without evaluations: {len(merged_df[merged_df['model'].isna()])}")


if __name__ == "__main__":
    merge_evaluation_results()
