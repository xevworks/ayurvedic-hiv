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
INPUT_CSV  = r'E:\research\ayurvedic-hiv\data\processed\11_pdbj.csv'
OUTPUT_CSV = r'E:\research\ayurvedic-hiv\data\processed\12_pdbj-titled.csv'
ERROR_CSV  = r'E:\research\ayurvedic-hiv\data\error\12_pdbj-titled.csv'

# --- Load data & init kolom baru ---
df = pd.read_csv(INPUT_CSV)
df['title'] = None   # akan kita isi list of values

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
error = []

for idx, row in tqdm(df.iterrows(), total=df.shape[0], desc="Extracting titles", unit="row"):
    link = f'https://pdbj.org/mine/structural_details/{row["protein_code"]}'
    
    try:
        driver.get(link)
        time.sleep(5)
        title_element = wait.until(EC.visibility_of_element_located((
            By.CSS_SELECTOR,
            "#PDBExplorerPlane h2"
        )))
        title_value = title_element.text
        df.at[idx, 'title'] = title_value
        
    except Exception as e:
        print(f"[{idx}] ERROR on {link}: {e}")
        error.append((idx, str(e)))
    
    # print(df.head(5))  # Debug: print first 5 rows to check progress

# --- Simpan & cleanup ---
driver.quit()
df.to_csv(OUTPUT_CSV, index=True)
error_df = pd.DataFrame(error, columns=['idx', 'error'])
error_df.to_csv(ERROR_CSV, index=False)
print(f"Done! Errors saved to {ERROR_CSV}")
print(f"Done! Results with all queries saved to {OUTPUT_CSV}")
