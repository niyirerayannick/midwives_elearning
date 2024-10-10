from django.contrib.auth.models import AbstractUser
from django.db import models
from django.core.validators import RegexValidator

class HealthProviderUser(AbstractUser):
    ROLE_CHOICES = [
        ('admin', 'Admin'),
        ('instructor', 'Instructor'),
        ('student', 'Student'),
    ]

    # Define registration number as the primary field for authentication
    registration_number = models.CharField(
        max_length=10, 
        unique=True, 
        validators=[RegexValidator(
            regex=r'^LIC\d{4}RW$', 
            message='Registration number must be in the format: LICXXXXRW (e.g., LIC1063RW)'
        )],
    )

    first_name = models.CharField(max_length=50, null=True, blank=True)
    last_name = models.CharField(max_length=50, null=True, blank=True)
    email = models.EmailField(unique=True, null=True, blank=True)
    telephone = models.CharField(max_length=15, null=True, blank=True)
    date_of_birth = models.DateField(null=True, blank=True)

    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='student')

    # Remove username as it's no longer the primary field
    username = None

    # Override related_name for groups and permissions to avoid conflicts
    groups = models.ManyToManyField(
        'auth.Group', related_name='healthprovideruser_set', blank=True)
    user_permissions = models.ManyToManyField(
        'auth.Permission', related_name='healthprovideruser_set', blank=True)

    # Set registration_number as the field for authentication
    USERNAME_FIELD = 'registration_number'
    REQUIRED_FIELDS = ['email', 'first_name', 'last_name']

    def save(self, *args, **kwargs):
        # Automatically generate registration number for students if not provided
        if self.role == 'student' and not self.registration_number:
            last_user_id = HealthProviderUser.objects.filter(role='student').count() + 1
            self.registration_number = f"LIC{1000 + last_user_id}RW"
        
        # Set the registration number as the initial password if not explicitly set
        if not self.pk and self.registration_number:
            self.set_password(self.registration_number)
        
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.registration_number} - {self.get_role_display()}"

# Course Model

class Course(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField()  # Add description field
    instructor = models.ForeignKey('HealthProviderUser', related_name='courses', on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)  # Add created_at for course

    def __str__(self):
        return self.title


class Lesson(models.Model):
    title = models.CharField(max_length=255)
    course = models.ForeignKey(Course, related_name='lessons', on_delete=models.CASCADE)
    video_url = models.URLField(max_length=500, blank=True, null=True)  # Optional field for videos
    content = models.TextField()
    pdf_file = models.FileField(upload_to='lessons/pdfs/', blank=True, null=True)  # Add pdf_file field
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title

# Quiz Model
class Quiz(models.Model):
    course = models.ForeignKey(Course, related_name='quizzes', on_delete=models.CASCADE)
    title = models.CharField(max_length=255)
    total_marks = models.PositiveIntegerField()

    def __str__(self):
        return f"{self.title} ({self.course.title})"

# Question Model (For Quizzes)
class Question(models.Model):
    quiz = models.ForeignKey(Quiz, related_name='questions', on_delete=models.CASCADE)
    text = models.CharField(max_length=500)
    is_multiple_choice = models.BooleanField(default=False)

    def __str__(self):
        return self.text

# Answer Model (For Questions)
class Answer(models.Model):
    question = models.ForeignKey(Question, related_name='answers', on_delete=models.CASCADE)
    text = models.CharField(max_length=500)
    is_correct = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.text} ({'Correct' if self.is_correct else 'Incorrect'})"

# Exam Model (Final Exam for a Course)
class Exam(models.Model):
    course = models.ForeignKey(Course, related_name='exams', on_delete=models.CASCADE)
    title = models.CharField(max_length=255)
    total_marks = models.PositiveIntegerField()

    def __str__(self):
        return f"{self.title} ({self.course.title})"

# Certificate Model (Issued after course completion)
class Certificate(models.Model):
    user = models.ForeignKey('HealthProviderUser', related_name='certificates', on_delete=models.CASCADE)
    course = models.ForeignKey(Course, related_name='certificates', on_delete=models.CASCADE)
    date_issued = models.DateField(auto_now_add=True)
    certificate_file = models.FileField(upload_to='certificates/', null=True, blank=True)

    def __str__(self):
        return f"Certificate for {self.user.username} - {self.course.title}"

# Enrollment Model (For tracking user enrollment in courses)
class Enrollment(models.Model):
    user = models.ForeignKey('HealthProviderUser', related_name='enrollments', on_delete=models.CASCADE)
    course = models.ForeignKey(Course, related_name='enrollments', on_delete=models.CASCADE)
    date_enrolled = models.DateField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} enrolled in {self.course.title}"

# Progress Model (To track student progress in a course)
class Progress(models.Model):
    user = models.ForeignKey('HealthProviderUser', related_name='progress', on_delete=models.CASCADE)
    course = models.ForeignKey(Course, related_name='progress', on_delete=models.CASCADE)
    completed_lessons = models.IntegerField(default=0)
    total_lessons = models.IntegerField()

    def __str__(self):
        return f"{self.user.username}'s progress in {self.course.title}"

# Notification Model (For user notifications, such as course updates, certificates)
class Notification(models.Model):
    user = models.ForeignKey('HealthProviderUser', related_name='notifications', on_delete=models.CASCADE)
    message = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)

    def __str__(self):
        return f"Notification for {self.user.username}"