from rest_framework import status, permissions, serializers
from rest_framework.response import Response
from rest_framework.generics import GenericAPIView, ListAPIView, CreateAPIView, UpdateAPIView, DestroyAPIView
from rest_framework.mixins import CreateModelMixin
from django.contrib.auth import authenticate
from rest_framework.authtoken.models import Token
from rest_framework import generics
from django.contrib.auth import get_user_model
from .models import (HealthProviderUser, Course, Lesson, Quiz, Question, Answer, 
                     Exam, Certificate, Enrollment, Progress, Notification)

from .serializers import (AnswerSerializer, CourseProgressSerializer, EnrollmentSerializer, 
                          NotificationSerializer, QuizDetailSerializer, TakeQuizSerializer,  
                          UserSerializer, CourseSerializer, LessonSerializer,
                           QuizSerializer,QuestionSerializer)
from api.serializers import ChangePasswordSerializer, LoginSerializer

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

# Course Views
class CourseListView(ListAPIView):
    queryset = Course.objects.all()
    serializer_class = CourseSerializer

class CourseDetailView(GenericAPIView):
    # permission_classes = [permissions.IsAuthenticated]
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
    serializer_class = QuizDetailSerializer
    
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

        # Update progress for the specified user and course
        progress.update_progress(item_type, item_id)
        return Response({'message': f'{item_type.capitalize()} marked as completed!'}, status=status.HTTP_200_OK)


class TakeQuizAPIView(generics.CreateAPIView):
    serializer_class = TakeQuizSerializer

    def post(self, request, *args, **kwargs):
        quiz_id = self.kwargs.get('quiz_id')
        user_id = request.data.get('user_id')

        if not user_id:
            return Response({"error": "User ID not provided"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            return Response({"error": "User not found"}, status=status.HTTP_404_NOT_FOUND)

        try:
            quiz = Quiz.objects.get(id=quiz_id)
        except Quiz.DoesNotExist:
            return Response({"error": "Quiz not found"}, status=status.HTTP_404_NOT_FOUND)

        # Pass the user and quiz to the serializer
        serializer = self.get_serializer(data=request.data, context={'request': request, 'quiz': quiz, 'user': user})
        serializer.is_valid(raise_exception=True)
        result = serializer.save()

        return Response(result, status=status.HTTP_201_CREATED)
  
# Notification View
class NotificationView(GenericAPIView):
    # permission_classes = [permissions.IsAuthenticated]
    serializer_class = NotificationSerializer

    def get(self, request, *args, **kwargs):
        notifications = Notification.objects.filter(user=request.user).order_by('-created_at')
        serializer = NotificationSerializer(notifications, many=True)
        return Response(serializer.data)
