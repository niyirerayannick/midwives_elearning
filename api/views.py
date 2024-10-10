from rest_framework import status, permissions, serializers
from rest_framework.response import Response
from rest_framework.generics import GenericAPIView, ListAPIView, CreateAPIView, UpdateAPIView, DestroyAPIView
from rest_framework.mixins import CreateModelMixin
from django.contrib.auth import authenticate
from rest_framework.authtoken.models import Token
from django.contrib.auth import get_user_model
from .models import HealthProviderUser, Course, Lesson, Quiz, Question, Answer, Exam, Certificate, Enrollment, Progress, Notification
from .serializers import UserSerializer, CourseSerializer, LessonSerializer, QuizSerializer, QuestionSerializer, AnswerSerializer, ExamSerializer, CertificateSerializer, EnrollmentSerializer, ProgressSerializer, NotificationSerializer
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
                'error': 'Registration number does not exist. Please contact the admin to register.'
            }, status=status.HTTP_400_BAD_REQUEST)

        user = authenticate(username=registration_number, password=password)

        if user is not None:
            token, created = Token.objects.get_or_create(user=user)

            # If it's the first login (password is still the registration number)
            if user.check_password(registration_number):
                return Response({
                    'token': token.key,
                    'first_login': True,  # Indicate first-time login
                })

            return Response({
                'token': token.key,
                'first_login': False,
            })

        return Response({'error': 'Invalid credentials'}, status=status.HTTP_400_BAD_REQUEST)

# Change password after first login
class ChangePasswordView(GenericAPIView):
    # permission_classes = [permissions.IsAuthenticated]
    serializer_class = ChangePasswordSerializer

    def post(self, request, *args, **kwargs):
        user = request.user
        serializer = self.get_serializer(data=request.data)

        if serializer.is_valid():
            new_password = serializer.validated_data.get('new_password')
            user.set_password(new_password)
            user.save()
            return Response({'message': 'Password changed successfully'})

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

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

# Enrollment View
class EnrollmentView(GenericAPIView):
    # permission_classes = [permissions.IsAuthenticated]
    serializer_class = EnrollmentSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# Progress View
class ProgressView(GenericAPIView):
    # permission_classes = [permissions.IsAuthenticated]  # Ensure only authenticated users can access this view
    serializer_class = ProgressSerializer

    def get(self, request, course_id, *args, **kwargs):
        # Check if the user is authenticated
        if request.user.is_authenticated:
            # Fetch the progress for the authenticated user and course_id
            progress = Progress.objects.filter(user=request.user, course_id=course_id).first()

            if progress:
                serializer = ProgressSerializer(progress)
                return Response(serializer.data)
            return Response({'error': 'Progress not found'}, status=status.HTTP_404_NOT_FOUND)
        
        # If the user is not authenticated
        return Response({'error': 'Authentication required'}, status=status.HTTP_401_UNAUTHORIZED)

# Notification View
class NotificationView(GenericAPIView):
    # permission_classes = [permissions.IsAuthenticated]
    serializer_class = NotificationSerializer

    def get(self, request, *args, **kwargs):
        notifications = Notification.objects.filter(user=request.user).order_by('-created_at')
        serializer = NotificationSerializer(notifications, many=True)
        return Response(serializer.data)
