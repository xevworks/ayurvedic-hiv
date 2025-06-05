import pandas as pd
import numpy as np

def explode_rows(df, index):
    split_target_name = df.loc[index, 'target_name'].split(', ')
    split_species = df.loc[index, 'species'].split(', ')
    split_bdb_id = df.loc[index, 'bdb_id'].split(', ')
    split_ligand_smiles = df.loc[index, 'ligand_smiles'].split(', ')
    pdb_link_value = df.loc[index, 'pdb_link']
    
    if pd.isna(pdb_link_value):
        split_pdb_link = [np.nan]
    else:
        split_pdb_link = pdb_link_value.split(', ')

    # Check the lengths of the lists
    lengths = [len(split_target_name), len(split_species), len(split_bdb_id), len(split_ligand_smiles), len(split_pdb_link)]
    
    # Ensure all lists have the same length
    min_length = min(lengths)
    split_target_name = split_target_name[:min_length]
    split_species = split_species[:min_length]
    split_bdb_id = split_bdb_id[:min_length]
    split_ligand_smiles = split_ligand_smiles[:min_length]
    split_pdb_link = split_pdb_link[:min_length]
    
    new_rows = pd.DataFrame({
        'C_ID': [df.loc[index, 'C_ID']] * min_length,
        'Code': [df.loc[index, 'Code']] * min_length,
        'FSM_Code': [df.loc[index, 'FSM_Code']] * min_length,
        'Name': [df.loc[index, 'Name']] * min_length,
        'Common Name': [df.loc[index, 'Common Name']] * min_length,
        'Scientific Name': [df.loc[index, 'Scientific Name']] * min_length,
        'Quantity': [df.loc[index, 'Quantity']] * min_length,
        'Non plant ingredient': [df.loc[index, 'Non plant ingredient']] * min_length,
        'Action': [df.loc[index, 'Action']] * min_length,
        'Application': [df.loc[index, 'Application']] * min_length,
        'Comments': [df.loc[index, 'Comments']] * min_length,
        'Bacteria': [df.loc[index, 'Bacteria']] * min_length,
        'Metabolite Name': [df.loc[index, 'Metabolite Name']] * min_length,
        'Formula': [df.loc[index, 'Formula']] * min_length,
        'Mw': [df.loc[index, 'Mw']] * min_length,
        'CAS RN': [df.loc[index, 'CAS RN']] * min_length,
        'InChIKey': [df.loc[index, 'InChIKey']] * min_length,
        'InChICode': [df.loc[index, 'InChICode']] * min_length,
        'SMILES': [df.loc[index, 'SMILES']] * min_length,
        'target_name': split_target_name,
        'species': split_species,
        'bdb_id': split_bdb_id,
        'ligand_smiles': split_ligand_smiles,
        'pdb_link': split_pdb_link
    })
    
    return new_rows

def process_dataframe(df):
    all_new_rows = []
    for i in range(len(df)):
        print(f"Processing row {i}")
        new_rows = explode_rows(df, i)
        all_new_rows.append(new_rows)
    
    all_new_rows_df = pd.concat(all_new_rows, ignore_index=True)
    return all_new_rows_df
    