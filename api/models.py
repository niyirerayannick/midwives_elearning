from django.contrib.auth.models import AbstractUser
from django.db import models
from django.core.exceptions import ValidationError
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
            regex=r'^LIC\d{3,6}RW$',  # Updated regex to allow 3 to 6 digits
            message='Registration number must be in the format: LICXXXRW to LICXXXXRW (e.g., LIC123RW, LIC1234RW, LIC123456RW)'
        )],
    )
    
    first_name = models.CharField(max_length=50, null=True, blank=True)
    last_name = models.CharField(max_length=50, null=True, blank=True)
    email = models.EmailField(unique=True, null=True, blank=True)
    telephone = models.CharField(max_length=15, null=True, blank=True)
    date_of_birth = models.DateField(null=True, blank=True)
    profile_image = models.ImageField(upload_to='profile_images/', null=True, blank=True)  # Ensure this line is present

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
    
class Skill(models.Model):
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name
    
class Course(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField()
    instructor = models.ForeignKey('HealthProviderUser', related_name='courses', on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    cpd = models.PositiveIntegerField()
    skills = models.ManyToManyField(Skill, related_name='courses', blank=True)  # New field for skills
    course_image = models.ImageField(upload_to='course_images/', null=True, blank=True)
    category = models.ForeignKey(Category, related_name='courses', on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self):
        return self.title

def validate_video_file(value):
    # Remove file size check, only check for allowed extensions
    if not value.name.endswith(('.mp4', '.avi', '.mkv', '.mov')):
        raise ValidationError("Only video files (.mp4, .avi, .mkv, .mov) are allowed.")

def validate_audio_file(value):
    # Remove file size check, only check for allowed extensions
    if not value.name.endswith(('.mp3', '.wav', '.aac')):
        raise ValidationError("Only audio files (.mp3, .wav, .aac) are allowed.")


class Lesson(models.Model):
    title = models.CharField(max_length=255, verbose_name="Lesson Title", help_text="The title of the lesson")
    course = models.ForeignKey(Course, related_name='lessons', on_delete=models.CASCADE, verbose_name="Related Course")
    video_file = models.FileField(upload_to='lessons/videos/', blank=True, null=True, verbose_name="Video File", help_text="Optional video file for the lesson")
    audio_file = models.FileField(upload_to='lessons/audios/', blank=True, null=True, verbose_name="Audio File", help_text="Optional audio file for the lesson")
    readings = models.TextField(blank=True, null=True, verbose_name="Readings", help_text="Optional text-based lesson content")
    pdf_file = models.FileField(upload_to='lessons/pdfs/', blank=True, null=True, verbose_name="PDF File", help_text="Optional PDF file for lesson")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Date Created")

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = "Lesson"
        verbose_name_plural = "Lessons"
        ordering = ['created_at']
        constraints = [
            models.UniqueConstraint(fields=['title', 'course'], name='unique_lesson_title_in_course')
        ]

    def save(self, *args, **kwargs):
        self.clean()
        super(Lesson, self).save(*args, **kwargs)

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

class Grade(models.Model):
    user = models.ForeignKey(HealthProviderUser, related_name='grades', on_delete=models.CASCADE)
    course = models.ForeignKey(Course, related_name='grades', on_delete=models.CASCADE)
    quiz = models.ForeignKey(Quiz, related_name='grades', null=True, blank=True, on_delete=models.SET_NULL)
    exam = models.ForeignKey(Exam, related_name='grades', null=True, blank=True, on_delete=models.SET_NULL)
    score = models.DecimalField(max_digits=5, decimal_places=2)  # The score achieved
    total_score = models.IntegerField()  # The total possible score

    @property
    def percentage(self):
        return (self.score / self.total_score) * 100 if self.total_score > 0 else 0

    def __str__(self):
        return f"{self.user} - {self.course} - {self.score}/{self.total_score}"

# Notification Model
class Notification(models.Model):
    user = models.ForeignKey('HealthProviderUser', related_name='notifications', on_delete=models.CASCADE)
    message = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)

    def __str__(self):
        return f"Notification for {self.user.registration_number}"

class Update(models.Model):
    title = models.CharField(max_length=255)
    content = models.TextField()
    author = models.ForeignKey('HealthProviderUser', related_name='updates', on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    cover_image = models.ImageField(upload_to='updates/covers/', blank=True, null=True)
    file = models.FileField(upload_to='updates/files/', blank=True, null=True)

    def __str__(self):
        return self.title

    def total_likes(self):
        return self.likes.count()

    def total_comments(self):
        return self.comments.count()


class Comment(models.Model):
    update = models.ForeignKey(Update, related_name='comments', on_delete=models.CASCADE)
    author = models.ForeignKey('HealthProviderUser', on_delete=models.CASCADE)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'Comment by {self.author} on {self.update}'


class Like(models.Model):
    update = models.ForeignKey(Update, related_name='likes', on_delete=models.CASCADE)
    user = models.ForeignKey('HealthProviderUser', on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('update', 'user')  # Ensures that a user can like an update only once

    def __str__(self):
        return f'{self.user} likes {self.update}'