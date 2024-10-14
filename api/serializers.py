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
        Create a new user, ensuring the password is hashed.
        """
        user = super().create(validated_data)
        if 'password' in validated_data:
            user.set_password(validated_data['password'])  # Hash the password
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
    user_id = serializers.IntegerField(required=True)
    new_password = serializers.CharField(required=True, write_only=True)
    confirm_password = serializers.CharField(required=True, write_only=True)

    def validate(self, data):
        """
        Ensure the new password and confirmation match.
        """
        if data['new_password'] != data['confirm_password']:
            raise serializers.ValidationError("The new password and confirmation password do not match.")
        return data

    def save(self):
        """
        Change the password for the identified user.
        """
        user_id = self.validated_data['user_id']
        new_password = self.validated_data['new_password']

        try:
            user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            raise serializers.ValidationError("User not found.")

        request_user = self.context['request'].user

        # Check permissions
        if user != request_user and not request_user.is_staff:
            raise serializers.ValidationError("You do not have permission to change this user's password.")

        # Change the password
        user.set_password(new_password)
        user.save()
        return user

class InstructorSerializer(serializers.ModelSerializer):
    full_name = serializers.SerializerMethodField()

    class Meta:
        model = HealthProviderUser  # Ensure this points to your actual instructor model
        fields = ['id', 'full_name', 'registration_number', 'email', 'telephone']

    def get_full_name(self, obj):
        """
        Return the full name of the instructor.
        """
        return f"{obj.first_name} {obj.last_name}"

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'name', 'description']

class LessonSerializer(serializers.ModelSerializer):
    class Meta:
        model = Lesson
        fields = ['id', 'title', 'video_url', 'content', 'pdf_file', 'created_at']

class QuizSerializer(serializers.ModelSerializer):
    class Meta:
        model = Quiz
        fields = ['id', 'course', 'title', 'total_marks']

class QuestionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Question
        fields = ['id', 'quiz', 'text', 'is_multiple_choice']

class AnswerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Answer
        fields = ['id', 'question', 'text', 'is_correct']

class ExamSerializer(serializers.ModelSerializer):
    class Meta:
        model = Exam
        fields = ['id', 'course', 'title', 'total_marks']

class CertificateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Certificate
        fields = ['id', 'user', 'course', 'date_issued', 'certificate_file']

class CourseBasicSerializer(serializers.ModelSerializer):
    class Meta:
        model = Course  # Assuming this is your course model
        fields = [
            'id', 'title', 'description', 'course_image', 'created_at',
            'category', 'lessons', 'instructor', 'enrollments'
        ]

class EnrollmentSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)  # Nested UserSerializer
    course = CourseBasicSerializer(read_only=True)  # Use CourseSerializer to get full course details

    class Meta:
        model = Enrollment
        fields = ['id', 'user', 'course', 'date_enrolled']  # Include user, course, and date_enrolled

    def create(self, validated_data):
        """
        Create a new enrollment while handling errors appropriately.
        """
        try:
            enrollment = Enrollment.objects.create(**validated_data)
        except Exception as e:
            raise serializers.ValidationError(f"Error creating enrollment: {str(e)}")
        return enrollment
   
class CourseSerializer(serializers.ModelSerializer):
    category = CategorySerializer()  # Nested Category
    lessons = LessonSerializer(many=True)  # Nested Lessons
    enrollments = serializers.SerializerMethodField()  # Use SerializerMethodField for enrollments
    instructor = InstructorSerializer()  # Nested Instructor

    class Meta:
        model = Course
        fields = [
            'id', 'title', 'description', 'course_image', 'created_at',
            'category', 'lessons', 'instructor', 'enrollments'
        ]

    def get_enrollments(self, obj):
        """
        Method to retrieve enrollments for the course.
        """
        enrollments = Enrollment.objects.filter(course=obj)
        return EnrollmentSerializer(enrollments, many=True).data

class ProgressSerializer(serializers.ModelSerializer):
    user_name = serializers.CharField(source='user.get_full_name', read_only=True)

    class Meta:
        model = Progress
        fields = ['id', 'user_name', 'course', 'completed_lessons', 'total_lessons']

class NotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notification
        fields = ['id', 'user', 'message', 'created_at', 'is_read']
