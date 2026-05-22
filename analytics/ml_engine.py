import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import LabelEncoder
import joblib
import os
from django.conf import settings

class MLEngine:
    MODEL_DIR = os.path.join(settings.BASE_DIR, 'analytics', 'ml_models')
    
    def __init__(self):
        os.makedirs(self.MODEL_DIR, exist_ok=True)
        self.le_gender = LabelEncoder()
        self.le_dept = LabelEncoder()

    def preprocess_data(self, df):
        # Sample preprocessing logic
        # Expected columns: attendance_rate, mid_grade, assignment_score, gender, department, target (Pass/Fail)
        df = df.copy()
        
        if 'gender' in df.columns:
            df['gender'] = self.le_gender.fit_transform(df['gender'])
        if 'department' in df.columns:
            df['department'] = self.le_dept.fit_transform(df['department'])
            
        return df

    def train_performance_model(self, data_path):
        df = pd.read_csv(data_path)
        df = self.preprocess_data(df)
        
        X = df[['attendance_rate', 'mid_grade', 'assignment_score', 'gender', 'department']]
        y = df['performance_score'] # Target variable
        
        # Binary classification for simplicity: High (1) or Low (0) performance
        y_binary = (y > 60).astype(int)
        
        X_train, X_test, y_train, y_test = train_test_split(X, y_binary, test_size=0.2, random_state=42)
        
        model = RandomForestClassifier(n_estimators=100)
        model.fit(X_train, y_train)
        
        accuracy = model.score(X_test, y_test)
        
        # Save model
        model_path = os.path.join(self.MODEL_DIR, 'performance_model.pkl')
        joblib.dump(model, model_path)
        
        return accuracy

    def predict_performance(self, student_data):
        """
        student_data: dict with keys ['attendance_rate', 'mid_grade', 'assignment_score', 'gender', 'department']
        """
        model_path = os.path.join(self.MODEL_DIR, 'performance_model.pkl')
        if not os.path.exists(model_path):
            return None # Model not trained
            
        model = joblib.load(model_path)
        
        # Preprocess input (using same encoders - in a real app, these should be saved too)
        # For simplicity in this beginner project, we'll assume standard inputs
        
        # Dummy encoding for now if encoders aren't fitted
        gender_val = 1 if student_data['gender'].lower() == 'male' else 0
        dept_val = 1 # Simplified
        
        features = np.array([[
            student_data['attendance_rate'],
            student_data['mid_grade'],
            student_data['assignment_score'],
            gender_val,
            dept_val
        ]])
        
        prediction = model.predict(features)[0]
        probability = model.predict_proba(features)[0][1]
        
        return {
            'prediction': 'High' if prediction == 1 else 'Low',
            'confidence': round(probability * 100, 2)
        }

    def generate_sample_data(self, n=200):
        """Generates a sample dataset for training demo."""
        data = {
            'attendance_rate': np.random.uniform(50, 100, n),
            'mid_grade': np.random.uniform(30, 100, n),
            'assignment_score': np.random.uniform(40, 100, n),
            'gender': np.random.choice(['Male', 'Female'], n),
            'department': np.random.choice(['CS', 'Math', 'Physics', 'Bio'], n),
        }
        df = pd.DataFrame(data)
        # Logic: if attendance and grades are high, performance is high
        df['performance_score'] = (df['attendance_rate'] * 0.4 + df['mid_grade'] * 0.4 + df['assignment_score'] * 0.2) + np.random.normal(0, 5, n)
        
        os.makedirs(os.path.join(settings.BASE_DIR, 'data'), exist_ok=True)
        csv_path = os.path.join(settings.BASE_DIR, 'data', 'sample_educational_data.csv')
        df.to_csv(csv_path, index=False)
        return csv_path
