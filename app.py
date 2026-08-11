from flask import Flask, render_template, request, jsonify, session
import pickle
import pandas as pd
import requests

app = Flask(__name__)
app.secret_key = "carebot-secret-key-change-this"  # needed for sessions to work

with open("model.pkl", "rb") as f:
    model = pickle.load(f)

symptom_synonyms = {
    "fever": ["high_fever", "mild_fever"],
    "stomach ache": ["stomach_pain", "abdominal_pain"],
    "stomach pain": ["stomach_pain", "abdominal_pain"],
    "throwing up": ["vomiting"],
    "tired": ["fatigue"],
    "dizzy": ["dizziness"],
    "cant sleep": ["restlessness"],
    "cold": ["continuous_sneezing", "runny_nose"],
    "sore throat": ["throat_irritation", "patches_in_throat"],
    "body pain": ["muscle_pain", "joint_pain"],
}

with open("symptoms_list.pkl", "rb") as f:
    all_symptoms = pickle.load(f)

URGENT_SYMPTOMS = {"chest_pain", "breathlessness", "coma", "loss_of_balance", "slurred_speech", "unsteadiness"}

def extract_symptoms(user_message):
    matched = set()

    # Step 1: exact symptom matches first (most specific/reliable)
    for symptom in all_symptoms:
        if symptom.replace("_", " ") in user_message:
            matched.add(symptom)

    # Step 2: synonym phrases — only add if none of their target symptoms are already covered
    for phrase, mapped in symptom_synonyms.items():
        if phrase in user_message:
            if not any(m in matched for m in mapped):
                matched.update(mapped)

    return matched

def get_bot_reply(user_message):
    user_message = user_message.lower().strip()

    if user_message == "":
        return "Please tell me your symptoms so I can help."

    # Track symptoms across the whole conversation, not just this message
    if "collected_symptoms" not in session:
        session["collected_symptoms"] = []

    new_symptoms = extract_symptoms(user_message)
    all_collected = set(session["collected_symptoms"]) | new_symptoms
    session["collected_symptoms"] = list(all_collected)

    urgent_warning = ""
    if any(s in all_collected for s in URGENT_SYMPTOMS):
        urgent_warning = "⚠️ These symptoms may need immediate medical attention — please consider seeing a doctor urgently.\n\n"

    if len(all_collected) > 0:
        input_data = {symptom: (1 if symptom in all_collected else 0) for symptom in all_symptoms}
        input_df = pd.DataFrame([input_data])

        prediction = model.predict(input_df)[0]

        recognized = ", ".join(s.replace("_", " ") for s in all_collected)

        # Encourage more detail if we only have 1-2 symptoms so far
        followup = ""
        if len(all_collected) < 3:
            followup = " Do you have any other symptoms? More details will improve accuracy."

        return (f"{urgent_warning}Based on symptoms so far ({recognized}), it could be: "
                f"{prediction}.{followup} "
                f"Please consult a doctor to confirm.")

    # Fallback: NIH API for out-of-dataset queries
    try:
        filler_words = {"i", "have", "a", "an", "the", "and", "my", "feel", "feeling", "am", "is", "with"}
        words = [w for w in user_message.split() if w not in filler_words]

        all_conditions = []
        for word in words:
            response = requests.get(
                "https://clinicaltables.nlm.nih.gov/api/conditions/v3/search",
                params={"terms": word, "df": "term_icd9_code,primary_name"}
            )
            data = response.json()
            conditions = data[3]
            if conditions:
                all_conditions.extend(conditions)

        if all_conditions:
            seen = set()
            unique_names = []
            for c in all_conditions:
                if c[1] not in seen:
                    seen.add(c[1])
                    unique_names.append(c[1])
                if len(unique_names) == 5:
                    break
            condition_list = ", ".join(unique_names)
            return (f"Possible related conditions: {condition_list}. "
                     f"Please consult a doctor to confirm.")
        else:
            return "I couldn't recognize any symptoms in that. Could you describe them differently?"
    except Exception:
        return "I couldn't recognize any symptoms in that. Could you describe them differently?"

@app.route("/")
def home():
    session.clear()  # fresh symptom memory each time the page loads
    return render_template("index.html")

@app.route("/chat", methods=["POST"])
def chat():
    data = request.get_json()
    user_message = data.get("message", "")
    reply = get_bot_reply(user_message)
    return jsonify({"reply": reply})

@app.route("/reset", methods=["POST"])
def reset():
    session.clear()
    return jsonify({"status": "cleared"})

if __name__ == "__main__":
    app.run(debug=True)