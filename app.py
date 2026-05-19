"""
app.py — Flask backend for Student Performance Predictor
Run: python app.py
"""

from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
import pickle
import numpy as np
import os
import sqlite3
from datetime import datetime

app = Flask(__name__)
CORS(app)

# ---- Load Model ----
MODEL_PATH = os.path.join(os.path.dirname(__file__), 'model.pkl')
with open(MODEL_PATH, 'rb') as f:
    model = pickle.load(f)

LABELS = {
    0: {'grade': 'Fail',        'color': '#e74c3c', 'emoji': '✗', 'advice': 'Significant improvement needed. Focus on attendance and core study hours.'},
    1: {'grade': 'Pass',        'color': '#e67e22', 'emoji': '~', 'advice': 'You are passing but there is room to grow. Increase study hours and assignment quality.'},
    2: {'grade': 'Merit',       'color': '#2ecc71', 'emoji': '✓', 'advice': 'Good performance. Push your midterm preparation and you can reach Distinction.'},
    3: {'grade': 'Distinction', 'color': '#3498db', 'emoji': '★', 'advice': 'Excellent! Keep up the consistency and maintain your study routine.'},
}

# ---- Database Setup ----
DB_PATH = os.path.join(os.path.dirname(__file__), 'predictions.db')

def init_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS predictions (
            id              INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp       TEXT NOT NULL,
            attendance      REAL,
            assignment_avg  REAL,
            midterm_score   REAL,
            hours_studied   REAL,
            prev_gpa        REAL,
            sleep_hours     REAL,
            extracurricular INTEGER,
            prediction      TEXT,
            confidence      REAL
        )
    ''')
    conn.commit()
    conn.close()

def save_prediction(inputs, prediction, confidence):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('''
        INSERT INTO predictions (
            timestamp, attendance, assignment_avg, midterm_score,
            hours_studied, prev_gpa, sleep_hours, extracurricular,
            prediction, confidence
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (
        datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        inputs['attendance'],
        inputs['assignment_avg'],
        inputs['midterm_score'],
        inputs['hours_studied'],
        inputs['prev_gpa'],
        inputs['sleep_hours'],
        inputs['extracurricular'],
        prediction,
        confidence
    ))
    conn.commit()
    conn.close()

def get_history(limit=50):
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    c.execute('SELECT * FROM predictions ORDER BY id DESC LIMIT ?', (limit,))
    rows = [dict(row) for row in c.fetchall()]
    conn.close()
    return rows

def get_stats():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('SELECT COUNT(*) FROM predictions')
    total = c.fetchone()[0]

    c.execute('SELECT prediction, COUNT(*) FROM predictions GROUP BY prediction')
    distribution = {row[0]: row[1] for row in c.fetchall()}

    c.execute('SELECT AVG(attendance), AVG(hours_studied), AVG(midterm_score), AVG(confidence) FROM predictions')
    avgs = c.fetchone()

    conn.close()
    return {
        'total': total,
        'distribution': distribution,
        'avg_attendance': round(avgs[0] or 0, 1),
        'avg_study_hours': round(avgs[1] or 0, 1),
        'avg_midterm': round(avgs[2] or 0, 1),
        'avg_confidence': round(avgs[3] or 0, 1),
    }

# Init DB on startup
init_db()

# ---- Routes ----
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/history')
def history_page():
    return render_template('history.html')

@app.route('/predict', methods=['POST'])
def predict():
    try:
        data = request.get_json()

        attendance      = float(data['attendance'])
        assignment_avg  = float(data['assignment_avg'])
        midterm_score   = float(data['midterm_score'])
        hours_studied   = float(data['hours_studied'])
        prev_gpa        = float(data['prev_gpa'])
        sleep_hours     = float(data['sleep_hours'])
        extracurricular = int(data['extracurricular'])

        features = np.array([[
            attendance, assignment_avg, midterm_score,
            hours_studied, prev_gpa, sleep_hours, extracurricular
        ]])

        prediction = int(model.predict(features)[0])
        probabilities = model.predict_proba(features)[0]
        confidence = round(float(probabilities[prediction]) * 100, 1)

        result = LABELS[prediction]

        # Save to DB
        save_prediction(data, result['grade'], confidence)

        # Factor analysis
        factors = []
        if attendance < 75:
            factors.append({'label': 'Low Attendance', 'impact': 'negative', 'tip': 'Aim for at least 75% attendance'})
        elif attendance >= 90:
            factors.append({'label': 'Excellent Attendance', 'impact': 'positive', 'tip': 'Keep it up'})
        if hours_studied < 3:
            factors.append({'label': 'Low Study Hours', 'impact': 'negative', 'tip': 'Try to study at least 3-4 hours daily'})
        elif hours_studied >= 6:
            factors.append({'label': 'Strong Study Habit', 'impact': 'positive', 'tip': 'Consistency is key'})
        if midterm_score < 50:
            factors.append({'label': 'Midterm Performance', 'impact': 'negative', 'tip': 'Focus on understanding core concepts'})
        elif midterm_score >= 75:
            factors.append({'label': 'Strong Midterm Score', 'impact': 'positive', 'tip': 'Great foundation for finals'})
        if sleep_hours < 6:
            factors.append({'label': 'Insufficient Sleep', 'impact': 'negative', 'tip': 'Sleep 7-8 hours for better retention'})

        all_probs = [
            {'label': LABELS[i]['grade'], 'probability': round(float(p) * 100, 1), 'color': LABELS[i]['color']}
            for i, p in enumerate(probabilities)
        ]

        return jsonify({
            'prediction': result['grade'],
            'color': result['color'],
            'emoji': result['emoji'],
            'confidence': confidence,
            'advice': result['advice'],
            'factors': factors,
            'probabilities': all_probs
        })

    except KeyError as e:
        return jsonify({'error': f'Missing field: {str(e)}'}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/history')
def api_history():
    limit = request.args.get('limit', 50, type=int)
    return jsonify(get_history(limit))

@app.route('/api/stats')
def api_stats():
    return jsonify(get_stats())

@app.route('/api/clear', methods=['DELETE'])
def clear_history():
    conn = sqlite3.connect(DB_PATH)
    conn.execute('DELETE FROM predictions')
    conn.commit()
    conn.close()
    return jsonify({'status': 'cleared'})

@app.route('/health')
def health():
    return jsonify({'status': 'ok', 'model': 'loaded'})

if __name__ == '__main__':
    app.run(debug=True, port=5000)