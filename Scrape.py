from selenium.webdriver import Chrome, ChromeOptions
from selenium.webdriver.chromium.remote_connection import ChromiumRemoteConnection
from bs4 import BeautifulSoup
from dotenv import load_dotenv
import os
#The code uses Selenium for web automation/scraping
#Beautiful soup for html parsing
#dotenv for environment variable management




#scrape_website function
def scrape_website(website):
    print("Starting local ChromeDriver...")
    options = ChromeOptions()
    with Chrome(options=options) as driver:
        driver.get(website)
        print("Scraping page content...")
        html = driver.page_source
        return html
    
# This function takes a website URL as input
# Creates a chrome browser instances using selenium 
# loads website and retrieves its html content
# returns the raw html on page
# uses context manager(with statement) to properly handle browser resourses






#Extract_body_content(html_content) function
def extract_body_content(html_content):
    soup = BeautifulSoup(html_content, "html.parser")
    body_content = soup.body
    if body_content:
                return str(body_content)
    return ""

#takes raw html as input 
#uses beautifulSoup to parse the html
#extracts only the <body> section of the web page
#returns the body content of a string, or empty string if no body found
#this helps focus on the main content, ignoring headers and metadata




#Clean_bosy_content function
def clean_body_content(body_content):
    soup = BeautifulSoup(body_content, "html.parser")
    
    # Remove script and style elements
    for script_or_style in soup(["script", "style"]):
        script_or_style.extract()

    # Get text and clean it up
    cleaned_content = soup.get_text(separator="\n")
    cleaned_content = "\n".join(
        line.strip() for line in cleaned_content.splitlines() if line.strip()
    )
    return cleaned_content

#takes body content and further cleans it
#removes all <script> and <style> tags to focus on actual content
#extracts only the text conetent, removing html tags
#uses "\n" as seperator btwn elements
#strips whitespace and removes empty lines
#returns clean, readable text content






#split_dom_content(dom_content, max_length=6000) Function
def split_dom_content(dom_content, max_length=6000):
    return [
        dom_content[i : i + max_length] for i in range(0, len(dom_content), max_length)
    ]

#takes cleaned content and splits into smaller chunkss
# default chunk size 6000 characters
#uses list comprehension to create chunks
#important for processing large texts that might exceed model conetxts limits



