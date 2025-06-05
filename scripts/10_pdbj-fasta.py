import requests
import os
from tqdm import tqdm

import pandas as pd

save_folder = r'E:\research\ayurvedic-hiv\data\fasta'
os.makedirs(save_folder, exist_ok=True)

file_path = r'E:\research\ayurvedic-hiv\data\processed\12_pdbj-titled.csv'

counter = 0

ERROR = []

df = pd.read_csv(file_path)

for idx, row in tqdm(df.iterrows(), total=df.shape[0], desc="Downloading FASTA files", unit="row"):
    hiv_protein = row['protein_code']
    fasta_url = f'https://pdbj.org/rest/newweb/fetch/file?cat=pdb&type=fasta&id={hiv_protein}'
    
    file_path = os.path.join(save_folder, f"{hiv_protein}.tsv")
    
    try:
        response = requests.get(fasta_url, stream=True)
        # response.raise_for_status()  # Raise an error for bad responses
        
        if response.status_code == 200:
            with open(file_path, 'wb') as file:
                for chunk in response.iter_content(chunk_size=1024):
                    file.write(chunk)
            print(f"Downloaded {hiv_protein} to {file_path}")
            counter += 1
        else:
            print(f"Failed to download {hiv_protein} at index {idx}: HTTP {response.status_code}")

    except requests.RequestException as e:
        print(f"Error downloading {hiv_protein}: {e}")
        ERROR.append((idx, str(e)))
        
# Save errors to a CSV file
error_df = pd.DataFrame(ERROR, columns=['idx', 'error'])
error_file_path = os.path.join(save_folder, 'download_errors.csv')
error_df.to_csv(error_file_path, index=False)
print(f"Total files downloaded: {counter}")
print(f"Errors saved to {error_file_path}")
