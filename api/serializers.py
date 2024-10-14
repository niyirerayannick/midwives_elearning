from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.core.validators import RegexValidator
from .models import Category, HealthProviderUser, Course, Lesson, Quiz, Question, Answer, Exam, Certificate, Enrollment, Progress, Notification

User = get_user_model()

class UserSerializer(serializers.ModelSerializer):
    registration_number = serializers.CharField(
        required=True,
        validators=[RegexValidator(
            regex=r'^LIC\d{4}RW$', 
            message='Registration number must be in the format: LICXXXXRW (e.g., LIC1063RW)'
        )]
    )

    class Meta:
        model = User
        fields = ['registration_number', 'first_name', 'last_name', 'email', 'telephone', 'date_of_birth', 'role']

    def create(self, validated_data):
        """
        Override the create method to handle password setting logic.
        """
        user = super().create(validated_data)
        if 'password' in validated_data:
            user.set_password(validated_data['password'])  # Ensure the password is hashed
        user.save()
        return user

class LoginSerializer(serializers.Serializer):
    registration_number = serializers.CharField(
        required=True,
        validators=[RegexValidator(
            regex=r'^LIC\d{4}RW$', 
            message='Registration number must be in the format: LICXXXXRW (e.g., LIC1063RW)'
        )]
    )
    password = serializers.CharField(required=True)

class ChangePasswordSerializer(serializers.Serializer):
    user_id = serializers.IntegerField(required=True)  # Added user_id to identify the user
    new_password = serializers.CharField(required=True, write_only=True)
    confirm_password = serializers.CharField(required=True, write_only=True)

    def validate(self, data):
        """
        Custom validation to check if the new_password and confirm_password match.
        """
        if data['new_password'] != data['confirm_password']:
            raise serializers.ValidationError("The new password and confirmation password do not match.")
        return data

    def save(self):
        """
        Change the password for the user identified by user_id.
        """
        user_id = self.validated_data['user_id']
        new_password = self.validated_data['new_password']

        try:
            user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            raise serializers.ValidationError("User not found.")

        # Ensure that the password is only changed for the correct user (the logged-in user or an admin)
        request_user = self.context['request'].user

        # Allow password change if the logged-in user is the same as the user_id or an admin
        if user != request_user and not request_user.is_staff:
            raise serializers.ValidationError("You do not have permission to change this user's password.")

        # Change the password
        user.set_password(new_password)
        user.save()

        return user
# Course Serializer

class InstructorSerializer(serializers.ModelSerializer):
    full_name = serializers.SerializerMethodField()

    class Meta:
        model = HealthProviderUser
        fields = ['id', 'full_name', 'registration_number', 'email', 'telephone']

    def get_full_name(self, obj):
        return f"{obj.first_name} {obj.last_name}"
# Category Serializer
class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'name', 'description']
class CourseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Course
        fields = ['id', 'title', 'description', 'created_at', 'course_image']
# Lesson Serializer
class LessonSerializer(serializers.ModelSerializer):
    class Meta:
        model = Lesson
        fields = ['id', 'title', 'video_url', 'content', 'pdf_file', 'created_at']

# Quiz Serializer
class QuizSerializer(serializers.ModelSerializer):
    class Meta:
        model = Quiz
        fields = ['id', 'course', 'title', 'total_marks']

# Question Serializer
class QuestionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Question
        fields = ['id', 'quiz', 'text', 'is_multiple_choice']

# Answer Serializer
class AnswerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Answer
        fields = ['id', 'question', 'text', 'is_correct']

# Exam Serializer
class ExamSerializer(serializers.ModelSerializer):
    class Meta:
        model = Exam
        fields = ['id', 'course', 'title', 'total_marks']

# Certificate Serializer
class CertificateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Certificate
        fields = ['id', 'user', 'course', 'date_issued', 'certificate_file']

# Enrollment Serializer
class EnrollmentSerializer(serializers.ModelSerializer):
    # Extract specific fields from the related User model
    user_id = serializers.IntegerField(source='user.id', read_only=True)
    user_email = serializers.EmailField(source='user.email', read_only=True)
    user_name = serializers.CharField(source='user.get_full_name', read_only=True)

    # Include course details using CourseSerializer without source argument
    course = CourseSerializer(read_only=True)  # No need for source='course'

    class Meta:
        model = Enrollment
        fields = ['id', 'user_id', 'user_email', 'user_name', 'course', 'date_enrolled']

# Progress Serializer
class ProgressSerializer(serializers.ModelSerializer):
    user_name = serializers.CharField(source='user.get_full_name', read_only=True)

    class Meta:
        model = Progress
        fields = ['id', 'user_name', 'course', 'completed_lessons', 'total_lessons']
# Notification Serializer
class NotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notification
        fields = ['id', 'user', 'message', 'created_at', 'is_read']

# Course Serializer
class CourseSerializer(serializers.ModelSerializer):
    category = CategorySerializer()  # Nested Category
    lessons = LessonSerializer(many=True)  # Nested lessons (chapters)
    enrollments = EnrollmentSerializer(many=True)  # Nested enrollments
    instructor = InstructorSerializer()
    class Meta:
        model = Course
        fields = [
            'id', 'title', 'description', 'course_image', 'created_at', 'category',
            'lessons', 'instructor', 'enrollments'
        ]