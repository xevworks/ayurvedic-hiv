import os
import time

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
from urllib.parse import quote

def test_function():
    return "Hello World!"

def test_selenium():
    print("Testing Selenium...")
    ## Setup chrome options
    chrome_options = Options()
    chrome_options.add_argument("--headless") # Ensure GUI is off
    chrome_options.add_argument("--no-sandbox")

    # Set path to chrome/chromedriver as per your configuration
    print("Executing part 1")
    homedir = os.path.expanduser("~")
    chrome_options.binary_location = f"{homedir}/chrome-linux64/chrome"
    webdriver_service = Service(f"{homedir}/chromedriver-linux64/chromedriver")

    print("Executing part 2")
    # Choose Chrome Browser
    browser = webdriver.Chrome(service=webdriver_service, options=chrome_options)

    print("Executing part 3")
    # Get page
    browser.get("https://cloudbytes.dev")

    print("Executing part 4")
    # Extract description from page and print
    description = browser.find_element(By.NAME, "description").get_attribute("content")
    print(f"{description}")

    #Wait for 10 seconds
    time.sleep(3)
    browser.quit()

def scrape_bindingdb(smiles):
    encoded_smiles = quote(smiles)
    base_url = "https://www.bindingdb.org/rwd/bind/searchby_smiles.jsp"
    query_url = f"{base_url}?submit=Search&startPg=0&Increment=50&SearchType=3&smilesStr={encoded_smiles}&Similarity=0.8"
    
    options = Options()
    options.add_argument('--headless')
    options.add_argument('--disable-gpu')
    options.add_argument('--no-sandbox')
    
    # Set path to chrome/chromedriver as per your configuration
    homedir = os.path.expanduser("~")
    options.binary_location = f"{homedir}/chrome-linux64/chrome"
    webdriver_service = Service(f"{homedir}/chromedriver-linux64/chromedriver")
    
    driver = webdriver.Chrome(service=webdriver_service, options=options)
    driver.get(query_url)
    WebDriverWait(driver, 30).until(
        EC.presence_of_element_located((By.TAG_NAME, "body"))
    )
    soup = BeautifulSoup(driver.page_source, 'html.parser')
    
    # Check if the page contains "No Similarity Matches"
    if "No Similarity Matches" in soup.body.get_text():
        driver.quit()
        return "No Similarity Matches", "No Similarity Matches", "No Similarity Matches", "No Similarity Matches", "No Similarity Matches"
    elif "Error: java.lang.NullPointerException" in soup.body.get_text():
        driver.quit()
        return "ERROR", "ERROR", "ERROR", "ERROR", "ERROR"
    
    target_names = []
    specieses = []
    bdb_ids = []
    ligand_smiles = []
    pdb_links = []
    
    # Extract the data from the page
    rows = soup.select(".index_table > div")
    for row in rows:
        target = row.select_one("span.header + a.big").text.strip() if row.select_one("span.header + a.big") else "NaN"
        target_names.append(target)
        
        species = row.select_one("span.header + a.big + span + span").text.strip() if row.select_one("span.header + a.big + span + span") else "NaN"
        specieses.append(species)
        
        bdb_id = row.select_one("span.header + a + a.big").text.strip() if row.select_one("span.header + a + a.big") else "NaN"
        bdb_ids.append(bdb_id)
        
        smiles_button = row.select_one("span.header + a + a.big + button")
        # print('SMILES_BUTTON', smiles_button)
        smiles_str = smiles_button["onclick"].split("'")[1] if smiles_button and "onclick" in smiles_button.attrs else "NaN"
        ligand_smiles.append(smiles_str)
        
        pdb_link = row.select_one("span.header + a[href^='https://www.rcsb.org']")
        pdb_link = pdb_link["href"] if pdb_link else "NaN"
        pdb_links.append(pdb_link)
    
    driver.quit()
    return ", ".join(target_names), ", ".join(specieses), ", ".join(bdb_ids), ", ".join(ligand_smiles), ", ".join(pdb_links)