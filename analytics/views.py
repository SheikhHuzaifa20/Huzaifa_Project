from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .services import HDFSSimulator
from .ml_engine import MLEngine
from dashboard.models import EducationalDataset

@login_required
def analytics_view(request):
    if request.user.is_student():
        messages.error(request, "Students are not authorized to access the Analytics module.")
        return redirect('dashboard')
        
    engine = MLEngine()
    # Check if model exists
    model_trained = os.path.exists(os.path.join(engine.MODEL_DIR, 'performance_model.pkl'))
    
    context = {
        'model_trained': model_trained,
        'hdfs_files': HDFSSimulator.list_files()
    }
    return render(request, 'analytics/analytics.html', context)

@login_required
def upload_data_view(request):
    if not (request.user.is_admin() or request.user.is_analyst() or request.user.is_teacher()):
        messages.error(request, "Only authorized roles can upload educational datasets.")
        return redirect('dashboard')

    if request.method == 'POST' and request.FILES.get('dataset'):
        uploaded_file = request.FILES['dataset']
        title = request.POST.get('title', uploaded_file.name)
        
        # Store in simulated HDFS
        hdfs_rel_path = HDFSSimulator.store_file(uploaded_file, title)
        
        # Save record in DB
        dataset = EducationalDataset.objects.create(
            title=title,
            file=uploaded_file,
            uploaded_by=request.user,
            hdfs_path=hdfs_rel_path
        )
        
        messages.success(request, f"Dataset '{title}' uploaded and partitioned in HDFS.")
        
        # Trigger training if requested
        if 'train_model' in request.POST:
            engine = MLEngine()
            abs_path = os.path.join(settings.BASE_DIR, hdfs_rel_path)
            try:
                accuracy = engine.train_performance_model(abs_path)
                messages.success(request, f"Model trained successfully! Accuracy: {accuracy*100:.2f}%")
            except Exception as e:
                messages.error(request, f"Training failed: {str(e)}")
        
        return redirect('analytics')
        
    return render(request, 'analytics/upload.html')

@login_required
def analyze_dataset_view(request):
    if not (request.user.is_admin() or request.user.is_analyst()):
        messages.error(request, "Only Analysts and Admins can run dataset analysis.")
        return redirect('analytics')
    file_path = request.GET.get('file')
    if not file_path:
        messages.error(request, "No file specified for analysis.")
        return redirect('analytics')

    abs_path = os.path.join(settings.BASE_DIR, 'hdfs_simulation', 'data', file_path)
    if not os.path.exists(abs_path):
        messages.error(request, "File not found in HDFS storage.")
        return redirect('analytics')

    try:
        df = pd.read_csv(abs_path)
        stats = {
            'total_records': len(df),
            'avg_attendance': round(df['attendance_rate'].mean(), 2) if 'attendance_rate' in df.columns else 'N/A',
            'avg_mid_grade': round(df['mid_grade'].mean(), 2) if 'mid_grade' in df.columns else 'N/A',
            'top_department': df['department'].mode()[0] if 'department' in df.columns else 'N/A',
        }
        
        # Sample predictions for the first 5 rows
        engine = MLEngine()
        sample_results = []
        if 'attendance_rate' in df.columns and os.path.exists(os.path.join(engine.MODEL_DIR, 'performance_model.pkl')):
            for _, row in df.head(5).iterrows():
                pred = engine.predict_performance({
                    'attendance_rate': row['attendance_rate'],
                    'mid_grade': row['mid_grade'],
                    'assignment_score': row.get('assignment_score', 70),
                    'gender': row.get('gender', 'Male'),
                    'department': row.get('department', 'CS')
                })
                sample_results.append({
                    'name': f"Student {_+1}",
                    'prediction': pred['prediction'],
                    'confidence': pred['confidence']
                })

        return render(request, 'analytics/results.html', {
            'file_name': os.path.basename(file_path),
            'stats': stats,
            'sample_results': sample_results
        })
    except Exception as e:
        messages.error(request, f"Analysis failed: {str(e)}")
        return redirect('analytics')

import pandas as pd
import os
from django.conf import settings
