import requests

url = "https://clinicaltables.nlm.nih.gov/api/conditions/v3/search"
params = {
    "terms": "fever",
    "df": "term_icd9_code,primary_name"
}

response = requests.get(url, params=params)
print("Status code:", response.status_code)
print("Response:", response.json())