import os
import re
import string
import ssl
import pickle
from datetime import datetime, timezone

import nltk
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
from flask import Flask, render_template_string, request, jsonify
from flask_sqlalchemy import SQLAlchemy

# --- TENSORFLOW IMPORTS ---
import tensorflow as tf
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Embedding, LSTM, Dense
from tensorflow.keras.preprocessing.sequence import pad_sequences
from tensorflow.keras.preprocessing.text import Tokenizer

# --- SSL FIX FOR NLTK DOWNLOADS ---
try:
    _create_unverified_https_context = ssl._create_unverified_context
except AttributeError:
    pass
else:
    ssl._create_default_https_context = _create_unverified_https_context

nltk.download('stopwords', quiet=True)
nltk.download('wordnet', quiet=True)
lemmatizer = WordNetLemmatizer()
stop_words = set(stopwords.words('english'))

script_dir = os.path.dirname(os.path.abspath(__file__))

def clean_and_standardize(text):
    text = str(text).lower()
    text = re.sub(r'https?://\S+|www\.\S+', '', text)
    text = re.sub(r'<.*?>+', '', text)
    text = re.sub(r'[%s]' % re.escape(string.punctuation), '', text)
    text = re.sub(r'\w*\d\w*', '', text)
    tokens = text.split()
    cleaned = [lemmatizer.lemmatize(w) for w in tokens if w not in stop_words]
    return " ".join(cleaned)

SUSPICIOUS_PATTERNS = [
    r'\b(shocking|unbelievable|secret|they don\'t want you to know|miracle|conspiracy)\b',
    r'\b(breaking news|urgent|share before deleted|100% true|guaranteed)\b',
    r'\b(invaded|secretly attacked|nuked|overthrown|declared war|yesterdayy)\b',
    r'!!+', r'\?\?\?+'
]

def analyze_and_highlight(raw_text):
    highlighted_text = raw_text
    flagged_words = []
    for pattern in SUSPICIOUS_PATTERNS:
        matches = re.findall(pattern, raw_text, re.IGNORECASE)
        for match in matches:
            if match not in flagged_words:
                flagged_words.append(match)
            highlighted_text = re.sub(
                f"({re.escape(match)})", 
                r'<mark style="background-color: #ffe066; color: #000; font-weight: bold; padding: 2px 6px; border-radius: 4px;">\1</mark>', 
                highlighted_text, 
                flags=re.IGNORECASE
            )
    return highlighted_text, flagged_words

# Flask App Configuration
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = f"sqlite:///{os.path.join(script_dir, 'database.db')}"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

class VerificationLog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    input_text = db.Column(db.Text, nullable=False)
    prediction = db.Column(db.String(10), nullable=False)
    confidence = db.Column(db.Float, nullable=False)
    timestamp = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

with app.app_context():
    db.create_all()

# --- LSTM MODEL CONFIGURATION ---
# Fixed to match the Kaggle dataset sequence length
MAX_LEN = 200 

model_path = os.path.join(script_dir, "lstm_model.h5")
tokenizer_path = os.path.join(script_dir, "tokenizer.pkl")

if os.path.exists(model_path) and os.path.exists(tokenizer_path):
    model = tf.keras.models.load_model(model_path)
    with open(tokenizer_path, 'rb') as handle:
        tokenizer = pickle.load(handle)
else:
    print("[WARNING] LSTM model/tokenizer not found. Initializing untrained dummy architecture...")
    # Updated dummy vocabulary size to match training script
    tokenizer = Tokenizer(num_words=20000)
    tokenizer.fit_on_texts(["real news headline", "fake secret miracle shocker news"])
    
    # Updated output_dim to 128 to match the actual trained model structure
    model = Sequential([
        Embedding(input_dim=20000, output_dim=128, input_length=MAX_LEN),
        LSTM(64),
        Dense(32, activation='relu'),
        Dense(1, activation='sigmoid') 
    ])
    model.compile(loss='binary_crossentropy', optimizer='adam', metrics=['accuracy'])

# ==========================================
# FULL HTML TEMPLATE
# ==========================================
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Fake News Verification Engine</title>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;700&display=swap" rel="stylesheet">
    <style>
        :root {
            --primary: #4f46e5; --primary-hover: #4338ca; --bg: #0f172a; --card-bg: #1e293b;
            --text-main: #f8fafc; --text-muted: #94a3b8; --real-color: #10b981; --fake-color: #ef4444; --border: #334155;
        }
        * { box-sizing: border-box; margin: 0; padding: 0; font-family: 'Inter', sans-serif; }
        body { background-color: var(--bg); color: var(--text-main); min-height: 100vh; display: flex; flex-direction: column; align-items: center; padding: 40px 20px; }
        .header { text-align: center; margin-bottom: 30px; }
        .header h1 { font-size: 2.2rem; font-weight: 700; background: linear-gradient(90deg, #818cf8, #c084fc); -webkit-background-clip: text; -webkit-text-fill-color: transparent; margin-bottom: 8px; }
        .header p { color: var(--text-muted); font-size: 0.95rem; }
        .container { width: 100%; max-width: 850px; background: var(--card-bg); border: 1px solid var(--border); border-radius: 16px; padding: 30px; box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.5); }
        .input-group { display: flex; flex-direction: column; gap: 8px; margin-bottom: 16px; }
        label { font-size: 0.85rem; font-weight: 600; color: var(--text-muted); text-transform: uppercase; letter-spacing: 0.05em; }
        textarea { width: 100%; background: #0f172a; border: 1px solid var(--border); border-radius: 10px; padding: 14px; color: var(--text-main); font-size: 0.95rem; outline: none; transition: border-color 0.2s; height: 130px; resize: vertical; }
        textarea:focus { border-color: var(--primary); }
        .btn-group { display: flex; gap: 12px; }
        button.action-btn { flex: 2; background: var(--primary); color: white; border: none; padding: 14px 28px; font-size: 1rem; font-weight: 600; border-radius: 10px; cursor: pointer; transition: all 0.2s; }
        button.action-btn:hover { background: var(--primary-hover); }
        .btn-clear { flex: 1; background: #475569; }
        .btn-clear:hover { background: #334155; }
        .result-box { display: none; margin-top: 25px; padding: 24px; border-radius: 12px; border: 1px solid var(--border); background: #0f172a; }
        .result-header { display: flex; align-items: center; justify-content: space-between; margin-bottom: 20px; padding-bottom: 15px; border-bottom: 1px solid var(--border); }
        .badge { padding: 6px 16px; border-radius: 20px; font-weight: 700; font-size: 0.9rem; letter-spacing: 0.05em; }
        .badge.REAL { background: rgba(16, 185, 129, 0.2); color: var(--real-color); border: 1px solid var(--real-color); }
        .badge.FAKE { background: rgba(239, 68, 68, 0.2); color: var(--fake-color); border: 1px solid var(--fake-color); }
        .progress-section { margin-bottom: 20px; }
        .progress-label { display: flex; justify-content: space-between; font-size: 0.85rem; color: var(--text-muted); margin-bottom: 8px; }
        .progress-bar-bg { width: 100%; height: 10px; background: var(--border); border-radius: 5px; overflow: hidden; }
        .progress-bar-fill { height: 100%; width: 0%; transition: width 0.6s ease; border-radius: 5px; }
        .highlight-section h4 { font-size: 0.9rem; color: var(--text-muted); margin-bottom: 10px; }
        .highlight-content { background: var(--card-bg); padding: 16px; border-radius: 8px; line-height: 1.6; color: #cbd5e1; font-size: 0.95rem; }
        .logs-container { margin-top: 30px; width: 100%; max-width: 850px; }
        .logs-container h3 { font-size: 1.1rem; color: var(--text-muted); margin-bottom: 12px; }
        table { width: 100%; border-collapse: collapse; background: var(--card-bg); border-radius: 12px; overflow: hidden; border: 1px solid var(--border); }
        th, td { padding: 12px 16px; text-align: left; font-size: 0.85rem; }
        th { background: #0f172a; color: var(--text-muted); font-weight: 600; }
        td { border-top: 1px solid var(--border); color: #cbd5e1; }
    </style>
</head>
<body>

    <div class="header">
        <h1>Fake News Verification Engine</h1>
        <p>NLP & LSTM Deep Learning Powered Authenticity Analysis</p>
    </div>

    <div class="container">
        <div class="input-group">
            <label for="newsInput">Article Content or Headline</label>
            <textarea id="newsInput" placeholder="Paste news article body or headline here to inspect..."></textarea>
        </div>

        <div class="btn-group">
            <button class="action-btn" onclick="verify()">Run Forensic Analysis</button>
            <button onclick="clearText()" class="action-btn btn-clear">Clear Input</button>
        </div>

        <div id="output" class="result-box">
            <div class="result-header">
                <h3>Verification Verdict</h3>
                <span id="verdictBadge" class="badge">---</span>
            </div>

            <div class="progress-section">
                <div class="progress-label">
                    <span>Confidence Score</span>
                    <span id="confidenceText">0%</span>
                </div>
                <div class="progress-bar-bg">
                    <div id="progressBar" class="progress-bar-fill"></div>
                </div>
            </div>

            <div class="highlight-section">
                <h4>Analyzed Text Output (Suspicious Patterns Flagged)</h4>
                <div id="highlighted" class="highlight-content"></div>
            </div>
        </div>
    </div>

    <div class="logs-container">
        <h3>Recent Database Analysis Logs</h3>
        <table>
            <thead>
                <tr>
                    <th>Snippet</th>
                    <th>Verdict</th>
                    <th>Confidence</th>
                </tr>
            </thead>
            <tbody id="logsTable">
                <tr><td colspan="3" style="text-align:center; color: var(--text-muted);">No logs recorded yet.</td></tr>
            </tbody>
        </table>
    </div>

<script>
async function verify() {
    const text = document.getElementById('newsInput').value;
    if(!text.trim()) return;

    try {
        const res = await fetch('/predict', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ text: text })
        });

        if (!res.ok) {
            const errData = await res.json();
            alert("Error: " + (errData.error || "Server error occurred."));
            return;
        }

        const data = await res.json();
        
        const output = document.getElementById('output');
        const badge = document.getElementById('verdictBadge');
        const confidenceText = document.getElementById('confidenceText');
        const progressBar = document.getElementById('progressBar');
        const highlighted = document.getElementById('highlighted');

        output.style.display = 'block';
        badge.innerText = data.prediction + " NEWS";
        badge.className = 'badge ' + (data.prediction === 'REAL' ? 'REAL' : 'FAKE');

        confidenceText.innerText = data.confidence + '%';
        progressBar.style.width = data.confidence + '%';
        progressBar.style.backgroundColor = data.prediction === 'REAL' ? 'var(--real-color)' : 'var(--fake-color)';

        highlighted.innerHTML = data.highlighted_text;

        loadLogs();
    } catch (err) {
        console.error("Analysis Failed:", err);
        alert("Failed to connect to the backend server.");
    }
}

function clearText() {
    document.getElementById('newsInput').value = '';
    document.getElementById('output').style.display = 'none';
}

async function loadLogs() {
    const res = await fetch('/logs');
    const logs = await res.json();
    const table = document.getElementById('logsTable');
    if(logs.length === 0) {
        table.innerHTML = `<tr><td colspan="3" style="text-align:center; color: var(--text-muted);">No logs recorded yet.</td></tr>`;
        return;
    }
    
    table.innerHTML = logs.map(log => `
        <tr>
            <td>${log.input_text}...</td>
            <td style="color: ${log.prediction === 'REAL' ? 'var(--real-color)' : 'var(--fake-color)'}; font-weight: 600;">${log.prediction}</td>
            <td>${log.confidence}%</td>
        </tr>
    `).join('');
}

loadLogs();
</script>
</body>
</html>
"""

@app.route('/')
def home():
    return render_template_string(HTML_TEMPLATE)

@app.route('/predict', methods=['POST'])
def predict():
    data = request.get_json()
    raw_text = data.get('text', '')
    if not raw_text.strip():
        return jsonify({'error': 'Empty input'}), 400

    cleaned = clean_and_standardize(raw_text)
    highlighted_html, flagged = analyze_and_highlight(raw_text)

    if not cleaned.strip():
        label = "FAKE" if len(flagged) > 0 else "REAL"
        confidence = 50.00
    else:
        seq = tokenizer.texts_to_sequences([cleaned])
        padded = pad_sequences(seq, maxlen=MAX_LEN, padding='post')
        prediction_score = float(model.predict(padded, verbose=0)[0][0])
        
        # Override logic: If at least 1 clickbait phrase is found, force FAKE
        if len(flagged) >= 1:
            label = "FAKE"
            confidence = min(99.9, 80.0 + (len(flagged) * 5.0))
        elif prediction_score > 0.6: 
            label = "FAKE"
            confidence = prediction_score * 100
        else:
            label = "REAL"
            confidence = max(75.0, (1.0 - prediction_score) * 100)

    log = VerificationLog(
        input_text=raw_text[:60], 
        prediction=label, 
        confidence=round(confidence, 2),
        timestamp=datetime.now(timezone.utc)
    )
    db.session.add(log)
    db.session.commit()

    return jsonify({
        'prediction': label,
        'confidence': round(confidence, 2),
        'highlighted_text': highlighted_html,
        'flagged_count': len(flagged)
    })

@app.route('/logs', methods=['GET'])
def get_logs():
    logs = VerificationLog.query.order_by(VerificationLog.id.desc()).limit(5).all()
    return jsonify([{
        'input_text': log.input_text,
        'prediction': log.prediction,
        'confidence': log.confidence
    } for log in logs])

if __name__ == '__main__':
    print("\nStarting LSTM server... Open http://127.0.0.1:5000 in your browser!")
    app.run(debug=True, port=5000)