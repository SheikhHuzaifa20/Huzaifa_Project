import base64
import os
import django
import random
from datetime import date, timedelta

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'edupredict.settings')
django.setup()

from django.conf import settings
from accounts.models import User
from dashboard.models import Student, Attendance, AcademicRecord, Notification, Course, EducationalDataset
from analytics.ml_engine import MLEngine

PLACEHOLDER_PNG_B64 = (
    'iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mNgYAAAAAMAAWgmWQ0A'
    'AAABJRU5ErkJggg=='
)

def ensure_placeholder_image():
    image_dir = os.path.join(settings.MEDIA_ROOT, 'profiles')
    os.makedirs(image_dir, exist_ok=True)
    image_path = os.path.join(image_dir, 'user_placeholder.png')
    if not os.path.exists(image_path):
        with open(image_path, 'wb') as f:
            f.write(base64.b64decode(PLACEHOLDER_PNG_B64))
    return 'profiles/user_placeholder.png'


def create_user(data):
    user, created = User.objects.get_or_create(
        username=data['username'],
        defaults={
            'email': data['email'],
            'role': data['role'],
            'first_name': data['first_name'],
            'last_name': data['last_name'],
            'phone': data['phone'],
            'profile_pic': data['profile_pic'],
            'is_approved': True,
            'is_staff': data.get('is_staff', False),
            'is_superuser': data.get('is_superuser', False),
        }
    )
    user.email = data['email']
    user.role = data['role']
    user.first_name = data['first_name']
    user.last_name = data['last_name']
    user.phone = data['phone']
    user.profile_pic = data['profile_pic']
    user.is_approved = True
    user.is_staff = data.get('is_staff', False)
    user.is_superuser = data.get('is_superuser', False)
    user.set_password(data['password'])
    user.save()
    return user, created


def create_notification(user, title, message, alert_type='INFO'):
    Notification.objects.get_or_create(
        user=user,
        title=title,
        message=message,
        defaults={'alert_type': alert_type}
    )


def create_dataset(course_user, title, file_name, description, hdfs_path):
    EducationalDataset.objects.get_or_create(
        title=title,
        defaults={
            'file': file_name,
            'uploaded_by': course_user,
            'description': description,
            'hdfs_path': hdfs_path,
        }
    )


def add_student_profile(user, student_id, department, semester, dob, address, courses):
    student, created = Student.objects.get_or_create(
        user=user,
        defaults={
            'student_id': student_id,
            'department': department,
            'semester': semester,
            'date_of_birth': dob,
            'address': address,
        }
    )
    if created:
        for course in courses:
            AcademicRecord.objects.create(
                student=student,
                course=course,
                grade=round(random.uniform(3.0, 4.0), 2),
                semester=semester,
                year=2024
            )
        for i in range(10):
            Attendance.objects.create(
                student=student,
                date=date.today() - timedelta(days=i),
                is_present=random.choice([True, True, True, False]),
                course=random.choice(courses)
            )
    return student


def populate_data():
    print('Populating complete demo data...')
    profile_image = ensure_placeholder_image()

    course_names = [
        ('Algorithms', 'CS101'),
        ('Database Systems', 'CS102'),
        ('Linear Algebra', 'MATH101'),
        ('Statistics', 'MATH201'),
    ]
    courses = []
    for name, code in course_names:
        course_obj, _ = Course.objects.get_or_create(
            name=name,
            code=code,
            defaults={'description': f'{name} course for demo students'}
        )
        courses.append(course_obj)

    users = [
        {
            'username': 'admin@example.com',
            'email': 'admin@example.com',
            'role': 'ADMIN',
            'first_name': 'Admin',
            'last_name': 'User',
            'phone': '0300-1111111',
            'profile_pic': profile_image,
            'password': 'password123',
            'is_staff': True,
            'is_superuser': True,
        },
        {
            'username': 'teacher@example.com',
            'email': 'teacher@example.com',
            'role': 'TEACHER',
            'first_name': 'Tahir',
            'last_name': 'Teacher',
            'phone': '0300-2222222',
            'profile_pic': profile_image,
            'password': 'password123',
        },
        {
            'username': 'student@example.com',
            'email': 'student@example.com',
            'role': 'STUDENT',
            'first_name': 'Sara',
            'last_name': 'Student',
            'phone': '0300-3333333',
            'profile_pic': profile_image,
            'password': 'password123',
        },
        {
            'username': 'analyst@example.com',
            'email': 'analyst@example.com',
            'role': 'ANALYST',
            'first_name': 'Ali',
            'last_name': 'Analyst',
            'phone': '0300-4444444',
            'profile_pic': profile_image,
            'password': 'password123',
        },
    ]

    created_users = {}
    for user_data in users:
        user, created = create_user(user_data)
        created_users[user_data['role']] = user
        state = 'Created' if created else 'Updated'
        print(f'{state} user {user.username} ({user.role})')

    additional_students = [
        {
            'username': 'student_arif',
            'email': 'student_arif@example.com',
            'first_name': 'Arif',
            'last_name': 'Khan',
            'phone': '0300-5555555',
            'dob': date(2004, 5, 12),
            'address': 'Block B, Green Town, Lahore',
            'department': 'Computer Science',
            'semester': 2,
        },
        {
            'username': 'student_fatima',
            'email': 'student_fatima@example.com',
            'first_name': 'Fatima',
            'last_name': 'Riaz',
            'phone': '0300-6666666',
            'dob': date(2003, 11, 3),
            'address': 'Street 12, Defence, Karachi',
            'department': 'Statistics',
            'semester': 4,
        },
        {
            'username': 'student_muhammad',
            'email': 'student_muhammad@example.com',
            'first_name': 'Muhammad',
            'last_name': 'Ali',
            'phone': '0300-7777777',
            'dob': date(2004, 2, 20),
            'address': 'Phase 1, Islamabad',
            'department': 'Mathematics',
            'semester': 1,
        },
        {
            'username': 'student_zaara',
            'email': 'student_zaara@example.com',
            'first_name': 'Zaara',
            'last_name': 'Naveed',
            'phone': '0300-8888888',
            'dob': date(2003, 8, 18),
            'address': 'Gulshan-e-Iqbal, Karachi',
            'department': 'Physics',
            'semester': 3,
        },
    ]

    student_profiles = []
    for student_data in additional_students:
        user_data = {
            'username': student_data['username'],
            'email': student_data['email'],
            'role': 'STUDENT',
            'first_name': student_data['first_name'],
            'last_name': student_data['last_name'],
            'phone': student_data['phone'],
            'profile_pic': profile_image,
            'password': 'password123',
        }
        user, created = create_user(user_data)
        student_profiles.append(add_student_profile(
            user=user,
            student_id=f'S{random.randint(10000, 99999)}',
            department=student_data['department'],
            semester=student_data['semester'],
            dob=student_data['dob'],
            address=student_data['address'],
            courses=courses,
        ))
        print(f"{'Created' if created else 'Updated'} student {user.username}")

    main_student_user = created_users['STUDENT']
    student_profiles.append(add_student_profile(
        user=main_student_user,
        student_id='S10001',
        department='Computer Science',
        semester=3,
        dob=date(2003, 9, 1),
        address='Street 5, Bahria Town, Lahore',
        courses=courses,
    ))

    if not EducationalDataset.objects.filter(title='Demo Educational Dataset').exists():
        create_dataset(
            course_user=created_users['ANALYST'],
            title='Demo Educational Dataset',
            file_name='datasets/sample_educational_data.csv',
            description='Sample dataset for analytics and ML demo.',
            hdfs_path='/hdfs/simulated/demo_educational_data.csv',
        )
        print('Created demo dataset entry')

    notifications = [
        (created_users['ADMIN'], 'Welcome Admin', 'Your admin dashboard is ready and sample data has been populated.', 'INFO'),
        (created_users['TEACHER'], 'New Student Records', 'Four new student profiles were added for teaching demos.', 'INFO'),
        (created_users['STUDENT'], 'Welcome Student', 'Your student dashboard and performance data are available.', 'INFO'),
        (created_users['ANALYST'], 'Analytics Ready', 'ML sample dataset and model are available for the analyst dashboard.', 'INFO'),
    ]
    for user, title, message, alert_type in notifications:
        create_notification(user, title, message, alert_type)

    for student in student_profiles:
        create_notification(student.user, 'Attendance Imported', 'Dummy attendance and academic record data are available.', 'INFO')

    print('Demo data population complete!')


if __name__ == '__main__':
    populate_data()
