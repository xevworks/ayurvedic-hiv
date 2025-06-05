import requests
from bs4 import BeautifulSoup
import pandas as pd
from tqdm import tqdm
import argparse
import os

"""
KNApSAcK Secondary Metabolite Scraper

This script scrapes the KNApSAcK database (http://www.knapsackfamily.com/) to retrieve 
secondary metabolite information for plant species. It takes a CSV file containing plant 
scientific names as input and outputs a CSV file with detailed information about the 
secondary metabolites associated with each plant.

For each plant species, the script:
1. Searches the KNApSAcK database using the scientific name
2. Extracts all compound IDs (CIDs) associated with the plant
3. Retrieves detailed information for each compound, including:
   - Metabolite name
   - Chemical formula
   - Molecular weight
   - CAS Registry Number
   - KNApSAcK ID (C_ID)
   - InChIKey
   - InChICode
   - SMILES notation

The input CSV file should contain a column named 'Scientific Name' with the plant 
scientific names to search for.
"""

def main():
    # Set up argument parser
    parser = argparse.ArgumentParser(description='Scrape KNApSAcK for metabolite information.')
    parser.add_argument('--file', required=True, help='Path to the input CSV file')
    parser.add_argument('--output', required=True, help='Directory to save the output file')
    args = parser.parse_args()

    # Validate input file
    if not os.path.exists(args.file):
        print(f"Error: Input file {args.file} does not exist.")
        return

    # Validate output directory
    if not os.path.exists(args.output):
        print(f"Creating output directory: {args.output}")
        os.makedirs(args.output)

    # Construct output file path
    output_file = os.path.join(args.output, "ayurvedic-formula-knapsack.csv")

    # Load the input data
    df = pd.read_csv(args.file, index_col=0)

    # Base URLs for search and details
    search_url = "http://www.knapsackfamily.com/knapsack_core/result.php"
    detail_url = "http://www.knapsackfamily.com/knapsack_core/information.php"

    rows_to_append = []

    for idx, row in tqdm(df.iterrows(), total=df.shape[0], desc="Processing Scientific Names"):
        print(f"Processing row {idx + 1}/{df.shape[0]}: {row['Scientific Name']}")
        scientific_name = row['Scientific Name']
        if pd.isna(scientific_name):
            continue  # Skip rows without a valid scientific name

        # Search for the metabolites
        params = {"sname": "all", "word": scientific_name}
        search_response = requests.get(search_url, params=params)
        search_soup = BeautifulSoup(search_response.text, 'html.parser')

        # Extract CIDs from the search result
        cid_links = search_soup.find_all('a', href=True, string=lambda t: t and t.startswith('C'))
        total_cids = len(cid_links)
        print(f"Found {total_cids} CIDs for '{scientific_name}'")
        if not cid_links:
            continue  # Skip if no CIDs are found

        # Iterate over all found CIDs and extract details
        for cid_link in cid_links:
            print(f"Processing CID {cid_links.index(cid_link) + 1}/{total_cids} for index {idx}")
            cid = cid_link['href'].split('=')[-1]
            detail_response = requests.get(f"{detail_url}?word={cid}")
            detail_soup = BeautifulSoup(detail_response.text, 'html.parser')

            # Extract relevant information from the detail page
            details = {
                "Name": None,
                "Formula": None,
                "Mw": None,
                "CAS RN": None,
                "C_ID": None,
                "InChIKey": None,
                "InChICode": None,
                "SMILES": None,
            }

            # Map table rows to the details dictionary
            for tr in detail_soup.find_all('tr'):
                th = tr.find('th')
                td = tr.find('td')
                if th and td:
                    key = th.get_text(strip=True)
                    value = td.get_text(strip=True)
                    if key in details:
                        details[key] = value

            # Create a new row with the original data and add the metabolite information
            new_row = row.copy()
            new_row['Metabolite Name'] = details['Name']
            new_row['Formula'] = details['Formula']
            new_row['Mw'] = details['Mw']
            new_row['CAS RN'] = details['CAS RN']
            new_row['C_ID'] = details['C_ID'].replace(',', '') if details['C_ID'] else None  # Remove comma from C_ID
            new_row['InChIKey'] = details['InChIKey']
            new_row['InChICode'] = details['InChICode']
            new_row['SMILES'] = details['SMILES']

            # Add the new row to the rows_to_append list
            rows_to_append.append(new_row)
            
    rows_to_append_df = pd.DataFrame(rows_to_append)
    rows_to_append_df.to_csv(output_file, index=False)
    print(f"Data extraction complete. Results saved to '{output_file}'.")

if __name__ == "__main__":
    main()