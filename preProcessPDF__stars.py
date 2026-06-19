import os, re
import pdfplumber
import pandas as pd
import logging
from utils.utils import setupLogger, cleanTextForExcel


def readPDF(pdfFilePath):
    with pdfplumber.open(pdfFilePath) as pdf:
        pdfText = ""
        # extract text of each page
        for page in pdf.pages:
            pdfText += page.extract_text() + "\n"
        
        # return word count, character Count, number of pages, text
        return len(pdfText.split()), len(pdfText), len(pdf.pages), pdfText


def getPDF(pdfFolderPath, fileLimit=None, logger=None):
    if logger is None:
        logger = logging.getLogger(__name__)
        
    # Initialize an empty list to store PDF file paths
    pdfFiles = []
    df = pd.DataFrame(columns=["Record ID", "Student Name", "Text", "Page Count", "Word Count", "Character Count"])

    # Iterate through all files in the folder
    for file in os.listdir(pdfFolderPath):
        # Check if the file is a PDF
        if file.endswith('.pdf'):
            pdfFiles.append(file)
    
    if fileLimit is None:
        fileLimit = len(pdfFiles)

    # get Student Name and Record ID from the PDF file name
    for file in pdfFiles[:fileLimit]:
        # Extract student name and record ID from the file name
        # EG: "Cover Letter - <Student Name> - Record ID <Record ID>.pdf"
        search = re.search(r'Cover Letter - (.*) - Record ID (\d+)', file)
        if search:
            studentName = search.group(1)
            recordID = search.group(2)
            logger.info(f"Student Name: {studentName}, Record ID: {recordID}")
        else:
            logger.warning(f"No student name or record ID found in file: {file}")
    
        wordCount, charCount, pageCount, pdfText = readPDF(os.path.join(pdfFolderPath, file))
        logger.info(f"Word Count: {wordCount}, Character Count: {charCount}, Page Count: {pageCount}")

        # Clean the text before adding to DataFrame
        cleanedText = cleanTextForExcel(pdfText)

        # Create a new row as a DataFrame and concatenate with the existing DataFrame
        newRow = pd.DataFrame({
            "Record ID": [recordID], 
            "Student Name": [studentName], 
            "Text": [cleanedText], 
            "Page Count": [pageCount], 
            "Word Count": [wordCount], 
            "Character Count": [charCount]
        })
        df = pd.concat([df, newRow], ignore_index=True)

    return df


if __name__ == "__main__":
    # User variables
    inputDir = "/Users/varun/Downloads/Cover Letter Files - March 26 (22 new applications)"
    outputFileName = "cover_letters_march26.xlsx"
    logFileName = "preProcessPDF__stars_march26.log"
    outputDir = "euroOutputs"
    
    # Setup logging
    logger = setupLogger(outputDir, logFileName)
    
    try:
        # Process PDFs
        df = getPDF(inputDir, fileLimit=None, logger=logger)
        
        # Clean all text columns before saving
        for column in df.select_dtypes(include=['object']).columns:
            df[column] = df[column].apply(cleanTextForExcel)
        
        # save to excel
        df.to_excel(os.path.join(outputDir, outputFileName), index=False)
        logger.info(f"Successfully saved data to {outputFileName}")
    except Exception as e:
        logger.error(f"Error processing PDFs: {str(e)}")
        raise
