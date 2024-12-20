from tokenize import Comment

from django.shortcuts import get_object_or_404
from .models import Emergency, EmergencyFile, ExamAnswer, ExamQuestion, ExamUserAnswer, Skill, Update, Comment, Like
from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.core.validators import RegexValidator
from .models import (Category, Grade, HealthProviderUser, Course, Lesson, Like, Quiz, Question,OneTimePassword,
                      Answer, Exam, Certificate, Enrollment, Progress, Notification, Update, QuizUserAnswer,ExamUserAnswer)

from rest_framework import serializers
from .models import ExamUserAnswer
User = get_user_model()
from django.contrib.auth.hashers import make_password

class UserSerializer(serializers.ModelSerializer):
    registration_number = serializers.CharField(
        required=True,
        validators=[RegexValidator(
            regex=r'^LIC\d{4}RW$', 
            message='Registration number must be in the format: LICXXXXRW (e.g., LIC1063RW)'
        )]
    )

    class Meta:
        model = HealthProviderUser
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
        fields = ['user', 'course', 'exam', 'issued_date']

class SkillSerializer(serializers.ModelSerializer):
    class Meta:
        model = Skill
        fields = ['id', 'name']
        
class CourseBasicSerializer(serializers.ModelSerializer):
    skills = SkillSerializer(many=True, read_only=True)
    instructor = InstructorSerializer()  
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
    type = serializers.ChoiceField(choices=['lesson', 'quiz', 'exam'], required=True)  # Type of item
    item_id = serializers.IntegerField(required=True)  # ID of the item (lesson, quiz, or exam)

    def validate(self, data):
        """
        Ensure that the lesson, quiz, or exam exists before marking it as completed.
        """
        item_type = data.get('type')
        item_id = data.get('item_id')

        if item_type == 'lesson':
            if not Lesson.objects.filter(id=item_id).exists():
                raise serializers.ValidationError("Lesson does not exist.")
        elif item_type == 'quiz':
            if not Quiz.objects.filter(id=item_id).exists():
                raise serializers.ValidationError("Quiz does not exist.")
        elif item_type == 'exam':
            if not Exam.objects.filter(id=item_id).exists():
                raise serializers.ValidationError("Exam does not exist.")
        
        return data

    def create(self, validated_data):
        """
        This method is not used, but you can define it if needed for future enhancements.
        """
        pass

    def update(self, instance, validated_data):
        """
        Update the progress for the user based on the item type and ID.
        """
        item_type = validated_data.get('type')
        item_id = validated_data.get('item_id')

        # Update progress for the specified user and course
        instance.update_progress(item_type, item_id)  # Ensure `update_progress` is implemented in the model
        return instance

    
class ProgressSerializer(serializers.ModelSerializer):
    # Nested serializers for related fields
    user = serializers.PrimaryKeyRelatedField(queryset=HealthProviderUser.objects.all())
    course = serializers.PrimaryKeyRelatedField(queryset=Course.objects.all())
    completed_lessons = serializers.PrimaryKeyRelatedField(queryset=Lesson.objects.all(), many=True)
    completed_quizzes = serializers.PrimaryKeyRelatedField(queryset=Quiz.objects.all(), many=True)
    
    total_lessons = serializers.IntegerField(read_only=True)
    total_quizzes = serializers.SerializerMethodField()
    
    # Calculate the total number of quizzes in a course
    def get_total_quizzes(self, obj):
        return Quiz.objects.filter(course=obj.course).count()
    
    # Check if the progress is complete (all lessons and quizzes completed)
    is_completed = serializers.SerializerMethodField()

    def get_is_completed(self, obj):
        total_lessons = obj.total_lessons
        completed_lessons_count = obj.completed_lessons.count()
        total_quizzes = self.get_total_quizzes(obj)
        completed_quizzes_count = obj.completed_quizzes.count()

        # Progress is complete when all lessons and quizzes are completed
        return completed_lessons_count == total_lessons and completed_quizzes_count == total_quizzes

    class Meta:
        model = Progress
        fields = ['id', 'user', 'course', 'completed_lessons', 'completed_quizzes', 'total_lessons', 'total_quizzes', 'is_completed']
class NotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notification
        fields = ['id', 'user', 'message', 'created_at', 'is_read']

class AnswerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Answer
        fields = ['id', 'question', 'text', 'is_correct']

class QuestionSerializer(serializers.ModelSerializer):
    answers = AnswerSerializer(many=True, read_only=True)
    class Meta:
        model = Question
        fields = ['id', 'quiz', 'text','is_multiple_choice','answers']

class QuizSerializer(serializers.ModelSerializer):
    questions = QuestionSerializer(many=True, read_only=True)  # Nested questions

    class Meta:
        model = Quiz
        fields = ['id', 'course', 'title', 'total_marks', 'questions']
class ExamAnswerSerializer(serializers.ModelSerializer):
    class Meta:
        model = ExamAnswer
        fields = ['id', 'question', 'text', 'is_correct']

class ExamQuestionSerializer(serializers.ModelSerializer):
    answers = ExamAnswerSerializer(many=True, read_only=True)  # Include answers
    class Meta:
        model = ExamQuestion
        fields = ['id', 'text', 'exam','answers']  # Include all relevant fields

class ExamSerializer(serializers.ModelSerializer):
    questions = ExamQuestionSerializer(many=True, read_only=True)  # Use the correct serializer

    class Meta:
        model = Exam
        fields = ['id', 'course', 'title', 'total_marks', 'questions']

class ExamUserAnswerSerializer(serializers.ModelSerializer):
    question = serializers.PrimaryKeyRelatedField(queryset=ExamQuestion.objects.all())

    class Meta:
        model = ExamUserAnswer
        fields = ['user', 'exam', 'question', 'selected_answer', 'is_correct']

class y_TakeExamSerializer(serializers.Serializer):
    answers = serializers.ListField(
        child=serializers.DictField()  # Each answer should be a dictionary with 'question' and 'selected_answer'
    )

    def validate(self, data):
        answers = data['answers']
        exam = self.context['exam']
        question_ids = set(exam.questions.values_list('id', flat=True))  # All valid question IDs from ExamQuestion

        for answer in answers:
            question_id = answer.get('question')
            selected_answer_id = answer.get('selected_answer')

            # Check if the provided question_id is valid
            if question_id not in question_ids:
                raise serializers.ValidationError(f"Invalid question ID: {question_id}.")
            
            if selected_answer_id is None:
                raise serializers.ValidationError("Each answer must include 'selected_answer'.")

        return data

    def create(self, validated_data):
        exam = self.context['exam']
        user = self.context['user']
        answers = validated_data['answers']

        correct_count = 0
        total_questions = len(answers)

        for answer in answers:
            question_id = answer.get('question')
            selected_answer_id = answer.get('selected_answer')

            # Ensure that each answer has valid question and selected_answer IDs
            question = get_object_or_404(ExamQuestion, id=question_id)
            selected_answer = get_object_or_404(ExamAnswer, id=selected_answer_id, question=question)

            if selected_answer.is_correct:
                correct_count += 1

            # Create or update the user's answer for this question
            ExamUserAnswer.objects.update_or_create(
                user=user,
                question=question,
                exam=exam,
                defaults={
                    'selected_answer': selected_answer,
                    'is_correct': selected_answer.is_correct
                }
            )

        score = (correct_count / total_questions) * 100

        Grade.objects.update_or_create(
            user=user,
            exam=exam,
            defaults={'score': score, 'total_score': exam.total_marks}
        )

        return {
            'exam_id': exam.id,
            'score': score,
            'total_questions': total_questions,
            'correct_answers': correct_count
        }

from rest_framework import serializers
from .models import ExamUserAnswer, Question, Answer, Exam

class TakeExamAnswerSerializer(serializers.Serializer):
    question_id = serializers.IntegerField()
    answer_id = serializers.IntegerField()

    def validate(self, data):
        # Validate that the question exists
        try:
            question = Question.objects.get(id=data['question_id'])
        except Question.DoesNotExist:
            raise serializers.ValidationError("Question not found.")
        
        # Validate that the answer exists
        try:
            answer = Answer.objects.get(id=data['answer_id'], question_id=data['question_id'])
        except Answer.DoesNotExist:
            raise serializers.ValidationError("Answer not found for the given question.")
        
        return data


class TakeExamSerializer(serializers.Serializer):
    user_id = serializers.IntegerField()
    answers = TakeExamAnswerSerializer(many=True)

    def validate_user(self, value):
        """Validate that the user exists."""
        try:
            user = User.objects.get(id=value)
        except User.DoesNotExist:
            raise serializers.ValidationError("User not found.")
        return value

    def validate(self, data):
        """Perform validation that the user has completed all lessons and quizzes."""
        user = User.objects.get(id=data['user_id'])
        answers = data.get('answers', [])

        # Check if user has completed all lessons and quizzes (add your logic here)
        # Check if the user has completed all lessons and quizzes
        course = Exam.objects.get(id=self.context['exam'].id).course  # Use the exam context to get the course
        completed_lessons = Progress.objects.filter(user=user, completed_lessons__in=course.lesson_set.all())
        completed_quizzes = Progress.objects.filter(user=user, completed_quizzes__in=course.quiz_set.all())

        if completed_lessons.count() != course.lesson_set.count():
            raise serializers.ValidationError("You must complete all lessons before taking the exam.")

        if completed_quizzes.count() != course.quiz_set.count():
            raise serializers.ValidationError("You must complete all quizzes before taking the exam.")

        return data

    def create(self, validated_data):
        """Create the ExamUserAnswer records."""
        user_id = validated_data['user_id']
        user = User.objects.get(id=user_id)
        exam = self.context['exam']
        answers_data = validated_data['answers']

        # Create ExamUserAnswer records for each question-answer pair
        answer_objects = []
        for answer_data in answers_data:
            question = Question.objects.get(id=answer_data['question_id'])
            selected_answer = Answer.objects.get(id=answer_data['answer_id'])
            answer_obj = ExamUserAnswer(
                user=user,
                exam=exam,
                question=question,
                selected_answer=selected_answer
            )
            answer_objects.append(answer_obj)

        # Bulk create all answers at once
        ExamUserAnswer.objects.bulk_create(answer_objects)
        return validated_data


class QuizUserAnswerSerializer(serializers.Serializer):
    question = serializers.PrimaryKeyRelatedField(queryset=Question.objects.all())
    selected_answer = serializers.PrimaryKeyRelatedField(queryset=Answer.objects.all())

class TakeQuizSerializer(serializers.Serializer):
    answers = serializers.JSONField()  # Assumes answers will be passed as JSON

    def validate(self, data):
        answers = data.get('answers')
        quiz = self.context['quiz']
        question_ids = set(quiz.questions.values_list('id', flat=True))

        if isinstance(answers, str):
            import json
            try:
                answers = json.loads(answers)
            except json.JSONDecodeError:
                raise serializers.ValidationError("Answers must be a valid JSON object.")

        if not isinstance(answers, list):
            raise serializers.ValidationError("Answers must be a list of dictionaries.")

        for answer in answers:
            if not isinstance(answer, dict) or 'question' not in answer or 'selected_answer' not in answer:
                raise serializers.ValidationError("Each answer must have 'question' and 'selected_answer' keys.")
            question = answer['question']
            if question not in question_ids:
                raise serializers.ValidationError(f"Invalid question ID: {question}")

        data['answers'] = answers
        return data

    def create(self, validated_data):
        quiz = self.context['quiz']
        user = self.context['user']
        answers = validated_data['answers']

        correct_count = 0
        total_questions = len(answers)

        for answer in answers:
            question_id = answer['question']
            selected_answer_id = answer['selected_answer']
            question = get_object_or_404(Question, id=question_id)
            selected_answer = get_object_or_404(Answer, id=selected_answer_id)

            # Save the user's answer
            QuizUserAnswer.objects.update_or_create(
                user=user,
                quiz=quiz,
                question=question,
                defaults={'selected_answer': selected_answer, 'is_correct': selected_answer.is_correct}
            )

            # Check if the selected answer is correct
            if selected_answer.is_correct:
                correct_count += 1

        score = (correct_count / total_questions) * quiz.total_marks if total_questions > 0 else 0

        # Save the user's grade
        Grade.objects.create(user=user, course=quiz.course, quiz=quiz, score=score, total_score=quiz.total_marks)

        return {
            'quiz_id': quiz.id,
            'score': score,
            'total_questions': total_questions,
            'correct_answers': correct_count
        }

class GradeRequestSerializer(serializers.Serializer):
    user_id = serializers.IntegerField(required=True)
    course_id = serializers.IntegerField(required=True)

class QuizSerializer_Grade(serializers.ModelSerializer):
    class Meta:
        model = Quiz
        fields = ['id', 'course', 'title', 'total_marks', 'questions']

class ExamSerializer_Grade(serializers.ModelSerializer):
    class Meta:
        model = Exam
        fields = ['id', 'course', 'title', 'total_marks']

class GradeSerializer(serializers.ModelSerializer):
    quiz = QuizSerializer_Grade(read_only=True)
    exam = ExamSerializer_Grade(read_only=True)

    class Meta:
        model = Grade
        fields = ['id', 'user', 'quiz', 'exam', 'score', 'total_score']

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        # Assuming course_id can be fetched through quiz or exam
        if instance.quiz:
            representation['course_id'] = instance.quiz.course_id
        elif instance.exam:
            representation['course_id'] = instance.exam.course_id
        return representation


class UpdateSerializer(serializers.ModelSerializer):
    author = UserSerializer(read_only=True)
    class Meta:
        model = Update
        fields = ['id', 'title', 'content', 'author', 'cover_image', 'file', 'created_at', 'updated_at']

class CourseSerializer(serializers.ModelSerializer):
    category = serializers.PrimaryKeyRelatedField(queryset=Category.objects.all())  # Foreign Key to Category    lessons = LessonSerializer(many=True)  # Nested Lessons
    enrollments = serializers.SerializerMethodField()  # Use SerializerMethodField for enrollments
    instructor = InstructorSerializer()  # Nested Instructor
    lessons = LessonSerializer(many=True)  # Nested Lessons
    skills = SkillSerializer(many=True, read_only=True)

    class Meta:
        model = Course
        fields = [
            'id', 'title', 'description', 'course_image', 'created_at',
            'category', 'lessons', 'instructor', 'enrollments','skills'
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
    author = UserSerializer(read_only=True)
    class Meta:
        model = Comment
        fields = ['id', 'update', 'author', 'content', 'created_at']
        read_only_fields = ['id', 'author', 'created_at', 'update']

class LikeSerializer(serializers.ModelSerializer):
    author = UserSerializer(read_only=True)
    class Meta:
        model = Like
        fields = ['id', 'update', 'user', 'created_at']
        read_only_fields = ['id', 'user', 'created_at', 'update']

class VerifyPasswordResetOtpSerializer(serializers.Serializer):
    registration_number = serializers.CharField(max_length=50)
    otp = serializers.CharField(max_length=6)

    def validate(self, data):
        registration_number = data.get("registration_number")
        otp = data.get("otp")

        try:
            user = HealthProviderUser.objects.get(registration_number=registration_number)
            otp_obj = OneTimePassword.objects.filter(user=user, otp=otp).first()
            if not otp_obj:
                raise serializers.ValidationError("Invalid OTP.")
        except HealthProviderUser.DoesNotExist:
            raise serializers.ValidationError("User does not exist.")
        
        return data

class SetNewPasswordSerializer(serializers.Serializer):
    registration_number = serializers.CharField(max_length=50)
    otp = serializers.CharField(max_length=6)
    new_password = serializers.CharField(write_only=True)

    def validate(self, data):
        registration_number = data.get("registration_number")
        otp = data.get("otp")

        try:
            user = HealthProviderUser.objects.get(registration_number=registration_number)
            otp_obj = OneTimePassword.objects.filter(user=user, otp=otp).first()
            if not otp_obj:
                raise serializers.ValidationError("Invalid OTP.")
        except HealthProviderUser.DoesNotExist:
            raise serializers.ValidationError("User does not exist.")
        
        return data
    
    def save(self):
        registration_number = self.validated_data.get("registration_number")
        new_password = self.validated_data.get("new_password")
        
        user = HealthProviderUser.objects.get(registration_number=registration_number)
        user.password = make_password(new_password)
        user.save()

        # Optionally, delete OTP after successful password reset
        OneTimePassword.objects.filter(user=user).delete()

class ExamUserSerializer(serializers.ModelSerializer):

    class Meta:
        model = HealthProviderUser  # Ensure this points to your actual instructor model
        fields = ['id', 'full_name', 'registration_number', 'email', 'telephone']


class CertificateSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    course = CourseSerializer(read_only=True)
    exam = ExamSerializer(read_only=True, allow_null=True)  # Allow null for optional exams

    class Meta:
        model = Certificate
        fields = ['id', 'user', 'course', 'exam', 'issued_date']


class EmergencyFileSerializer(serializers.ModelSerializer):
    file_url = serializers.ReadOnlyField()  # This will use the 'file_url' property from the model

    class Meta:
        model = EmergencyFile
        fields = ['file_url', 'file_type', 'description']

class EmergencySerializer(serializers.ModelSerializer):
    files = EmergencyFileSerializer(many=True, read_only=True)  # Nest the files in the emergency response

    class Meta:
        model = Emergency
        fields = ['id', 'title', 'description', 'created_at', 'files']

class CompletedCourseSerializer(serializers.ModelSerializer):
    course_title = serializers.CharField(source='course.title')  # Get course title
    is_completed = serializers.SerializerMethodField()  # Determine completion status
    completion_message = serializers.SerializerMethodField()  # Generate a message

    class Meta:
        model = Progress
        fields = ['course_title', 'is_completed', 'completion_message']

    def get_is_completed(self, obj):
        # Check if the course is completed
        return (
            obj.completed_lessons.count() == obj.course.lesson_set.count()
            and obj.completed_quizzes.count() == obj.course.quiz_set.count()
        )

    def get_completion_message(self, obj):
        # Return a completion message based on the completion status
        if self.get_is_completed(obj):
            return f"Course '{obj.course.title}' is completed."
        return f"Course '{obj.course.title}' is not completed yet."
    
class CourseInProgressSerializer(serializers.ModelSerializer):
    course_title = serializers.CharField(source='course.title')

    class Meta:
        model = Progress
        fields = ['course_title']