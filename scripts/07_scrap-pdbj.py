import os
import time
import pandas as pd
from tqdm import tqdm
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager

# --- Paths ---
INPUT_CSV  = r'E:\research\ayurvedic-hiv\data\processed\09_ayurvedic-knapsack-bindingdb-hiv-targets.csv'
OUTPUT_CSV = r'E:\research\ayurvedic-hiv\data\processed\10_ayurvedic-knapsack-bindingdb-pdbj.csv'
ERROR_CSV  = r'E:\research\ayurvedic-hiv\data\error\10_ayurvedic-knapsack-bindingdb-pdbj.csv'

# --- Load data & init kolom baru ---
df = pd.read_csv(INPUT_CSV)
df['queries'] = None   # akan kita isi list of values

# --- Setup Chrome ---
opts = Options()
# opts.add_argument("--headless")    # bisa di‐uncomment nanti
opts.add_argument("--no-sandbox")
opts.add_argument("--disable-dev-shm-usage")
opts.add_argument("--disable-gpu")

driver = webdriver.Chrome(
    service=Service(ChromeDriverManager().install()),
    options=opts
)
wait = WebDriverWait(driver, 30)

# --- Loop per baris ---
for idx, link_str in tqdm(df['pdb_link'].items(),
                          total=len(df),
                          desc="Extracting all queries",
                          unit="row"):
    # split dan bersihkan
    # urls = [u.strip() for u in link_str.split(',') if u.strip()]
    values = []
    error = []
    
    try:
        driver.get(link_str)
        time.sleep(5)   # beri waktu React mount
        inp = wait.until(EC.visibility_of_element_located((
            By.CSS_SELECTOR,
            "input[type='text'][placeholder='Enter one or more search terms.']"
        )))
        values.append(inp.get_attribute('value'))
    except Exception as e:
        print(f"[{idx}] ERROR on {link_str}: {e}")
        error.append(idx, e)
        
    df.at[idx, 'queries'] = values

# --- Simpan & cleanup ---
driver.quit()
df.to_csv(OUTPUT_CSV, index=True)
error_df = pd.DataFrame(error, columns=['idx', 'error'])
error_df.to_csv(ERROR_CSV, index=False)
print(f"Done! Errors saved to {ERROR_CSV}")
print(f"Done! Results with all queries saved to {OUTPUT_CSV}")
