# STARS Application Review System

This guide explains how to use the STARS application review system, which processes and evaluates student cover letters using a series of Python scripts and LLM-based analysis.

## System Requirements

- Python 3.x
- Required Python packages:
  - pdfplumber
  - pandas
  - reportlab
  - openai (for LLM processing)

## Workflow Overview

The system consists of four main scripts that should be run in sequence:

1. PDF Preprocessing (`preProcessPDF__stars.py`)
2. LLM Processing (`processLLM_stars.py`)
3. Post Processing (`postProcess_stars.py`)
4. PDF Report Generation (`pdfReport__stars.py`)

## Detailed Usage Guide

### 1. PDF Preprocessing (`preProcessPDF__stars.py`)

This script processes the raw PDF cover letters and extracts their text content.

**Input**: 
- PDF files in the format: "Cover Letter - {Student Name} - Record ID {Record ID}.pdf"

**Configuration**:
```python
inputDir = "/path/to/cover/letter/files"
outputFileName = "cover_letters_temp.xlsx"
outputDir = "euroOutputs"
```

**Output**:
- Excel file containing extracted text and metadata from PDFs
- Includes: Record ID, Student Name, Text, Page Count, Word Count, Character Count

### 2. LLM Processing (`processLLM_stars.py`)

This script handles the OpenAI API processing of the cleaned cover letter data.

**Input**:
- Excel file generated from the preprocessing step
- JSON schema file for evaluation structure
- System prompt file for LLM instructions

**Configuration**:
```python
INPUT_FILE = "euroOutputs/cover_letters_temp.xlsx"
OUTPUT_DIR = "euroOutputs"
OUTPUT_FILE = "combined_results.xlsx"
model = "gpt-4" # or your preferred OpenAI model
PROMPT_FILE = "systemPromptStars_v2.txt"
```

**Output**:
- Individual JSON files for each evaluation
- Combined Excel file with all evaluations

### 3. Post Processing (`postProcess_stars.py`)

This script merges the LLM evaluation data with the original student information and calculates total scores.

**Input**:
- Original cover letter Excel file
- LLM output JSON files
- Combined results Excel file

**Configuration**:
```python
inputFileStudentCoverLetter = "euroOutputs/cover_letters_temp.xlsx"
jsonDir = "euroOutputs/jsonOutputs"
outputFileName = "STARS25-Evaluation-Details.xlsx"
```

**Output**:
- Consolidated Excel file with all evaluation details and total scores

### 4. PDF Report Generation (`pdfReport__stars.py`)

This script generates a professional PDF report containing all evaluations.

**Input**:
- Final evaluation Excel file from post-processing

**Configuration**:
```python
inputFile = "euroOutputs/STARS25-Evaluation-Details.xlsx"
outputDir = "euroOutputs/pdf_reports"
outputFileName = "STARS25-EvaluationReport.pdf"
authorName = "YOUR_NAME"
reportTitle = "STARS 2025"
reportSubtitle = "Student Evaluation Report"
```

**Output**:
- Professional PDF report with:
  - Title page
  - Table of contents
  - Individual student evaluations
  - Cover letter text
  - STARS track recommendations
  - Detailed scoring and rationales

## Directory Structure

```
project_root/
├── euroOutputs/
│   ├── cover_letters_temp.xlsx
│   ├── combined_results.xlsx
│   ├── STARS25-Evaluation-Details.xlsx
│   ├── jsonOutputs/
│   └── pdf_reports/
├── preProcessPDF__stars.py
├── processLLM_stars.py
├── postProcess_stars.py
├── pdfReport__stars.py
└── systemPromptStars_v2.txt
```

## Running the Pipeline

1. Place all cover letter PDFs in the input directory
2. Run the scripts in sequence:
```bash
python preProcessPDF__stars.py
python processLLM_stars.py
python postProcess_stars.py
python pdfReport__stars.py
```

## Error Handling

- Each script includes logging functionality
- Log files are created in the `euroOutputs` directory
- Check respective log files for any issues during processing:
  - `preProcessPDF__stars.log`
  - `processLLM_stars.log`
  - `postProcess_stars.log`

## Notes

- Ensure you have proper OpenAI API credentials configured
- Monitor API usage when processing large batches
- Keep backup copies of original files
- Review the generated PDF report for quality assurance 