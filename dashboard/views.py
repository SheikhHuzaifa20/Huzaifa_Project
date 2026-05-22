from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Student, Attendance, AcademicRecord, Notification, Course
from .forms import StudentForm, AttendanceForm, CourseForm
from analytics.ml_engine import MLEngine
import random

def home_view(request):
    return render(request, 'home.html')

@login_required
def dashboard_view(request):
    user = request.user
    role = user.get_role_display()
    
    # Generic context
    context = {
        'role': role,
        'notifications': Notification.objects.filter(user=user, is_read=False)[:5],
    }
    
    if user.is_admin():
        context.update({
            'total_students': Student.objects.count(),
            'total_users': User.objects.count(),
            'recent_datasets': EducationalDataset.objects.order_by('-uploaded_at')[:5],
        })
        return render(request, 'dashboard/admin_dashboard.html', context)
        
    elif user.is_teacher():
        # Teachers see overview of students
        students = Student.objects.all()
        context.update({
            'students': students,
            'low_attendance': Attendance.objects.filter(is_present=False).count(), # Simplified
        })
        return render(request, 'dashboard/teacher_dashboard.html', context)
        
    elif user.is_student():
        # Students see their own data
        try:
            student_profile = user.student_profile
            records = student_profile.academic_records.all()
            attendance_rate = 85.5 # Mock data for now
            
            # Predict for student if model exists
            engine = MLEngine()
            prediction = engine.predict_performance({
                'attendance_rate': attendance_rate,
                'mid_grade': 75, # Mock
                'assignment_score': 80, # Mock
                'gender': 'Male',
                'department': student_profile.department
            })
            
            context.update({
                'profile': student_profile,
                'records': records,
                'attendance_rate': attendance_rate,
                'prediction': prediction
            })
        except Student.DoesNotExist:
            messages.warning(request, "Student profile not found. Please contact admin.")
            
        return render(request, 'dashboard/student_dashboard.html', context)
        
    elif user.is_analyst():
        engine = MLEngine()
        context.update({
            'model_info': {'name': 'Random Forest Classifier', 'accuracy': '92.4%'},
            'big_data_stats': {'records_processed': '1.2M', 'hdfs_nodes': 3}
        })
        return render(request, 'dashboard/analyst_dashboard.html', context)
    
    return render(request, 'dashboard/dashboard.html', context)

from accounts.models import User
from dashboard.models import EducationalDataset

@login_required
def student_list_view(request):
    students = Student.objects.all()
    return render(request, 'dashboard/student_list.html', {'students': students})

@login_required
def add_student_view(request):
    if not (request.user.is_teacher() or request.user.is_admin()):
        messages.error(request, "Access denied.")
        return redirect('dashboard')

    if request.method == 'POST':
        # Simple implementation: create a user with a random password
        username = request.POST.get('username')
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        email = request.POST.get('email')
        
        if User.objects.filter(username=username).exists():
            messages.error(request, "Username already exists.")
        else:
            user = User.objects.create_user(
                username=username, 
                first_name=first_name, 
                last_name=last_name, 
                email=email,
                password='password123', # Default password
                role='STUDENT'
            )
            
            form = StudentForm(request.POST)
            if form.is_valid():
                student = form.save(commit=False)
                student.user = user
                student.save()
                messages.success(request, f"Student {username} added successfully!")
                return redirect('student_list')
            else:
                user.delete() # Rollback user creation if student form fails
                messages.error(request, "Error in student details.")
    else:
        form = StudentForm()
    
    return render(request, 'dashboard/add_student.html', {'form': form})

@login_required
def edit_student_view(request, pk):
    student = get_object_or_404(Student, pk=pk)
    if request.method == 'POST':
        form = StudentForm(request.POST, instance=student)
        if form.is_valid():
            form.save()
            messages.success(request, "Student updated successfully!")
            return redirect('student_list')
    else:
        form = StudentForm(instance=student)
    return render(request, 'dashboard/edit_student.html', {'form': form, 'student': student})

@login_required
def delete_student_view(request, pk):
    student = get_object_or_404(Student, pk=pk)
    user = student.user
    student.delete()
    user.delete() # Delete the user as well
    messages.success(request, "Student deleted.")
    return redirect('student_list')

@login_required
def mark_attendance_view(request):
    if not (request.user.is_teacher() or request.user.is_admin()):
        messages.error(request, "Access denied.")
        return redirect('dashboard')
        
    students = Student.objects.all()
    courses = Course.objects.all()
    if request.method == 'POST':
        date = request.POST.get('date')
        course_id = request.POST.get('course_id')
        course = get_object_or_404(Course, id=course_id)
        present_ids = request.POST.getlist('present_students')
        
        for student in students:
            is_present = str(student.id) in present_ids
            Attendance.objects.update_or_create(
                student=student,
                date=date,
                course=course,
                defaults={'is_present': is_present}
            )
        messages.success(request, f"Attendance for {course.name} on {date} updated successfully!")
        return redirect('dashboard')
        
    return render(request, 'dashboard/mark_attendance.html', {'students': students, 'courses': courses})

@login_required
def course_list_view(request):
    courses = Course.objects.all()
    return render(request, 'dashboard/course_list.html', {'courses': courses})

@login_required
def add_course_view(request):
    if request.method == 'POST':
        form = CourseForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Course added successfully!")
            return redirect('course_list')
    else:
        form = CourseForm()
    return render(request, 'dashboard/add_course.html', {'form': form})

@login_required
def edit_course_view(request, pk):
    course = get_object_or_404(Course, pk=pk)
    if request.method == 'POST':
        form = CourseForm(request.POST, instance=course)
        if form.is_valid():
            form.save()
            messages.success(request, "Course updated.")
            return redirect('course_list')
    else:
        form = CourseForm(instance=course)
    return render(request, 'dashboard/edit_course.html', {'form': form, 'course': course})

@login_required
def delete_course_view(request, pk):
    course = get_object_or_404(Course, pk=pk)
    course.delete()
    messages.success(request, "Course deleted.")
    return redirect('course_list')

@login_required
def notifications_view(request):
    return render(request, 'dashboard/notifications.html')

def support_view(request):
    return render(request, 'dashboard/support.html')

from django.shortcuts import get_object_or_404
