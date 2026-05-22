from django.db import models
from django.conf import settings

class Student(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='student_profile')
    student_id = models.CharField(max_length=20, unique=True)
    department = models.CharField(max_length=100)
    semester = models.IntegerField(default=1)
    date_of_birth = models.DateField(null=True, blank=True)
    address = models.TextField(null=True, blank=True)
    
    def __str__(self):
        return f"{self.user.get_full_name()} ({self.student_id})"

class Course(models.Model):
    name = models.CharField(max_length=100, unique=True)
    code = models.CharField(max_length=20, unique=True)
    description = models.TextField(blank=True)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def __str__(self):
        return f"{self.name} ({self.code})"

class Attendance(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='attendances')
    date = models.DateField()
    is_present = models.BooleanField(default=True)
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='attendances', null=True, blank=True)

    class Meta:
        unique_together = ('student', 'date', 'course')

    def __str__(self):
        return f"{self.student.student_id} - {self.date} - {self.course.name if self.course else 'No Course'}"

class AcademicRecord(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='academic_records')
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='academic_records', null=True, blank=True)
    grade = models.FloatField()  # e.g., GPA or marks
    semester = models.IntegerField()
    year = models.IntegerField()

    def __str__(self):
        course_name = self.course.name if self.course else 'No Course'
        return f"{self.student.student_id} - {course_name} ({self.grade})"

class EducationalDataset(models.Model):
    title = models.CharField(max_length=255)
    file = models.FileField(upload_to='datasets/')
    uploaded_at = models.DateTimeField(auto_now_add=True)
    uploaded_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)
    description = models.TextField(blank=True)
    hdfs_path = models.CharField(max_length=500, blank=True) # Simulated HDFS path

    def __str__(self):
        return self.title

class Notification(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='notifications')
    title = models.CharField(max_length=255)
    message = models.TextField()
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    alert_type = models.CharField(max_length=20, choices=[('INFO', 'Info'), ('WARNING', 'Warning'), ('DANGER', 'Danger')], default='INFO')

    def __str__(self):
        return f"{self.user.username} - {self.title}"

class Feedback(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)
    name = models.CharField(max_length=100)
    email = models.EmailField()
    subject = models.CharField(max_length=255)
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} - {self.subject}"
