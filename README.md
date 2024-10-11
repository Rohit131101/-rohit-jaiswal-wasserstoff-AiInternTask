# PDF Processing Pipeline

This project processes PDF files by extracting text, generating summaries, and extracting keywords based on the document length (short, medium, and long PDFs). The results, including the summary, keywords, and metadata, are stored in MongoDB.

## Features
- **Concurrency**: Multiple PDFs are processed in parallel using Python's `ThreadPoolExecutor`.
- **Document Length Handling**: The pipeline adjusts the summarization and keyword extraction process for short (1-10 pages), medium (10-30 pages), and long (30+ pages) PDFs.
- **Error Handling**: If a PDF fails to download or parse, the error is logged, and processing continues for the other documents.
- **MongoDB Storage**: The extracted information is stored in MongoDB, allowing for further analysis and retrieval.
- **Performance Logging**: The total time taken to process all PDFs and the number of PDFs processed are logged.

## Table of Contents
1. [Requirements](#requirements)
2. [Setup](#setup)
3. [How to Run](#how-to-run)
4. [Project Structure](#project-structure)
5. [Customization](#customization)
6. [Error Handling](#error-handling)

## Requirements
- Python 3.x
- The following Python libraries:
  - `requests`
  - `PyPDF2`
  - `nltk`
  - `pymongo`
  - `concurrent.futures`
  
- MongoDB cluster (you can set up a free cluster using [MongoDB Atlas](https://www.mongodb.com/cloud/atlas)).
  
To install the required Python packages, you can use the following command:

```bash
  pip install requests PyPDF2 nltk pymongo
  import nltk
  nltk.download('stopwords')
  nltk.download('punkt')
```
## setup 
Clone this repository or copy the code files to your local machine.
Update the MongoDB connection string in the code:
```
connection_string = "your_mongo_db_connection_string_here"
```
Place your Dataset.json file (containing the URLs of the PDFs) in the appropriate folder. The file should be a JSON file where the values are URLs pointing to the PDFs you want to process.
The logs of any errors encountered during processing are saved in the pdf_processing.log fil
##How to Run
Run the script by executing the following command:
```bash

python parse_pdf1.py
```
The program will:

Fetch each PDF from the list of URLs.
Parse the text from each PDF.
Generate a summary and extract keywords based on the length of the PDF (short, medium, or long).
Store the extracted data in a MongoDB collection named summary&keywords.
Log the total time taken to process the PDFs and store the results.
After running, check MongoDB for the inserted documents, which will contain:

pdf_url: URL of the processed PDF.
summary: Summary of the text.
keywords: Extracted keywords.
num_pages: Number of pages in the PDF.
## Project Structure
```graphql

.
├── Dataset.json            # JSON file containing URLs to PDFs
├── pdf_processing.log      # Log file for error handling
└── README.md               # This README file
```
## Customization
Adjusting Summarization and Keyword Extraction:

The length of the summary and the number of keywords are adjusted based on the number of pages in the PDF.
You can modify the following logic in summarize_text and extract_keywords functions if you want to change these thresholds:
```
 if num_pages <= 10:  # Short PDFs (1-10 pages)
    num_sentences = 2
elif num_pages <= 30:  # Medium PDFs (10-30 pages)
    num_sentences = 5
else:  # Long PDFs (30+ pages)
    num_sentences = 8
```
## Concurrency:

The pipeline uses 5 threads by default. You can adjust this value in the ThreadPoolExecutor call:
```
with ThreadPoolExecutor(max_workers=5) as executor:
```
## Error Handling
If a PDF fails to download, parse, or store in MongoDB, the error will be logged in pdf_processing.log, and the pipeline will continue processing other PDFs.
The log file captures the URLs of the PDFs that encountered errors for later troubleshooting.
## Performance
The script processes 18 PDFs in 398.61 seconds on average, but actual performance may vary based on the size of the PDFs, the speed of the internet connection, and the performance of your system.
