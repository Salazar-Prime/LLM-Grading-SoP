# SoP Grading System

This repository describes the process of using LLM for grading Statements of Purpose (SoP) using a comprehensive rubric-based evaluation approach. The system follows four main steps to process and evaluate each SoP.

## Project Overview

The SoP Grading System is a comprehensive tool for evaluating student statements of purpose using advanced language models and a detailed rubric-based approach.

## Prerequisites

### System Requirements

- Python 3.8+
- pip package manager

### Installation

1. Clone the repository:

   ```bash
   git clone https://github.com/salazar-prime/sop-grading-system.git
   cd sop-grading-system
   ```
2. Create a virtual environment (recommended):

   ```bash
   conda create -n sop-grading-system python=3.8
   conda activate sop-grading-system
   ```
3. Install dependencies:

   ```bash
   pip install -r requirements.txt
   ```

## Dependencies Breakdown

The `requirements.txt` file includes the following key libraries:

- `pandas`: Data manipulation and analysis
- `openai`: OpenAI API integration for LLM evaluation
- `python-dotenv`: Environment variable management
- `fuzzywuzzy`: Fuzzy string matching
- `python-Levenshtein`: String distance calculations
- `reportlab`: PDF report generation
- `tiktoken`: Token counting for OpenAI models
- `matplotlib`: Data visualization

## Utility Files

### Word and Token Visualization

`utils/visualizeWordToken.py` provides a utility for analyzing input data:

- Creates histograms of word and token counts in Statements of Purpose
- Uses `matplotlib` for visualization
- Supports token counting with `tiktoken`

#### Usage

```python
from utils.visualizeWordToken import createHistogram
createHistogram(dataframe)  # Generates word and token count histograms
```

## Step 1: Data Cleaning and Preprocessing

The first step involves cleaning and preprocessing the raw SoP data:

- Removing special characters and formatting
- Removing SoP instructions if present in the text (Fuzzy string matching)
- Standardizing text format
- Extracting relevant information (Student Name, GUID, etc.)
- Preparing the text for evaluation

Key files:

- `clean_data.py`: Main script for data cleaning
- `utils/cleanString.py`: Utility functions for text preprocessing
- `instructions.txt`: SoP instructions to be removed from the text

## Step 2: LLM-Based Evaluation

The system uses an LLM model to evaluate each SoP based on a detailed rubric with six main categories. The rubric is defined in `systemPromptv2.txt`.

1. **Passion**

   - Motivation for Scientific Research (0-3 points)
   - Initiative (0-3 points)
2. **Clarity of Purpose**

   - Program Expectations and Benefits (0-3 points)
   - Alignment with Future Endeavors (0-3 points)
3. **Resilience**

   - Learning Reflection (0-3 points)
   - Problem Solving (0-3 points)

Each category is scored on a scale of 0-3, with detailed rationales provided for each score.

Key files:

- `main.py`: Main evaluation script
- `utils/openaiApi.py`: API integration for AI evaluation
- `systemPromptv2.txt`: Evaluation instructions and rubric

## Step 3: Results Processing

After evaluation, the results are processed and organized:

- Individual JSON outputs for each student
- Combined results in Excel format
- Score calculations and statistics

Key files:

- `postProcess.py`: Script for processing evaluation results
- `outputs/jsonOutputs/`: Directory containing individual evaluation results
- `combined_results.xlsx`: Consolidated evaluation data

## Step 4: Report Generation

The final step generates comprehensive reports:

- Individual PDF reports for each student
- Evaluation summaries
- Detailed feedback and rationales

Key files:

- `createPDFReport.py`: Script for generating PDF reports
- `outputs/pdf_reports/`: Directory containing generated reports

## Usage

1. Place raw SoP files in the input directory
2. Run the cleaning script:
   ```bash
   python clean_data.py
   ```
3. Execute the LLM-based evaluation:
   ```bash
   python main.py
   ```
4. Process results:
   ```bash
   python postProcess.py
   ```
5. Generate reports:
   ```bash
   python createPDFReport.py
   ```

## Output Format

The system generates several types of outputs:

1. Individual JSON files containing detailed evaluations
2. Excel spreadsheet with combined results
3. PDF reports with:
   - Original SoP text
   - Scores for each category
   - Detailed rationales
   - Overall evaluation summary

## Development and Contribution

### Developers

- **Lead Developer**: [varun Aggarwal]
- **Rubric Contributors**:
  - [Kay Kobak]
  - [Parth Kelkar]

## License

[Specify License - e.g., MIT, Apache 2.0]

## Contact

- **Email**: [aggarw82@purdue.edu]
- **Project Link**: [https://github.com/salazar-prime/sop-grading-system]

## Acknowledgments

- OpenAI for GPT models
- Purdue University EURO Office for providing the data and securing the funding
