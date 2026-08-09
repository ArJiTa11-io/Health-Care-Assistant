import pandas as pd 

df = pd.read_csv("dataset/dataset.csv")

print("Shape (rows, columns):",df.shape)
print("\nColumn names:", df.columns.tolist())
print("\nFirst 5 rows:")
print(df.head())

print("\nData type & missing values:")
print(df.info())

print("\nHow many uniquen diseases:")
print(df["Disease"].nunique())
print(df["Disease"].value_counts())

symptom_cols = [col for col in df.columns if "Symptom" in col]

all_symptoms = set()
for col in symptom_cols:
    all_symptoms.update(df[col].dropna().str.strip().unique())

print("Total unique symptoms:", len(all_symptoms))
print(sorted(all_symptoms))