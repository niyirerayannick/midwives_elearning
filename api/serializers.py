from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.core.validators import RegexValidator
from .models import HealthProviderUser, Course, Lesson, Quiz, Question, Answer, Exam, Certificate, Enrollment, Progress, Notification

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
class CourseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Course
        fields = ['id', 'title', 'description', 'instructor', 'created_at']

# Lesson Serializer
class LessonSerializer(serializers.ModelSerializer):
    class Meta:
        model = Lesson
        fields = ['id', 'course', 'title', 'video_url', 'content', 'pdf_file']

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
    class Meta:
        model = Enrollment
        fields = ['id', 'user', 'course', 'date_enrolled']

# Progress Serializer
class ProgressSerializer(serializers.ModelSerializer):
    class Meta:
        model = Progress
        fields = ['id', 'user', 'course', 'completed_lessons', 'total_lessons']

# Notification Serializer
class NotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notification
        fields = ['id', 'user', 'message', 'created_at', 'is_read']