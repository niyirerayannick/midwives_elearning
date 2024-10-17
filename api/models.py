from django.contrib.auth.models import AbstractUser
from django.db import models
from django.core.validators import RegexValidator
from django.contrib.auth.models import BaseUserManager

class HealthProviderUserManager(BaseUserManager):
    def create_superuser(self, registration_number, password=None, **extra_fields):
        """
        Create and return a superuser with a registration number and password.
        """
        if not registration_number:
            raise ValueError('The given registration number must be set')
        
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        user = self.model(registration_number=registration_number, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

class HealthProviderUser(AbstractUser):
    ROLE_CHOICES = [
        ('admin', 'Admin'),
        ('instructor', 'Instructor'),
        ('student', 'Student'),
    ]

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

    username = None

    objects = HealthProviderUserManager() 

    groups = models.ManyToManyField(
        'auth.Group', related_name='healthprovideruser_set', blank=True)
    user_permissions = models.ManyToManyField(
        'auth.Permission', related_name='healthprovideruser_set', blank=True)

    USERNAME_FIELD = 'registration_number'
    REQUIRED_FIELDS = ['email', 'first_name', 'last_name']

    def save(self, *args, **kwargs):
        if self.role == 'student' and not self.registration_number:
            last_user_id = HealthProviderUser.objects.filter(role='student').count() + 1
            self.registration_number = f"LIC{1000 + last_user_id}RW"
        
        if not self.pk and self.registration_number:
            self.set_password(self.registration_number)
        
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.registration_number} - {self.get_role_display()}"

class Category(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.name

class Course(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField()
    instructor = models.ForeignKey('HealthProviderUser', related_name='courses', on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    course_image = models.ImageField(upload_to='course_images/', null=True, blank=True)
    category = models.ForeignKey(Category, related_name='courses', on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self):
        return self.title

class Lesson(models.Model):
    title = models.CharField(max_length=255)
    course = models.ForeignKey(Course, related_name='lessons', on_delete=models.CASCADE)
    video_url = models.URLField(max_length=500, blank=True, null=True)
    content = models.TextField()
    pdf_file = models.FileField(upload_to='lessons/pdfs/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title

class Quiz(models.Model):
    course = models.ForeignKey(Course, related_name='quizzes', on_delete=models.CASCADE)
    title = models.CharField(max_length=255)
    total_marks = models.PositiveIntegerField()

    def __str__(self):
        return f"{self.title} ({self.course.title})"

class Question(models.Model):
    quiz = models.ForeignKey(Quiz, related_name='questions', on_delete=models.CASCADE)
    text = models.CharField(max_length=500)
    is_multiple_choice = models.BooleanField(default=False)

    def __str__(self):
        return self.text

class Answer(models.Model):
    question = models.ForeignKey(Question, related_name='answers', on_delete=models.CASCADE)
    text = models.CharField(max_length=500)
    is_correct = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.text} ({'Correct' if self.is_correct else 'Incorrect'})"

class UserAnswer(models.Model):
    user = models.ForeignKey('HealthProviderUser', on_delete=models.CASCADE)
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    selected_choice = models.ForeignKey(Answer, on_delete=models.CASCADE)
    is_correct = models.BooleanField(default=False)

    class Meta:
        unique_together = ('user', 'question')

class Exam(models.Model):
    course = models.ForeignKey(Course, related_name='exams', on_delete=models.CASCADE)
    title = models.CharField(max_length=255)
    total_marks = models.PositiveIntegerField()

    def __str__(self):
        return f"{self.title} ({self.course.title})"

class Certificate(models.Model):
    user = models.ForeignKey('HealthProviderUser', related_name='certificates', on_delete=models.CASCADE)
    course = models.ForeignKey(Course, related_name='certificates', on_delete=models.CASCADE)
    date_issued = models.DateField(auto_now_add=True)
    certificate_file = models.FileField(upload_to='certificates/', null=True, blank=True)

    def __str__(self):
        return f"Certificate for {self.user.username} - {self.course.title}"

class Enrollment(models.Model):
    user = models.ForeignKey('HealthProviderUser', related_name='enrollments', on_delete=models.CASCADE)
    course = models.ForeignKey(Course, related_name='enrollments', on_delete=models.CASCADE)
    date_enrolled = models.DateField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} enrolled in {self.course.title}"

class Progress(models.Model):
    user = models.ForeignKey('HealthProviderUser', related_name='progress', on_delete=models.CASCADE)
    course = models.ForeignKey(Course, related_name='progress', on_delete=models.CASCADE)
    completed_lessons = models.JSONField(default=list)  # Store completed lesson IDs
    completed_quizzes = models.JSONField(default=list)  # Store completed quiz IDs
    total_lessons = models.IntegerField()

    def __str__(self):
        return f"{self.user.username}'s progress in {self.course.title}"
    
    def update_progress(self, item_type, item_id):
        if item_type == 'lesson':
            if item_id not in self.completed_lessons:
                self.completed_lessons.append(item_id)
        elif item_type == 'quiz':
            if item_id not in self.completed_quizzes:
                self.completed_quizzes.append(item_id)
        self.save()

# Notification Model
class Notification(models.Model):
    user = models.ForeignKey('HealthProviderUser', related_name='notifications', on_delete=models.CASCADE)
    message = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)

    def __str__(self):
        return f"Notification for {self.user.registration_number}"

