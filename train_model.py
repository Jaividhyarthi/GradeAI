"""
train_model.py
Run this once to generate model.pkl
Command: python train_model.py
"""

import numpy as np
import pickle
from sklearn.ensemble import GradientBoostingClassifier
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import Pipeline
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report

np.random.seed(42)
N = 2000

attendance     = np.random.randint(40, 101, N)
assignment_avg = np.random.randint(20, 101, N)
midterm_score  = np.random.randint(20, 101, N)
hours_studied  = np.random.uniform(0, 12, N)
prev_gpa       = np.random.uniform(2.0, 4.0, N)
sleep_hours    = np.random.uniform(3, 9, N)
extracurricular= np.random.randint(0, 2, N)  # 0 or 1

# Score formula with some noise
score = (
    0.25 * attendance +
    0.20 * assignment_avg +
    0.25 * midterm_score +
    0.15 * hours_studied * 8 +
    0.10 * (prev_gpa / 4.0) * 100 +
    0.05 * sleep_hours * 10 -
    0.05 * extracurricular * 10 +
    np.random.normal(0, 5, N)
)

# Labels: 0=Fail, 1=Pass, 2=Merit, 3=Distinction
def label(s):
    if s < 40:   return 0
    elif s < 60: return 1
    elif s < 75: return 2
    else:        return 3

labels = np.array([label(s) for s in score])

X = np.column_stack([
    attendance, assignment_avg, midterm_score,
    hours_studied, prev_gpa, sleep_hours, extracurricular
])

X_train, X_test, y_train, y_test = train_test_split(X, labels, test_size=0.2, random_state=42)

pipeline = Pipeline([
    ('scaler', StandardScaler()),
    ('model', GradientBoostingClassifier(n_estimators=200, max_depth=4, random_state=42))
])

pipeline.fit(X_train, y_train)
y_pred = pipeline.predict(X_test)

print("=== Model Performance ===")
print(classification_report(y_test, y_pred, target_names=['Fail','Pass','Merit','Distinction']))

with open('model.pkl', 'wb') as f:
    pickle.dump(pipeline, f)

print("model.pkl saved successfully.")
