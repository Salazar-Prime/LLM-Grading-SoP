import os
import logging
import re
import time
from logging.handlers import RotatingFileHandler

def cleanTextForExcel(text):
    """
    Clean text to remove characters that Excel cannot handle
    
    Args:
        text (str): Text to clean
    
    Returns:
        str: Cleaned text
    """
    if not isinstance(text, str):
        return text
        
    # Remove or replace problematic characters
    # Remove null bytes
    text = text.replace('\x00', '')
    
    # Replace other common problematic characters
    text = re.sub(r'[\x00-\x08\x0B\x0C\x0E-\x1F\x7F-\x9F]', '', text)
    
    # Replace specific Unicode characters that often cause issues
    text = text.replace('\u2028', ' ').replace('\u2029', ' ')
    
    # Replace multiple spaces with single space
    text = ' '.join(text.split())
    
    return text

def setupLogger(outputDir, logFileName='processing.log', continueWithLastFile=False):
    """
    Set up logging configuration for both file and console output
    
    Args:
        outputDir (str): Directory where log files will be stored
        logFileName (str): Name of the log file
        continueWithLastFile (bool): If True, append to existing log file instead of rotating it
    
    Returns:
        logger: Configured logger instance
    """
    # Create output directory if it doesn't exist
    os.makedirs(outputDir, exist_ok=True)

    # Get logger instance
    logger = logging.getLogger(__name__)
    
    # Remove any existing handlers
    if logger.hasHandlers():
        logger.handlers.clear()
    
    # Set logging level
    logger.setLevel(logging.INFO)

    # Create formatters and handlers
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

    # File handler (with rotation)
    logPath = os.path.join(outputDir, logFileName)
    
    # If log file exists and we don't want to continue with it, rotate it
    if os.path.exists(logPath) and not continueWithLastFile:
        try:
            # Rename existing log file with timestamp
            timestamp = os.path.getmtime(logPath)
            timeStr = time.strftime('%Y%m%d_%H%M%S', time.localtime(timestamp))
            os.rename(logPath, f"{logPath}.{timeStr}")
        except Exception as e:
            print(f"Warning: Could not rotate existing log file: {e}")

    # Set file mode based on continueWithLastFile flag
    fileMode = 'a' if continueWithLastFile else 'w'
    
    fileHandler = RotatingFileHandler(
        logPath,
        maxBytes=1024*1024,  # 1MB
        backupCount=5,
        mode=fileMode  # 'a' for append if continuing, 'w' for write if starting fresh
    )
    fileHandler.setFormatter(formatter)

    # Console handler
    consoleHandler = logging.StreamHandler()
    consoleHandler.setFormatter(formatter)

    # Add both handlers to the logger
    logger.addHandler(fileHandler)
    logger.addHandler(consoleHandler)

    # Log a separator if continuing with existing file
    if continueWithLastFile and os.path.exists(logPath):
        logger.info("-" * 80)
        logger.info("Continuing logging in existing file")
        logger.info(f"Timestamp: {time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())}")
        logger.info("-" * 80)

    return logger 