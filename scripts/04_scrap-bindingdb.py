import sys
import os
import argparse
import pandas as pd
from tqdm import tqdm

"""
BindingDB Scraper

This script scrapes the BindingDB database to retrieve binding information for compounds
based on their SMILES notations. It takes a CSV file containing SMILES strings as input
and outputs a CSV file with detailed binding information for each compound.

For each compound, the script:
1. Searches BindingDB using the SMILES notation
2. Extracts information about target proteins that bind to the compound
3. Retrieves details including:
   - Target protein names
   - Species information
   - BindingDB IDs
   - Ligand SMILES
   - PDB links for 3D structures

The input CSV file should contain a column named 'SMILES' with the chemical structure
notation for each compound.
"""

def setup_paths(file_path):
    """Set up the system path to include the bdb_scraper module from the utils directory"""
    # Get the directory of the current script
    script_dir = os.path.dirname(os.path.abspath(__file__))
    # The utils directory is under the same scripts directory
    utils_path = os.path.join(script_dir, 'utils')
    sys.path.append(utils_path)
    
    try:
        from bdb_scraper import scrape_bindingdb
        return scrape_bindingdb
    except ImportError:
        print(f"Error: Could not import bdb_scraper module from {utils_path}")
        print("Please ensure the module exists in the utils directory.")
        sys.exit(1)

def main():
    # Set up argument parser
    parser = argparse.ArgumentParser(
        description='Scrape BindingDB for protein binding information based on SMILES notations',
        epilog='Example: python 04_scrap-bindingdb.py --file compounds.csv --output results'
    )
    parser.add_argument('--file', required=True, 
                        help='Path to the input CSV file containing SMILES notations')
    parser.add_argument('--output', required=True, 
                        help='Directory to save the output CSV files')
    args = parser.parse_args()

    # Validate input file
    if not os.path.exists(args.file):
        print(f"Error: Input file {args.file} does not exist.")
        return

    # Validate output directory
    if not os.path.exists(args.output):
        print(f"Creating output directory: {args.output}")
        os.makedirs(args.output)

    # Import the scrape_bindingdb function
    scrape_bindingdb = setup_paths(args.file)

    # Load the input data
    df = pd.read_csv(args.file, index_col=0)
    
    # Prepare output file paths
    output_file = os.path.join(args.output, "ayurvedic-bindingdb-results.csv")
    error_file = os.path.join(args.output, "ayurvedic-bindingdb-errors.csv")
    
    error = []

    for idx, row in tqdm(df.iterrows(), total=df.shape[0], desc="Processing SMILES"):
        smiles = row['SMILES']
        if pd.notna(smiles):
            try:
                print(f"Processing SMILES: {smiles} from CID: {row['C_ID']}")
                target_names, specieses, bdb_ids, ligand_smiles, pdb_links = scrape_bindingdb(smiles)
                df.at[idx, 'target_name'] = target_names
                df.at[idx, 'species'] = specieses
                df.at[idx, 'bdb_id'] = bdb_ids
                df.at[idx, 'ligand_smiles'] = ligand_smiles
                df.at[idx, 'pdb_link'] = pdb_links
            except Exception as e:
                print(f"Error processing {idx} from C_ID {row['C_ID']}: {e}")
                error.append((idx, row['C_ID'], str(e)))

    # Save errors to file
    error_df = pd.DataFrame(error, columns=['Index', 'C_ID', 'Error'])
    error_df.to_csv(error_file, index=False)
    print(f"Errors saved to {error_file}")

    # Save results to file
    df.to_csv(output_file, index=True)
    print(f"Data saved to {output_file}")

if __name__ == "__main__":
    main()
