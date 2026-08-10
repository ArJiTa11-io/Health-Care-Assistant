# 🩺 CareBot - AI Symptom Checker Chatbot

CareBot is a full-stack AI/ML web application that helps users get a quick, preliminary idea of what condition their symptoms might point to. It combines a locally trained machine learning model with a live external medical API, wrapped in a conversational chat interface built with Flask.

## ✨ Features

- 🤖 **Conversational Chat UI**: Clean, dark, medical-themed chat interface with avatars and a typing indicator
- 🧠 **ML-Powered Predictions**: Decision Tree model trained on a 4,920-record disease-symptom dataset covering 41 conditions
- 🗣️ **Natural Language Matching**: Understands casual phrasing ("fever," "stomach ache"), not just exact medical terms
- 🌐 **Dynamic API Fallback**: Queries the free NIH Clinical Tables API for symptoms outside the trained dataset, instead of failing
- 💬 **Multi-Turn Memory**: Remembers symptoms across the whole conversation, not just the current message
- ⚠️ **Urgency Detection**: Flags potentially serious symptom combinations with an immediate warning
- 🕘 **Conversation History**: Review past conversations via a History panel
- 🔄 **Reset Option**: Start a fresh conversation anytime

## 🛠️ Tech Stack

**Backend**
- Python 3.13
- Flask
- Flask sessions (for multi-turn memory)

**Machine Learning**
- scikit-learn (Decision Tree Classifier)
- pandas (data cleaning & preprocessing)

**Frontend**
- HTML5, CSS3
- Vanilla JavaScript (ES6+)
- Browser `localStorage` (conversation history)

**External API**
- NIH Clinical Tables API (free, open, no key required)

## 📁 Project Structure
CareBot/
│
├── app.py # Main Flask server — routes, chat logic, API fallback
├── model_training.py # Data cleaning, encoding, and model training script
├── explore_data.py # Initial dataset exploration script
├── model.pkl # Saved trained Decision Tree model
├── symptoms_list.pkl # Saved list of 131 known symptoms (encoding order)
├── .gitignore # Git ignore rules
├── README.md # Project documentation
│
├── dataset/
│ ├── dataset.csv # Raw disease-symptom dataset (Kaggle)
│ └── encoded_dataset.csv # Cleaned, one-hot encoded dataset
│
└── templates/
└── index.html # Chat interface — UI, JS logic, styling

## ⚙️ Prerequisites

Before you begin, ensure you have the following installed:

- **Python** (v3.10 or higher)
- **pip** (comes with Python)
- **Git** — for version control
- **Code Editor** — VS Code recommended

## 🚀 Installation & Setup

### 1. Clone the Repository
```bash
git clone https://github.com/ArJiTa11-io/Health-Care-Assistant.git
cd Health-Care-Assistant
```

### 2. Install Dependencies
```bash
pip install flask pandas scikit-learn requests
```

### 3. Train the Model
This generates `model.pkl` and `symptoms_list.pkl` from the dataset:
```bash
python model_training.py
```

### 4. Start the Server
```bash
python app.py
```
You should see:
Running on http://127.0.0.1:5000
### 5. Access the Application
Open your browser and navigate to:
http://127.0.0.1:5000
## 🎯 How to Use CareBot

1. **Start a conversation** — CareBot greets you with a welcome message automatically
2. **Describe your symptoms** — type naturally, e.g. "I have high fever and cough"
3. **Get a prediction** — if your symptoms match the trained dataset, CareBot gives a specific prediction
4. **Out-of-scope symptoms** — if CareBot doesn't recognize something (e.g. "I have a broken toe"), it automatically checks the NIH medical database and returns relevant conditions instead
5. **Continue the conversation** — mention more symptoms in follow-up messages; CareBot remembers everything said so far
6. **Review history** — click **History** to revisit past conversations
7. **Start fresh** — click **Reset** to clear the current conversation

## 🔌 Backend Routes

| Method | Endpoint | Description | Request Body |
|--------|----------|-------------|---------------|
| GET | `/` | Loads the chat interface, clears session | – |
| POST | `/chat` | Sends a user message, returns CareBot's reply | `{ "message": "I have fever" }` |
| POST | `/reset` | Clears the current conversation's symptom memory | – |

**Example Request:**
```javascript
fetch('/chat', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({ message: "I have high fever and cough" })
});
```

## 🧠 How the Prediction Pipeline Works

1. **Data Cleaning**: Fixed inconsistent symptom formatting (extra spaces, inconsistent separators) in the raw Kaggle dataset
2. **Encoding**: Converted 131 unique symptoms into a one-hot encoded numeric format
3. **Training**: Trained a Decision Tree Classifier on the encoded data, split 80/20 for training/testing
4. **Matching**: User input is matched against known symptoms directly, and against a synonym dictionary for casual phrasing
5. **Prediction or Fallback**: If symptoms match, the trained model predicts a condition; if not, the NIH API is queried live for related conditions

## 🐛 Troubleshooting

**Issue: `jinja2.exceptions.TemplateNotFound: index.html`**
Solution: Make sure `index.html` is inside a folder named exactly `templates`, sitting next to `app.py`.

**Issue: `ModuleNotFoundError` for flask/pandas/sklearn**
Solution: Run `pip install flask pandas scikit-learn requests` again, and confirm you're using the same Python environment the error is referencing.

**Issue: Server starts but chat replies with "Something went wrong"**
Solution: Check the terminal running `python app.py` for the actual traceback — this usually points to a missing `model.pkl`/`symptoms_list.pkl` (run `model_training.py` first) or a NIH API connectivity issue.

**Issue: `python app.py` exits immediately with no output**
Solution: Check that the file still has its `@app.route` definitions and `app.run(debug=True)` at the bottom — these can get lost during manual edits.

## 📚 What I Learned

- Building a complete ML pipeline: cleaning, encoding, training, and reusing a saved model
- Connecting a Flask backend to both a trained ML model and a live external API in one system
- Designing a hybrid fallback architecture instead of depending on a single data source
- Real debugging: diagnosing blocked/rate-limited third-party APIs, and catching duplicate-code bugs through systematic testing
- Managing conversation state in a web app using Flask sessions

## 🔮 Possible Improvements

- Integrate a certified clinical API (e.g. Infermedica) for more clinically rigorous fallback data
- Add persistent, server-side conversation history using a database (currently browser-only)
- Expand the training dataset for broader native disease coverage
- Add confidence scores back with clearer visual presentation

## ⚠️ Disclaimer

CareBot is a project built for educational purposes. It is **not a substitute for professional medical advice, diagnosis, or treatment**. Always consult a qualified doctor for real symptoms or health concerns.

## 🤝 Contributing

Contributions, suggestions, and feedback are welcome:

1. Fork the repository
2. Create a new branch (`git checkout -b feature/YourFeature`)
3. Commit your changes (`git commit -m 'Add YourFeature'`)
4. Push to the branch (`git push origin feature/YourFeature`)
5. Open a Pull Request

## 💬 Feedback & Support

Found a bug or have a suggestion? Open an [issue](../../issues) on this repository, or reach out to me directly.

## 👩‍💻 Author

**Arjita**
GitHub: [@ArJiTa11-io](https://github.com/ArJiTa11-io)
LinkedIn:[@Arjita] (www.linkedin.com/in/arjita-pandey)
