# GradeAI — Student Performance Predictor

A full-stack AI/ML web application that predicts student academic performance based on key academic and lifestyle inputs. Built with Python (Flask + scikit-learn) backend and a clean, dark-themed frontend.

---

## Features

- Predicts result as Fail / Pass / Merit / Distinction
- Confidence score for each prediction
- Probability breakdown across all outcomes
- Key factor analysis with actionable tips
- Responsive dark UI — works on desktop and mobile
- REST API backend — easily extendable

---

## Project Structure

```
student-predictor/
├── app.py                  — Flask backend + prediction API
├── train_model.py          — ML model training script
├── model.pkl               — Trained model (auto-generated)
├── requirements.txt        — Python dependencies
├── templates/
│   └── index.html          — Frontend HTML
├── static/
│   ├── css/styles.css      — All styling
│   └── js/app.js           — Frontend logic
└── README.md
```

---

## Setup & Run

### 1. Install dependencies
```bash
pip install -r requirements.txt
```

### 2. Train the model (only needed once)
```bash
python train_model.py
```
This generates `model.pkl` with ~71% accuracy on test data.

### 3. Run the app
```bash
python app.py
```

Open your browser at `http://localhost:5000`

---

## API Reference

### POST /predict
**Request body (JSON):**
```json
{
  "attendance": 85,
  "assignment_avg": 78,
  "midterm_score": 72,
  "hours_studied": 4,
  "prev_gpa": 3.2,
  "sleep_hours": 7,
  "extracurricular": 0
}
```

**Response:**
```json
{
  "prediction": "Merit",
  "color": "#2ecc71",
  "emoji": "✓",
  "confidence": 68.4,
  "advice": "Good performance. Push your midterm preparation...",
  "factors": [...],
  "probabilities": [...]
}
```

---

## Model Details

- **Algorithm:** Gradient Boosting Classifier (scikit-learn)
- **Training data:** 2,000 synthetic student profiles
- **Features:** Attendance, Assignment Average, Midterm Score, Study Hours, Previous GPA, Sleep Hours, Extracurricular
- **Classes:** Fail, Pass, Merit, Distinction
- **Accuracy:** ~71% on held-out test set

---

## Tech Stack

- **Backend:** Python, Flask, scikit-learn, NumPy
- **Frontend:** Vanilla HTML, CSS, JavaScript
- **Fonts:** Clash Display + Cabinet Grotesk

---

Built by Jaividhyarthi Vivekanand
