from django.utils import timezone
from django.shortcuts import get_object_or_404
from rest_framework import status, permissions, serializers
from rest_framework.response import Response
from rest_framework.exceptions import NotFound
from rest_framework.generics import (GenericAPIView, ListAPIView, CreateAPIView, 
                                     UpdateAPIView, DestroyAPIView,RetrieveAPIView,RetrieveAPIView)
from rest_framework.mixins import CreateModelMixin
from django.contrib.auth import authenticate, get_user_model
from rest_framework.authtoken.models import Token
from rest_framework import generics
from rest_framework.views import APIView
from .utils import send_otp_to_email
from .models import (Category, ExamUserAnswer, Grade, HealthProviderUser, Course, Lesson, Like, Quiz, Question, Answer, 
                     Exam, Certificate, Enrollment, Progress, Notification, QuizUserAnswer, Skill, Update, Comment)
from .serializers import (AnswerSerializer, CategorySerializer, CertificateSerializer, CommentSerializer, CourseProgressSerializer,
                           EnrollmentSerializer, ExamSerializer, ExamUserAnswerSerializer, GradeRequestSerializer, GradeSerializer, 
                          NotificationSerializer, SkillSerializer, TakeExamSerializer, TakeQuizSerializer, UpdateSerializer,  
                          UserSerializer, CourseSerializer, LessonSerializer,
                           QuizSerializer,QuestionSerializer,VerifyPasswordResetOtpSerializer, SetNewPasswordSerializer,ChangePasswordSerializer, LoginSerializer)
User = get_user_model()
# Admin-only view for creating new users
class AdminUserCreateView(GenericAPIView, CreateModelMixin):
    serializer_class = UserSerializer
    # permission_classes = [permissions.IsAdminUser]
    def post(self, request, *args, **kwargs):
        return self.create(request, *args, **kwargs)
# Custom login using registration number and password
class RegistrationNumberAuthToken(GenericAPIView):
    serializer_class = LoginSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        registration_number = serializer.validated_data['registration_number']
        password = serializer.validated_data['password']

        try:
            user = User.objects.get(registration_number=registration_number)
        except User.DoesNotExist:
            return Response({
                'status': False,
                'message': 'Registration number does not exist. Please contact the admin to register.'
            }, status=status.HTTP_400_BAD_REQUEST)

        user = authenticate(username=registration_number, password=password)

        if user is not None:
            token, created = Token.objects.get_or_create(user=user)

            # Prepare the user details with registration number
            user_data = {
                'id': user.id,
                'registration_number': user.registration_number,  # Added registration number
                'full_name': f"{user.first_name} {user.last_name}",
                'email': user.email,
                'telephone': user.telephone,
                'role': user.get_role_display(),
            }

            # Prepare the tokens
            tokens = {
                'access_token': token.key,
                'refresh_token': token.key  # You can generate a refresh token if needed
            }

            # Check if it's the first login
            first_login = user.check_password(registration_number)

            response_data = {
                'status': True,
                'message': 'Login successfully.',
                'data': {
                    'user': user_data,
                    'tokens': tokens
                }
            }

            # Indicate first login in the response if necessary
            if first_login:
                response_data['first_login'] = True

            return Response(response_data)

        return Response({
            'status': False,
            'message': 'Invalid credentials'
        }, status=status.HTTP_400_BAD_REQUEST)

class ChangePasswordView(GenericAPIView):
    # permission_classes = [permissions.IsAuthenticated]
    serializer_class = ChangePasswordSerializer

    def post(self, request, *args, **kwargs):
        # Extract user_id from request data
        user_id = request.data.get('user_id')

        if not user_id:
            return Response({
                'status': False,
                'message': 'User ID is required.',
            }, status=status.HTTP_400_BAD_REQUEST)

        try:
            user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            return Response({
                'status': False,
                'message': 'User not found.',
            }, status=status.HTTP_404_NOT_FOUND)

        serializer = self.get_serializer(data=request.data)

        if serializer.is_valid():
            new_password = serializer.validated_data.get('new_password')
            user.set_password(new_password)
            user.save()

            # Prepare the user details for the response
            user_data = {
                'id': user.id,
                'full_name': f"{user.first_name} {user.last_name}",
                'email': user.email,
                'telephone': user.telephone,
                'role': user.get_role_display(),
                'registration_number': user.registration_number
            }

            response_data = {
                'status': True,
                'message': 'Password changed successfully.',
                'data': {
                    'user': user_data,
                }
            }

            return Response(response_data)

        return Response({
            'status': False,
            'message': 'Invalid data provided.',
            'errors': serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)

class UserProfileView(generics.RetrieveUpdateAPIView):
    queryset = HealthProviderUser.objects.all()
    serializer_class = UserSerializer

    def get_object(self):
        # Retrieve user ID from the URL
        user_id = self.kwargs.get("user_id")
        
        # Check if user_id is None or the user doesn't exist
        if user_id is None:
            raise NotFound("User ID is required in the request data.")
        
        try:
            # Attempt to fetch the user by ID
            return HealthProviderUser.objects.get(id=user_id)
        except HealthProviderUser.DoesNotExist:
            raise NotFound("User not found.")
# Course Views
class CourseListView(ListAPIView):
    queryset = Course.objects.all()
    serializer_class = CourseSerializer

class CourseDetailView(GenericAPIView):
    # permission_classes = [permissions.IsAuthenticated]
    queryset = Course.objects.all()  # Define the queryset
    serializer_class = CourseSerializer

    def get(self, request, pk, *args, **kwargs):
        try:
            course = Course.objects.get(pk=pk)
        except Course.DoesNotExist:
            return Response({'error': 'Course not found'}, status=status.HTTP_404_NOT_FOUND)
        serializer = CourseSerializer(course)
        return Response(serializer.data)

# View for creating a new course
class CourseCreateView(CreateAPIView):
    queryset = Course.objects.all()
    serializer_class = CourseSerializer
# View for updating a course
class CourseUpdateView(UpdateAPIView):
    queryset = Course.objects.all()
    serializer_class = CourseSerializer
# View for deleting a course
class CourseDeleteView(DestroyAPIView):
    queryset = Course.objects.all()
    serializer_class = CourseSerializer

class CourseSearchView(ListAPIView):
    serializer_class = CourseSerializer
    
    def get_queryset(self):
        # Get the search term from the query parameters
        search_term = self.request.query_params.get('q', None)
        queryset = Course.objects.all()

        if search_term:
            # Filter courses based on the search term
            queryset = queryset.filter(title__icontains=search_term)
        
        return queryset

# Lesson Views
class LessonListView(GenericAPIView):
    # permission_classes = [permissions.IsAuthenticated]
    serializer_class = LessonSerializer

    def get(self, request, course_id, *args, **kwargs):
        lessons = Lesson.objects.filter(course_id=course_id)
        serializer = LessonSerializer(lessons, many=True)
        return Response(serializer.data)
    def get_queryset(self):
        # Get the course_id from the URL
        course_id = self.kwargs.get('course_id')
        # Return only the lessons for the given course
        return Lesson.objects.filter(course_id=course_id)

class LessonCreateView(CreateAPIView):
    queryset = Lesson.objects.all()
    serializer_class = LessonSerializer

class LessonUpdateView(UpdateAPIView):
    queryset = Lesson.objects.all()
    serializer_class = LessonSerializer

class LessonDeleteView(DestroyAPIView):
    queryset = Lesson.objects.all()
    serializer_class = LessonSerializer

class LessonDetailView(RetrieveAPIView):
    queryset = Lesson.objects.all()
    serializer_class = LessonSerializer
    lookup_field = 'id'

# Quiz Views
class QuizListView(GenericAPIView):
    # permission_classes = [permissions.IsAuthenticated]
    serializer_class = QuizSerializer
    
    def get_queryset(self):
        # You can customize this method to apply filtering or other logic.
        return Quiz.objects.all()  # Example: return all quizzes

    def get(self, request, *args, **kwargs):
        quizzes = Quiz.objects.all()
        serializer = QuizSerializer(quizzes, many=True)
        return Response(serializer.data)
    
    
class QuizDetailView(generics.RetrieveAPIView):
    queryset = Quiz.objects.all()
    serializer_class = QuizSerializer
    
class QuizCreateView(CreateAPIView):
    queryset = Quiz.objects.all()
    serializer_class = QuizSerializer
    

class QuizUpdateView(UpdateAPIView):
    queryset = Quiz.objects.all()
    serializer_class = QuizSerializer

class QuizDeleteView(DestroyAPIView):
    queryset = Quiz.objects.all()
    serializer_class = QuizSerializer

# Question Views
class QuestionListView(GenericAPIView):
    # permission_classes = [permissions.IsAuthenticated]
    serializer_class = QuestionSerializer

    def get(self, request, quiz_id, *args, **kwargs):
        questions = Question.objects.filter(quiz_id=quiz_id)
        serializer = QuestionSerializer(questions, many=True)
        return Response(serializer.data)

class QuestionCreateView(CreateAPIView):
    queryset = Question.objects.all()
    serializer_class = QuestionSerializer

class QuestionUpdateView(UpdateAPIView):
    queryset = Question.objects.all()
    serializer_class = QuestionSerializer

class QuestionDeleteView(DestroyAPIView):
    queryset = Question.objects.all()
    serializer_class = QuestionSerializer

# Answer Views
class AnswerListView(GenericAPIView):
    # permission_classes = [permissions.IsAuthenticated]
    serializer_class = AnswerSerializer

    def get(self, request, question_id, *args, **kwargs):
        answers = Answer.objects.filter(question_id=question_id)
        serializer = AnswerSerializer(answers, many=True)
        return Response(serializer.data)

class AnswerCreateView(CreateAPIView):
    queryset = Answer.objects.all()
    serializer_class = AnswerSerializer

class AnswerUpdateView(UpdateAPIView):
    queryset = Answer.objects.all()
    serializer_class = AnswerSerializer

class AnswerDeleteView(DestroyAPIView):
    queryset = Answer.objects.all()
    serializer_class = AnswerSerializer
User = get_user_model()

class CourseEnrollAPIView(generics.CreateAPIView):
    queryset = Enrollment.objects.all()
    serializer_class = EnrollmentSerializer

    def create(self, request, *args, **kwargs):
        course_id = self.kwargs.get('course_id')  # Extract course_id from URL
        user_id = request.data.get('user_id')     # Extract user_id from request data

        if not user_id:
            return Response({"error": "User ID not provided"}, status=status.HTTP_400_BAD_REQUEST)

        # Check if the user exists
        try:
            user = HealthProviderUser.objects.get(id=user_id)
        except HealthProviderUser.DoesNotExist:
            return Response({"error": "User not found"}, status=status.HTTP_404_NOT_FOUND)

        # Check if the course exists
        try:
            course = Course.objects.get(id=course_id)
        except Course.DoesNotExist:
            return Response({"error": "Course not found"}, status=status.HTTP_404_NOT_FOUND)

        # Check if the user is already enrolled in the course
        if Enrollment.objects.filter(user=user, course=course).exists():
            return Response({"error": "User is already enrolled in this course"}, status=status.HTTP_400_BAD_REQUEST)

        # Create the new enrollment
        enrollment = Enrollment.objects.create(user=user, course=course)

        # Serialize and return the created enrollment
        serializer = self.get_serializer(enrollment)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
# Enrollment View
class UserEnrolledCoursesAPIView(generics.ListAPIView):
    serializer_class = EnrollmentSerializer

    def get_queryset(self):
        user_id = self.kwargs.get('user_id')  # Get user_id from URL
        return Enrollment.objects.filter(user_id=user_id).select_related('course', 'user')  # Optimize query

    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)
    
# Progress View
class CompleteLessonAPIView(generics.UpdateAPIView):
    def post(self, request, course_id, lesson_id):
        user = request.user  # Assuming the user is authenticated
        try:
            progress = Progress.objects.get(user=user, course_id=course_id)
            lesson = Lesson.objects.get(id=lesson_id)

            if lesson.course.id != course_id:
                return Response({'error': 'Lesson does not belong to the specified course'}, status=status.HTTP_400_BAD_REQUEST)

            # Increment completed lessons
            progress.update_progress()

            return Response({
                'message': 'Lesson completed successfully',
                'completed_lessons': progress.completed_lessons,
                'total_lessons': progress.total_lessons
            }, status=status.HTTP_200_OK)
        except Progress.DoesNotExist:
            return Response({'error': 'Progress record not found'}, status=status.HTTP_404_NOT_FOUND)
        except Lesson.DoesNotExist:
            return Response({'error': 'Lesson not found'}, status=status.HTTP_404_NOT_FOUND)


class CourseProgressView(generics.UpdateAPIView):
    serializer_class = CourseProgressSerializer

    def update(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user_id = serializer.validated_data['user_id']
        course_id = kwargs['course_id']

        # Check if the user has progress for the course
        progress, created = Progress.objects.get_or_create(
            user_id=user_id,
            course_id=course_id,
            defaults={'total_lessons': Lesson.objects.filter(course_id=course_id).count()}
        )

        item_type = serializer.validated_data['type']
        item_id = serializer.validated_data['item_id']

        # Check item existence based on type
        if item_type == 'lesson':
            lesson = get_object_or_404(Lesson, id=item_id, course_id=course_id)

            # Check if the lesson is already marked as completed
            if progress.completed_lessons.filter(id=lesson.id).exists():
                return Response({'message': 'You have already completed this lesson!'}, status=status.HTTP_400_BAD_REQUEST)

            # Mark lesson as completed in progress
            progress.completed_lessons.add(lesson)

        elif item_type == 'quiz':
            quiz = get_object_or_404(Quiz, id=item_id, course_id=course_id)

            # Check if the quiz is already marked as completed
            if progress.completed_quizzes.filter(id=quiz.id).exists():
                return Response({'message': 'You have already completed this quiz!'}, status=status.HTTP_400_BAD_REQUEST)

            # Mark quiz as completed in progress
            progress.completed_quizzes.add(quiz)

        else:
            return Response({'error': 'Invalid item type'}, status=status.HTTP_400_BAD_REQUEST)

        return Response({'message': f'{item_type.capitalize()} marked as completed!'}, status=status.HTTP_200_OK)

class TakeQuizAPIView(generics.CreateAPIView):
    serializer_class = TakeQuizSerializer

    def post(self, request, *args, **kwargs):
        quiz_id = self.kwargs.get('quiz_id')
        user_id = request.data.get('user_id')
        retake = request.path.endswith('retake/')  # Check if the endpoint is for retaking

        if not user_id:
            return Response({"error": "User ID not provided"}, status=status.HTTP_400_BAD_REQUEST)

        user = get_object_or_404(User, id=user_id)
        quiz = get_object_or_404(Quiz, id=quiz_id)

        # Check if the user has already taken the quiz
        existing_answers = QuizUserAnswer.objects.filter(user=user, quiz=quiz)
        if existing_answers.exists():
            if not retake:
                return Response(
                    {"message": "Quiz already taken. Use retake option to attempt again."},
                    status=status.HTTP_409_CONFLICT
                )
            else:
                # If retake is true, delete previous answers
                existing_answers.delete()

                # Also delete the previous grade
                Grade.objects.filter(user=user, quiz=quiz).delete()

        # Proceed with creating new answers
        serializer = self.get_serializer(data=request.data, context={'request': request, 'quiz': quiz, 'user': user})
        serializer.is_valid(raise_exception=True)

        # Save the user's answers
        result = serializer.save()

        # Calculate the score and save or update the user's grade
        score = self.calculate_score(user, quiz)  # Function to calculate score based on saved answers
        total_marks = quiz.total_marks

        # Create or update the grade
        Grade.objects.update_or_create(
            user=user,
            course=quiz.course,
            quiz=quiz,
            defaults={'score': score, 'total_score': total_marks}
        )

        return Response(result, status=status.HTTP_201_CREATED)

    def calculate_score(self, user, quiz):
        # Calculate the score based on the user's answers
        correct_answers = QuizUserAnswer.objects.filter(user=user, quiz=quiz, is_correct=True).count()
        return correct_answers  # Adjust based on your grading scheme

class UserGradeListView(APIView):
    queryset = Grade.objects.all()  # Define the queryset for grades

    def post(self, request, *args, **kwargs):
        serializer = GradeRequestSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        user_id = serializer.validated_data['user_id']
        course_id = serializer.validated_data['course_id']

        try:
            user = User.objects.get(pk=user_id)
            course = Course.objects.get(pk=course_id)

            # Fetch quiz and exam grades for the specific course
            grades = self.queryset.filter(user=user, course=course)

            if not grades.exists():
                return Response(
                    {
                        "message": "No grades found for this course.",
                        "user_id": user_id,
                        "course_id": course_id
                    },
                    status=status.HTTP_404_NOT_FOUND
                )

            grade_serializer = GradeSerializer(grades, many=True)
            return Response(grade_serializer.data, status=status.HTTP_200_OK)

        except User.DoesNotExist:
            return Response({"error": "User not found"}, status=status.HTTP_404_NOT_FOUND)

        except Course.DoesNotExist:
            return Response({"error": "Course not found"}, status=status.HTTP_404_NOT_FOUND)

        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class NotificationView(GenericAPIView):
    # permission_classes = [permissions.IsAuthenticated]
    serializer_class = NotificationSerializer

    def get(self, request, *args, **kwargs):
        notifications = Notification.objects.filter(user=request.user).order_by('-created_at')
        serializer = NotificationSerializer(notifications, many=True)
        return Response(serializer.data)

class UpdateListView(generics.ListCreateAPIView):
    queryset = Update.objects.all()
    serializer_class = UpdateSerializer

class UpdateDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Update.objects.all()
    serializer_class = UpdateSerializer


# ListCreateAPIView for listing all categories or creating a new one
class CategoryListCreateView(generics.ListCreateAPIView):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer

# RetrieveUpdateDestroyAPIView for retrieving, updating, or deleting a specific category
class CategoryDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer

# CRUD for Comments
class CommentListCreateView(generics.ListCreateAPIView):
    serializer_class = CommentSerializer

    def get_queryset(self):
        update_id = self.kwargs['update_id']
        return Comment.objects.filter(update_id=update_id)

    def perform_create(self, serializer):
        update_id = self.kwargs['update_id']
        update = get_object_or_404(Update, id=update_id)

        # Get user_id from request data
        user_id = self.request.data.get('user_id')
        user = get_object_or_404(HealthProviderUser, id=user_id)  # Fetch user by user_id

        serializer.save(author=user, update=update)

class CommentRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = CommentSerializer

    def get_queryset(self):
        update_id = self.kwargs['update_id']
        return Comment.objects.filter(update_id=update_id)

class LikeUpdateView(APIView):

    def post(self, request, update_id):
        update = get_object_or_404(Update, id=update_id)
        user_id = request.data.get('user_id')  # Get user_id from request data
        user = get_object_or_404(HealthProviderUser, id=user_id)  # Fetch user by user_id

        # Check if the user has already liked this update
        like, created = Like.objects.get_or_create(update=update, user=user)

        if not created:
            # If the like already exists, remove it (unlike)
            like.delete()
            return Response({'message': 'Like removed'}, status=status.HTTP_200_OK)

        return Response({'message': 'Update liked'}, status=status.HTTP_201_CREATED)
    
class SkillListCreateView(generics.ListCreateAPIView):
    queryset = Skill.objects.all()
    serializer_class = SkillSerializer

class SkillRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Skill.objects.all()
    serializer_class = SkillSerializer

class ExamListCreateView(generics.ListCreateAPIView):
    queryset = Exam.objects.all()
    serializer_class = ExamSerializer

# View to retrieve, update, or delete a single exam
class ExamRetrieveUpdateDeleteView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Exam.objects.all()
    serializer_class = ExamSerializer

class TakeExamAPIView(generics.CreateAPIView):
    serializer_class = TakeExamSerializer

    def post(self, request, *args, **kwargs):
        exam_id = self.kwargs.get('exam_id')
        user_id = request.data.get('user_id')
        retake = request.path.endswith('retake/')  # Check if the endpoint is for retaking

        if not user_id:
            return Response({"error": "User ID not provided"}, status=status.HTTP_400_BAD_REQUEST)

        user = get_object_or_404(User, id=user_id)
        exam = get_object_or_404(Exam, id=exam_id)

        # Check if the user has already taken the exam
        existing_answers = ExamUserAnswer.objects.filter(user=user, exam=exam)
        if existing_answers.exists():
            if not retake:
                return Response(
                    {"message": "Exam already taken. Use retake option to attempt again."},
                    status=status.HTTP_409_CONFLICT
                )
            else:
                # If retake is true, delete previous answers and grades
                existing_answers.delete()
                Grade.objects.filter(user=user, exam=exam).delete()

        # Proceed with creating new answers
        serializer = self.get_serializer(data=request.data, context={'request': request, 'exam': exam, 'user': user})
        serializer.is_valid(raise_exception=True)

        # Save the user's answers and calculate marks
        result = serializer.save()

        return Response(result, status=status.HTTP_201_CREATED)
from rest_framework.decorators import api_view

@api_view(['GET'])
def get_quiz_by_course(request, course_id):
    try:
        quizzes = Quiz.objects.filter(course_id=course_id)
        if not quizzes.exists():
            return Response({"detail": "No quizzes found for this course."}, status=404)
        
        serializer = QuizSerializer(quizzes, many=True)
        return Response(serializer.data, status=200)
    except Quiz.DoesNotExist:
        return Response({"error": "Course not found."}, status=404)
    
@api_view(['GET'])
def get_exam_by_course(request, course_id):
    exams = Exam.objects.filter(course_id=course_id)
    if not exams.exists():
        return Response({"detail": "No Exams found for this course."}, status=404)
    
    serializer = ExamSerializer(exams, many=True)
    return Response(serializer.data, status=200)



class SendOtpForPasswordResetView(APIView):
    """
    Sends an OTP to the user's email and phone for password reset.
    """
    def post(self, request):
        registration_number = request.data.get("registration_number")
        if not registration_number:
            return Response({"error": "Registration number is required."}, status=status.HTTP_400_BAD_REQUEST)

        response_message = send_otp_to_email(registration_number, request)
        return Response({"message": response_message}, status=status.HTTP_200_OK)

class VerifyOtpView(APIView):
    """
    Verifies if the OTP entered by the user is valid.
    """
    def post(self, request):
        serializer = VerifyPasswordResetOtpSerializer(data=request.data)
        if serializer.is_valid():
            return Response({"message": "OTP is valid. Proceed to set a new password."}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class PasswordResetConfirmView(APIView):
    """
    Handles confirmation of OTP and password reset.
    """
    def post(self, request):
        serializer = SetNewPasswordSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()  # This will reset the user's password
            return Response({"message": "Password reset successfully."}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.utils import timezone
from .models import Grade, Certificate, HealthProviderUser  # Import your user model
from .serializers import CertificateSerializer

class CertificateListView(APIView):
    def post(self, request, *args, **kwargs):
        user_id = request.data.get('user_id')
        course_id = request.data.get('course_id')

        if not user_id or not course_id:
            return Response({"error": "user_id and course_id are required."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            # Fetch grades for the user and course, filtering only exams
            grades = Grade.objects.filter(user_id=user_id, course_id=course_id, exam__isnull=False)

            if not grades.exists():
                return Response({"error": "No grades found for this user and course."}, status=status.HTTP_404_NOT_FOUND)

            # Filter grades to find passing results
            passing_grades = grades.filter(score__gte=80)

            if not passing_grades.exists():
                return Response({"message": "User has not passed any exams for this course."}, status=status.HTTP_403_FORBIDDEN)

            certificates_data = []

            for grade in passing_grades:
                # Avoid creating duplicates
                existing_certificates = Certificate.objects.filter(
                    user_id=user_id,
                    course=grade.course,
                    exam=grade.exam
                )

                if existing_certificates.exists():
                    continue

                # Create the certificate data
                certificate_data = {
                    "user": grade.user.id,
                    "course": grade.course.id,
                    "exam": grade.exam.id,
                    "issued_date": timezone.now().date()
                }

                # Create the Certificate and assign the related objects
                serializer = CertificateSerializer(data=certificate_data)
                serializer.is_valid(raise_exception=True)
                certificate_instance = serializer.save(user=HealthProviderUser.objects.get(id=user_id))
                certificates_data.append(serializer.data)

            return Response({"certificates": certificates_data}, status=status.HTTP_201_CREATED)

        except HealthProviderUser.DoesNotExist:
            return Response({"error": "Invalid user ID."}, status=status.HTTP_404_NOT_FOUND)

