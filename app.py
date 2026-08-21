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

GENERAL_ADVICE = {
    "high_fever": "Rest, stay hydrated, and monitor your temperature every few hours.",
    "mild_fever": "Rest and stay hydrated; monitor if it worsens.",
    "cough": "Stay hydrated, avoid cold drinks, and rest your voice.",
    "vomiting": "Sip small amounts of water or ORS to stay hydrated; avoid solid food temporarily.",
    "diarrhoea": "Stay hydrated with ORS and avoid oily or spicy food.",
    "joint_pain": "Rest the affected joint and avoid strenuous activity.",
    "headache": "Rest in a quiet, dark room and stay hydrated.",
    "skin_rash": "Avoid scratching and keep the area clean and dry.",
    "chest_pain": "Avoid physical exertion and seek medical attention promptly.",
    "breathlessness": "Sit upright, stay calm, and seek medical attention promptly.",
    "fatigue": "Prioritize rest and avoid overexertion until you feel better.",
    "nausea": "Eat small, bland meals and avoid strong odors or greasy food.",
    "muscle_pain": "Rest the affected area and consider gentle stretching once pain eases.",
    "dizziness": "Sit or lie down immediately and avoid sudden movements.",
    "itching": "Avoid scratching, keep skin moisturized, and wear loose clothing.",
    "abdominal_pain": "Avoid heavy meals and rest; note if pain is localized or spreading.",
    "back_pain": "Avoid heavy lifting and maintain good posture while resting.",
    "sore_throat": "Gargle with warm salt water and stay hydrated.",
    "constipation": "Increase fluid and fiber intake, and stay physically active.",
    "weight_loss": "Track your diet and any other symptoms to report to your doctor.",
    "loss_of_appetite": "Try small, frequent meals rather than large ones.",
}

# Fallback tips based on broad symptom-name patterns, for anything not explicitly listed above
CATEGORY_FALLBACKS = [
    (["pain"], "Rest the affected area and avoid activities that worsen the discomfort."),
    (["fever"], "Stay hydrated and monitor your temperature regularly."),
    (["skin", "rash", "itching", "patches"], "Keep the area clean, avoid scratching, and monitor for spreading."),
    (["cough", "throat", "sneezing", "nose", "congestion"], "Stay hydrated and avoid irritants like smoke or cold air."),
    (["stomach", "abdominal", "vomiting", "nausea", "diarrhoea"], "Stay hydrated and eat light, bland food until you feel better."),
    (["fatigue", "weakness", "tired"], "Prioritize rest and avoid overexertion."),
]

def build_recommendations(matched_symptoms):
    tips = []
    for s in matched_symptoms:
        if s in GENERAL_ADVICE:
            if GENERAL_ADVICE[s] not in tips:
                tips.append(GENERAL_ADVICE[s])
        else:
            # No exact entry — try to match it to a broader category
            matched_category = False
            for keywords, tip in CATEGORY_FALLBACKS:
                if any(k in s for k in keywords):
                    if tip not in tips:
                        tips.append(tip)
                    matched_category = True
                    break
            if not matched_category and "Get adequate rest and stay hydrated." not in tips:
                tips.append("Get adequate rest and stay hydrated.")

    if not tips:
        tips.append("Get adequate rest and stay hydrated.")
    return tips

def get_bot_reply(user_message):
    user_message = user_message.lower().strip()

    if user_message == "":
        return "Please tell me your symptoms so I can help."

    if "collected_symptoms" not in session:
        session["collected_symptoms"] = []

    new_symptoms = extract_symptoms(user_message)
    previously_collected = set(session["collected_symptoms"])

    if previously_collected and new_symptoms and not (previously_collected & new_symptoms):
        all_collected = new_symptoms
    else:
        all_collected = previously_collected | new_symptoms

    session["collected_symptoms"] = list(all_collected)

    urgent_warning = ""
    if any(s in all_collected for s in URGENT_SYMPTOMS):
        urgent_warning = "⚠️ These symptoms may need immediate medical attention — please consider seeing a doctor urgently.\n\n"

    if len(all_collected) > 0:
        input_data = {symptom: (1 if symptom in all_collected else 0) for symptom in all_symptoms}
        input_df = pd.DataFrame([input_data])

        prediction = model.predict(input_df)[0]
        recognized = ", ".join(s.replace("_", " ") for s in all_collected)
        recommendations = build_recommendations(all_collected)
        rec_text = "\n".join(f"• {tip}" for tip in recommendations)

        followup = ""
        if len(all_collected) < 3:
            followup = "\n\nDo you have any other symptoms? More details will improve accuracy."

        return (f"{urgent_warning}Based on symptoms so far ({recognized}), it could be: {prediction}.\n\n"
                f"General care recommendations:\n{rec_text}\n\n"
                f"Please consult a doctor to confirm and for a proper treatment plan.{followup}")

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

            general_tips = (
                "• Monitor your symptoms and note any changes over time.\n"
                "• Avoid activities that worsen your discomfort until you're evaluated.\n"
                "• Avoid self-medicating or self-treating without professional guidance."
            )

            return (f"Possible related conditions: {condition_list}.\n\n"
                     f"General recommendations:\n{general_tips}\n\n"
                     f"Please consult a doctor for an accurate diagnosis and treatment plan.")
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