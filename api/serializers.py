from tokenize import Comment
from .models import Skill, Update, Comment, Like
from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.core.validators import RegexValidator
from .models import (Category, Grade, HealthProviderUser, Course, Lesson, Like, Quiz, Question,
                      Answer, Exam, Certificate, Enrollment, Progress, Notification, Update, UserAnswer)

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
        fields = ['registration_number', 'first_name', 'last_name', 'email', 'telephone', 'date_of_birth', 'role', 'profile_image']

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

class LessonSerializer(serializers.ModelSerializer):
    class Meta:
        model = Lesson
        fields = ['id', 'title', 'course', 'video_file', 'audio_file', 'readings', 'pdf_file', 'created_at']  # Updated field names

class CertificateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Certificate
        fields = ['id', 'user', 'course', 'date_issued', 'certificate_file']

class SkillSerializer(serializers.ModelSerializer):
    class Meta:
        model = Skill
        fields = ['id', 'name']
        
class CourseBasicSerializer(serializers.ModelSerializer):
    class Meta:
        model = Course  # Assuming this is your course model
        fields = [
            'id', 'title', 'description', 'course_image', 'created_at',
            'category', 'lessons', 'instructor', 'enrollments','skills'
        ]

class EnrollmentSerializer(serializers.ModelSerializer):
    # These will be used for both input (IDs) and output (nested data)
    user = UserSerializer(read_only=True)  # Use nested UserSerializer
    course = CourseBasicSerializer(read_only=True)  # Use nested CourseBasicSerializer

    class Meta:
        model = Enrollment
        fields = ['id', 'user', 'course', 'date_enrolled']

    def create(self, validated_data):
        """
        Create a new enrollment.
        """
        # Extract user and course from validated_data (they are passed as objects from PrimaryKeyRelatedField)
        user = validated_data.get('user')
        course = validated_data.get('course')

        # Create the enrollment object
        enrollment = Enrollment.objects.create(user=user, course=course)
        return enrollment
   


class CourseProgressSerializer(serializers.Serializer):
    user_id = serializers.IntegerField(required=True)  # User ID to mark progress
    type = serializers.ChoiceField(choices=['lesson', 'quiz'], required=True)  # Type of item
    item_id = serializers.IntegerField(required=True)  # ID of the lesson or quiz to mark as completed

    def validate(self, data):
        """
        Ensure that the lesson or quiz exists before marking it as completed.
        """
        item_type = data.get('type')
        item_id = data.get('item_id')

        if item_type == 'lesson':
            if not Lesson.objects.filter(id=item_id).exists():
                raise serializers.ValidationError("Lesson does not exist.")
        elif item_type == 'quiz':
            if not Quiz.objects.filter(id=item_id).exists():
                raise serializers.ValidationError("Quiz does not exist.")

        return data

    def create(self, validated_data):
        """
        This method is not used, but you can define it if needed for future enhancements.
        """
        pass  # If you need to implement any logic for creating progress, add it here.

    def update(self, instance, validated_data):
        """
        Update the progress for the user based on the item type and ID.
        """
        item_type = validated_data.get('type')
        item_id = validated_data.get('item_id')

        # Update progress for the specified user and course
        instance.update_progress(item_type, item_id)  # Call the update_progress method from the model
        return instance

class NotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notification
        fields = ['id', 'user', 'message', 'created_at', 'is_read']

class QuizSerializer(serializers.ModelSerializer):
    class Meta:
        model = Quiz
        fields = ['id', 'course', 'title', 'total_marks']
        
class AnswerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Answer
        fields = ['id', 'question', 'text', 'is_correct']

class QuestionSerializer(serializers.ModelSerializer):
    answers = AnswerSerializer(many=True, read_only=True)
    class Meta:
        model = Question
        fields = ['id', 'quiz', 'text','is_multiple_choice','answers']

class QuizDetailSerializer(serializers.ModelSerializer):
    # course = CourseSerializer(read_only=True)  # Nested CourseSerializer
    questions = QuestionSerializer(many=True, read_only=True)

    class Meta:
        model = Quiz
        fields = ['id', 'title', 'total_marks','questions']

class ExamSerializer(serializers.ModelSerializer):
    class Meta:
        model = Exam
        fields = ['id', 'course', 'title', 'total_marks']

class UserAnswerSerializer(serializers.Serializer):
    question = serializers.PrimaryKeyRelatedField(queryset=Question.objects.all())
    selected_choice = serializers.PrimaryKeyRelatedField(queryset=Answer.objects.all())

class TakeQuizSerializer(serializers.Serializer):
    answers = UserAnswerSerializer(many=True)

    def validate(self, data):
        answers = data['answers']
        quiz = self.context['quiz']

        question_ids = set(quiz.questions.values_list('id', flat=True))
        for answer in answers:
            question_id = answer['question'].id
            if question_id not in question_ids:
                raise serializers.ValidationError("Invalid question in answers.")

        return data

    def create(self, validated_data):
        quiz = self.context['quiz']
        user = self.context['user']
        answers = validated_data['answers']

        correct_count = 0
        total_questions = len(answers)

        for answer in answers:
            question = answer['question']
            selected_choice = answer['selected_choice']
            is_correct = selected_choice.is_correct

            user_answer, created = UserAnswer.objects.update_or_create(
                user=user,
                question=question,
                defaults={
                    'selected_choice': selected_choice,
                    'is_correct': is_correct
                }
            )

            if is_correct:
                correct_count += 1

        score = (correct_count / total_questions) * 100

        return {
            'quiz_id': quiz.id,
            'score': score,
            'total_questions': total_questions,
            'correct_answers': correct_count
        }

class GradeRequestSerializer(serializers.Serializer):
    user_id = serializers.IntegerField(required=True)
    course_id = serializers.IntegerField(required=True)

class GradeSerializer(serializers.ModelSerializer):
    # Nested serializers for quiz and exam
    quiz = QuizSerializer(read_only=True)
    exam = ExamSerializer(read_only=True)

    # Use PrimaryKeyRelatedField for user_id, as it's a foreign key
    user_id = serializers.PrimaryKeyRelatedField(queryset=User.objects.all())

    class Meta:
        model = Grade
        fields = ['id', 'user_id', 'quiz', 'exam', 'score', 'total_score']

    # If you need course_id, it should come through quiz or exam if related
    def to_representation(self, instance):
        representation = super().to_representation(instance)
        # Assuming course_id is related through quiz or exam
        if instance.quiz:
            representation['course_id'] = instance.quiz.course_id
        elif instance.exam:
            representation['course_id'] = instance.exam.course_id
        return representation

class UpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Update
        fields = ['id', 'title', 'content', 'author', 'cover_image', 'file', 'created_at', 'updated_at']


class CourseSerializer(serializers.ModelSerializer):
    category = serializers.PrimaryKeyRelatedField(queryset=Category.objects.all())  # Foreign Key to Category    lessons = LessonSerializer(many=True)  # Nested Lessons
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
    
class CategorySerializer(serializers.ModelSerializer):
    courses = CourseSerializer(many=True, read_only=True)

    class Meta:
        model = Category
        fields = ['id', 'name', 'description', 'courses']

class CommentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comment
        fields = ['id', 'update', 'author', 'content', 'created_at']
        read_only_fields = ['id', 'author', 'created_at', 'update']


class LikeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Like
        fields = ['id', 'update', 'user', 'created_at']
        read_only_fields = ['id', 'user', 'created_at', 'update']