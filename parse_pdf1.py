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
    """Fetches PDF from the provided URL and returns the PDF content."""
    try:
        response = requests.get(url)
        response.raise_for_status()  # Raise an exception for 4xx or 5xx status codes
        return BytesIO(response.content)
    except requests.exceptions.RequestException as e:
        logging.error(f"Failed to fetch PDF from {url}: {e}")
        return None

def parse_pdf(pdf_file):
    """Parses the PDF file and returns the text content and number of pages."""
    try:
        reader = PyPDF2.PdfReader(pdf_file)
        text_content = ""
        num_pages = len(reader.pages)
        
        for page in reader.pages:
            text_content += page.extract_text() + "\n"
        
        return text_content, num_pages
    except Exception as e:
        logging.error(f"Failed to parse PDF: {e}")
        return None, 0

def summarize_text(text, num_pages):
    """Summarizes text based on the number of pages (short, medium, long PDFs)."""
    sentences = text.split('.')
    
    if num_pages <= 10:  # Short PDFs (1-10 pages)
        num_sentences = 2
    elif num_pages <= 30:  # Medium PDFs (10-30 pages)
        num_sentences = 5
    else:  # Long PDFs (30+ pages)
        num_sentences = 8
    
    summary = '.'.join(sentences[:num_sentences])
    return summary

def extract_keywords(text, num_pages):
    """Extracts keywords using frequency analysis, adjusted for document length based on number of pages."""
    stop_words = set(stopwords.words('english'))
    words = word_tokenize(text)
    filtered_words = [word.lower() for word in words if word.isalnum() and word.lower() not in stop_words]
    word_freq = Counter(filtered_words)
    
    # Adjust number of keywords based on document length
    if num_pages <= 10:  # Short PDFs
        num_keywords = 3
    elif num_pages <= 30:  # Medium PDFs
        num_keywords = 5
    else:  # Long PDFs
        num_keywords = 7
    
    keywords = [word for word, freq in word_freq.most_common(num_keywords)]
    return keywords

def process_pdf(url):
    """Processes a single PDF, generating summary and keywords, and storing in MongoDB."""
    pdf_file = fetch_pdf(url)
    if pdf_file:
        text, num_pages = parse_pdf(pdf_file)
        if text:
            summary = summarize_text(text, num_pages)
            keywords = extract_keywords(text, num_pages)
            
            # Store in MongoDB
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
    """Ingests and parses PDF files from a list of URLs and stores data in MongoDB concurrently."""
    with ThreadPoolExecutor(max_workers=5) as executor:
        futures = [executor.submit(process_pdf, url) for url in urls]
        for future in as_completed(futures):
            try:
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

# Process PDFs concurrently
ingest_and_parse_pdfs(pdf_urls)

# End performance tracking
end_time = time.time()
elapsed_time = end_time - start_time

# Print success message and performance metrics
print("All PDF files have been processed successfully!")
print(f"Total time taken: {elapsed_time:.2f} seconds")
print(f"Total PDFs processed: {len(pdf_urls)}")
