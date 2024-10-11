import requests
import PyPDF2
from io import BytesIO
import json
from pymongo import MongoClient
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from collections import Counter
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
import logging

# MongoDB connection string (replace with your actual connection string)
connection_string = "mongodb+srv://rohitjai1311:6UdqgPcy3P6akbzX@cluster0.l3s4v.mongodb.net/"

# Connect to MongoDB
client = MongoClient(connection_string)
db = client['PDF']  
collection = db['summary&keywords']  

# Setup logging for error handling
logging.basicConfig(filename="pdf_processing.log", level=logging.ERROR)

def fetch_pdf(url):
    """
    Fetches the PDF content from the provided URL.
    
    Args:
        url (str): The URL of the PDF to fetch.
        
    Returns:
        BytesIO: The PDF content in binary format, or None if the fetch fails.
    """
    try:
        response = requests.get(url)
        response.raise_for_status()  # Raise an exception for HTTP errors (4xx, 5xx status codes)
        return BytesIO(response.content)
    except requests.exceptions.RequestException as e:
        logging.error(f"Failed to fetch PDF from {url}: {e}")
        return None

def parse_pdf(pdf_file):
    """
    Parses the PDF file to extract text and determine the number of pages.
    
    Args:
        pdf_file (BytesIO): The PDF file content in binary format.
        
    Returns:
        tuple: A tuple containing the extracted text and the number of pages in the PDF.
    """
    try:
        reader = PyPDF2.PdfReader(pdf_file)
        text_content = ""
        num_pages = len(reader.pages)
        
        # Extract text from each page
        for page in reader.pages:
            text_content += page.extract_text() + "\n"
        
        return text_content, num_pages
    except Exception as e:
        logging.error(f"Failed to parse PDF: {e}")
        return None, 0

def summarize_text(text, num_pages):
    """
    Summarizes the text based on the number of pages (short, medium, long PDFs).
    
    Args:
        text (str): The extracted text from the PDF.
        num_pages (int): The number of pages in the PDF.
        
    Returns:
        str: A summary of the text based on the length of the PDF.
    """
    sentences = text.split('.')
    
    # Adjust summary length based on document length (number of pages)
    if num_pages <= 10:  # Short PDFs (1-10 pages)
        num_sentences = 2
    elif num_pages <= 30:  # Medium PDFs (10-30 pages)
        num_sentences = 5
    else:  # Long PDFs (30+ pages)
        num_sentences = 8
    
    summary = '.'.join(sentences[:num_sentences])
    return summary

def extract_keywords(text, num_pages):
    """
    Extracts keywords using frequency analysis, adjusted for document length based on the number of pages.
    
    Args:
        text (str): The extracted text from the PDF.
        num_pages (int): The number of pages in the PDF.
        
    Returns:
        list: A list of extracted keywords based on the document length.
    """
    stop_words = set(stopwords.words('english'))
    words = word_tokenize(text)
    
    # Filter out stop words and non-alphanumeric characters
    filtered_words = [word.lower() for word in words if word.isalnum() and word.lower() not in stop_words]
    word_freq = Counter(filtered_words)
    
    # Adjust the number of keywords based on document length
    if num_pages <= 10:  # Short PDFs
        num_keywords = 3
    elif num_pages <= 30:  # Medium PDFs
        num_keywords = 5
    else:  # Long PDFs
        num_keywords = 7
    
    # Return the most common keywords
    keywords = [word for word, freq in word_freq.most_common(num_keywords)]
    return keywords

def process_pdf(url):
    """
    Processes a single PDF by fetching, parsing, summarizing, extracting keywords, and storing the results in MongoDB.
    
    Args:
        url (str): The URL of the PDF to process.
        
    Returns:
        bool: True if the processing was successful, False otherwise.
    """
    pdf_file = fetch_pdf(url)
    if pdf_file:
        text, num_pages = parse_pdf(pdf_file)
        if text:
            # Generate summary and keywords
            summary = summarize_text(text, num_pages)
            keywords = extract_keywords(text, num_pages)
            
            # Store the results in MongoDB
            document = {
                'pdf_url': url,
                'summary': summary,
                'keywords': keywords,
                'num_pages': num_pages  # Store the number of pages for reference
            }
            collection.insert_one(document)
            return True
        else:
            logging.error(f"Failed to extract text from {url}")
    return False

def ingest_and_parse_pdfs(urls):
    """
    Ingests and processes a list of PDF URLs concurrently, extracting text, summarizing, and storing in MongoDB.
    
    Args:
        urls (list): A list of URLs of PDFs to process.
    """
    with ThreadPoolExecutor(max_workers=5) as executor:
        # Submit each PDF URL for processing using multithreading
        futures = [executor.submit(process_pdf, url) for url in urls]
        for future in as_completed(futures):
            try:
                # Handle any exceptions that occur during processing
                future.result()
            except Exception as e:
                logging.error(f"Error during PDF processing: {e}")

# Load PDF URLs from dataset.json
dataset_folder = r"C:\Users\hp\Downloads\Dataset.json"
with open(dataset_folder, "r") as file:
    dataset_json = json.load(file)

pdf_urls = list(dataset_json.values())

# Start performance tracking
start_time = time.time()

# Process the PDFs concurrently
ingest_and_parse_pdfs(pdf_urls)

# End performance tracking
end_time = time.time()
elapsed_time = end_time - start_time

# Print success message and performance metrics
print("All PDF files have been processed successfully!")
print(f"Total time taken: {elapsed_time:.2f} seconds")
print(f"Total PDFs processed: {len(pdf_urls)}")
