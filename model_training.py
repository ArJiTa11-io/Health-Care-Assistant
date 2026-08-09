import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.tree import DecisionTreeClassifier
from sklearn.metrics import accuracy_score
import pickle

# Load dataset
df = pd.read_csv("dataset/dataset.csv")

symptom_cols = [col for col in df.columns if "Symptom" in col]
print("Symptom columns found:", len(symptom_cols))

# Step 1: Clean whitespace/formatting issues
for col in symptom_cols:
    df[col] = df[col].str.strip()
    df[col] = df[col].str.replace(" ", "_")

# Step 2: Collect unique symptoms
all_symptoms = set()
for col in symptom_cols:
    vals = df[col].dropna().unique()
    all_symptoms.update(vals)

all_symptoms = sorted(all_symptoms)
print("Cleaned unique symptom count:", len(all_symptoms))

# Step 3: Build the one-hot encoded table
encoded_rows = []
for _, row in df.iterrows():
    symptoms_in_row = set(row[symptom_cols].dropna())
    encoded_row = {symptom: 1 if symptom in symptoms_in_row else 0 for symptom in all_symptoms}
    encoded_row["Disease"] = row["Disease"]
    encoded_rows.append(encoded_row)

encoded_df = pd.DataFrame(encoded_rows)
print("Final encoded shape:", encoded_df.shape)
print(encoded_df.head())

encoded_df.to_csv("dataset/encoded_dataset.csv", index=False)
print("Saved to dataset/encoded_dataset.csv")

X = encoded_df.drop("Disease", axis=1)
y = encoded_df["Disease"]

# Step 2: Split into training and testing sets
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# Step 3: Train the Decision Tree
model = DecisionTreeClassifier(random_state=42)
model.fit(X_train, y_train)

# Step 4: Check accuracy
y_pred = model.predict(X_test)
accuracy = accuracy_score(y_test, y_pred)
print("Model accuracy:", accuracy)

# Step 5: Save the trained model + the symptom list (we'll need it later in app.py)
with open("model.pkl", "wb") as f:
    pickle.dump(model, f)

with open("symptoms_list.pkl", "wb") as f:
    pickle.dump(all_symptoms, f)

print("Model and symptom list saved!")