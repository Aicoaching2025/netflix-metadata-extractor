import pandas as pd
import os

# Point to the kagglehub download location
data_path = "/Users/candace/.cache/kagglehub/datasets/rohitgrewal/netflix-data/versions/1"

# First, see what files are in the folder
print("Files in dataset folder:")
print(os.listdir(data_path))

# Load the CSV
df = pd.read_csv(os.path.join(data_path, "Netflix Dataset.csv"))

# Basic overview
print("\nShape:", df.shape)
print("\nColumns:", df.columns.tolist())
print("\nData types:\n", df.dtypes)
print("\nFirst 5 rows:\n", df.head())

# Examine the description column
print("\n--- Sample Descriptions ---")
for i, desc in enumerate(df["Description"].dropna().head(10)):
    print(f"\n[{i+1}] {desc}")

if "Type" in df.columns:
    print("\n--- Genre Distribution ---")
    print(df["Type"].value_counts().head(20))

if "Category" in df.columns:
    print("\n--- Content Category ---")
    print(df["Category"].value_counts())

if "Rating" in df.columns:
    print("\n--- Rating Distribution ---")
    print(df["Rating"].value_counts())

print("\n--- Missing Values ---")
print(df.isnull().sum())



# Save sample descriptions to a file for reference
with open("data/sample_descriptions.txt", "w") as f:
    for i, row in df[["Title", "Description"]].dropna(subset=["Description"]).head(10).iterrows():
        f.write(f"[{i+1}] Title: {row['Title']}\n")
        f.write(f"    Description: {row['Description']}\n\n")

print("\nSample descriptions saved to data/sample_descriptions.txt")