import numpy as np
import pandas as pd

# Read CSV file
df = pd.read_csv("C:/AgriWork/CHF Wheat Lucknow/CHF_final_Work_Here/CHF_Wheat_All_Variables_normalized_Lucknow_25.csv")

# Ensure 'GDD_normalized' column exists
if "GDD_normalized" in df.columns:
    # Replace 0 with NaN and interpolate
    df["GDD_normalized"] = df["GDD_normalized"].replace(0, np.nan).interpolate()
    
    # Save corrected data
    df.to_csv("C:/AgriWork/CHF Wheat Lucknow/CHF_final_Work_Here/CHF_Wheat_All_Variables_normalized_Lucknow_25_GDD_correction.csv", index=False)

    print("Correction successful! File saved.")
else:
    print("Error: Column 'GDD_normalized' not found in the dataset.")
