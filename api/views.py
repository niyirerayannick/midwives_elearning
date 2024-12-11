from django.utils import timezone

from django.shortcuts import get_object_or_404
from django.http import JsonResponse
from .models import Grade
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
from .models import (Category, Emergency, ExamAnswer, ExamQuestion, ExamUserAnswer, Grade, HealthProviderUser, Course, Lesson, Like, Quiz, Question, Answer, 
                     Exam, Certificate, Enrollment, Progress, Notification, QuizUserAnswer, Skill, Update, Comment, UserExamProgress, UserLessonProgress, UserQuizProgress)
from .serializers import (AnswerSerializer, CategorySerializer, CertificateSerializer, CommentSerializer, CompletedCourseSerializer, CourseProgressSerializer, EmergencySerializer,
                           EnrollmentSerializer, ExamSerializer, ExamUserAnswerSerializer, GradeRequestSerializer, GradeSerializer, 
                          NotificationSerializer, SkillSerializer, TakeExamSerializer, TakeQuizSerializer, UpdateSerializer,  
                          UserSerializer, CourseSerializer, LessonSerializer,
                           QuizSerializer,QuestionSerializer,VerifyPasswordResetOtpSerializer, SetNewPasswordSerializer,ChangePasswordSerializer, LoginSerializer)
from django.db.models import F

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
        item_type = serializer.validated_data['type']
        item_id = serializer.validated_data['item_id']

        # Fetch or create progress for the user and course
        progress, _ = Progress.objects.get_or_create(
            user_id=user_id,
            course_id=course_id,
            defaults={'total_lessons': Lesson.objects.filter(course_id=course_id).count()}
        )

        # Handle item completion logic
        if item_type == 'lesson':
            response = self._mark_as_completed(progress, Lesson, item_id, course_id, 'completed_lessons')
        elif item_type == 'quiz':
            response = self._mark_as_completed(progress, Quiz, item_id, course_id, 'completed_quizzes')
        elif item_type == 'exam':
            response = self._mark_as_completed(progress, Exam, item_id, course_id, 'completed_exams')
        else:
            return Response({'error': 'Invalid item type'}, status=status.HTTP_400_BAD_REQUEST)

        return response

    def _mark_as_completed(self, progress, model, item_id, course_id, completed_field):
        """
        Mark the item (lesson, quiz, or exam) as completed for the user's progress.
        """
        item = get_object_or_404(model, id=item_id, course_id=course_id)

        # Check if the item is already marked as completed
        completed_items = getattr(progress, completed_field)
        if completed_items.filter(id=item.id).exists():
            return Response({'message': f'You have already completed this {model.__name__.lower()}!'}, status=status.HTTP_400_BAD_REQUEST)

        # Mark item as completed
        completed_items.add(item)
        return Response({'message': f'{model.__name__.capitalize()} marked as completed!'}, status=status.HTTP_200_OK)

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
                Grade.objects.filter(user=user, quiz=quiz).delete()

        serializer = self.get_serializer(data=request.data, context={'quiz': quiz, 'user': user})
        serializer.is_valid(raise_exception=True)
        result = serializer.save()

        return Response(result, status=status.HTTP_201_CREATED)

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

    # Short-circuit for schema generation
    
    def get_queryset(self):
        if getattr(self, 'swagger_fake_view', False):
           return Comment.objects.none()
        
         # Normal behavior
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
        retake = request.path.endswith('retake/')  # Check if the endpoint is for retaking the exam

        if not user_id:
            return Response({"error": "User ID not provided"}, status=status.HTTP_400_BAD_REQUEST)

        # Fetch the user and exam
        user = get_object_or_404(User, id=user_id)
        exam = get_object_or_404(Exam, id=exam_id)
        course = exam.course  # Get the associated course from the exam

        # Check if the user has completed all lessons
        completed_lessons = Lesson.objects.filter(course=course)
        user_completed_lessons = UserLessonProgress.objects.filter(user=user, lesson__in=completed_lessons, is_completed=True)
        
        if user_completed_lessons.count() != completed_lessons.count():
            return Response(
                {"error": "You must complete all lessons before taking the exam."},
                status=status.HTTP_403_FORBIDDEN
            )

        # Check if the user has completed all quizzes
        completed_quizzes = Quiz.objects.filter(course=course)
        user_completed_quizzes = UserQuizProgress.objects.filter(user=user, quiz__in=completed_quizzes, is_completed=True)

        if user_completed_quizzes.count() != completed_quizzes.count():
            return Response(
                {"error": "You must complete all quizzes before taking the exam."},
                status=status.HTTP_403_FORBIDDEN
            )

        # Check if the user has already taken the exam
        existing_answers = ExamUserAnswer.objects.filter(user=user, exam=exam)
        if existing_answers.exists():
            if not retake:
                return Response(
                    {"message": "Exam already taken. Use the retake option to attempt again."},
                    status=status.HTTP_409_CONFLICT
                )
            else:
                # If retake is true, delete previous answers and grades
                existing_answers.delete()
                Grade.objects.filter(user=user, exam=exam).delete()

        # Process the answers using the serializer
        serializer = self.get_serializer(data=request.data, context={'request': request, 'exam': exam, 'user': user})
        serializer.is_valid(raise_exception=True)

        # Save the user's answers and calculate the score
        serializer.save()

        score = self.calculate_score(user, exam)
        total_marks = exam.total_marks

        # Create or update the user's grade
        grade, created = Grade.objects.update_or_create(
            user=user,
            exam=exam,
            defaults={'score': score, 'total_score': total_marks, 'course': course}
        )

        return Response({"status": "success", "score": score, "total_score": total_marks}, status=status.HTTP_201_CREATED)
from rest_framework.decorators import api_view

class CoursesInProgressView(APIView):
    def get(self, request, user_id, *args, **kwargs):
        try:
            # Verify if the user exists
            if not HealthProviderUser.objects.filter(id=user_id).exists():
                return Response({"error": "User not found."}, status=status.HTTP_404_NOT_FOUND)

            # Fetch all progress records for the user
            progress_records = Progress.objects.filter(user_id=user_id)

            # Filter courses where not all lessons or quizzes are completed
            in_progress_courses = []
            for progress in progress_records:
                total_lessons = progress.course.lessons.count()
                total_quizzes = progress.course.quizzes.count()

                if (
                    progress.completed_lessons.count() < total_lessons or
                    progress.completed_quizzes.count() < total_quizzes
                ):
                    in_progress_courses.append({
                        "course_id": progress.course.id,
                        "course_title": progress.course.title
                    })

            # Check if there are any courses in progress
            if not in_progress_courses:
                return Response({"message": "No courses in progress."}, status=status.HTTP_404_NOT_FOUND)

            return Response({"in_progress_courses": in_progress_courses}, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class GetUserGrades(APIView):
    def get(self, request, user_id):
        grades = Grade.objects.filter(user_id=user_id)

        if not grades.exists():
            raise NotFound("No grades found for this user.")

        grades_data = [
            {
                "course": grade.course.title,
                "quiz": grade.quiz.title if grade.quiz else None,
                "exam": grade.exam.title if grade.exam else None,
                "score": float(grade.score),
                "total_score": grade.total_score,
                "percentage": grade.percentage
            }
            for grade in grades
        ]
        return Response({"grades": grades_data})
 
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
                    "user": user_id,  # We already have the user ID
                    "course": grade.course.id,
                    "exam": grade.exam.id,
                    "issued_date": timezone.now().date()
                }

                # Create the Certificate and assign the related objects
                serializer = CertificateSerializer(data=certificate_data)
                serializer.is_valid(raise_exception=True)
                serializer.save(user=HealthProviderUser.objects.get(id=user_id))  # Save with the related user
                certificates_data.append(serializer.data)

            return Response({"certificates": certificates_data}, status=status.HTTP_201_CREATED)

        except HealthProviderUser.DoesNotExist:
            return Response({"error": "Invalid user ID."}, status=status.HTTP_404_NOT_FOUND)

        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class UserCertificateListView(APIView):
    def get(self, request, user_id, *args, **kwargs):
        try:
            # Fetch certificates for the user
            certificates = Certificate.objects.filter(user_id=user_id)

            # Check if certificates exist for the user
            if not certificates.exists():
                return Response({"error": "No certificates found for this user."}, status=status.HTTP_404_NOT_FOUND)

            # Serialize the certificates
            serializer = CertificateSerializer(certificates, many=True)

            # Return the serialized data
            return Response({"certificates": serializer.data}, status=status.HTTP_200_OK)

        except Certificate.DoesNotExist:
            return Response({"error": "Certificates not found."}, status=status.HTTP_404_NOT_FOUND)

        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class CompletedCoursesView(APIView):
    def get(self, request, user_id, *args, **kwargs):
        try:
            # Verify if the user exists
            if not HealthProviderUser.objects.filter(id=user_id).exists():
                return Response({"error": "User not found."}, status=status.HTTP_404_NOT_FOUND)

            # Fetch grades where the score is >= 80 for completed courses
            
            completed_courses = Grade.objects.filter(
                user_id=user_id,
                score__gte=80
            ).values(
                'course__id',
                'course__title',
                'course__description',
                'course__course_image', 
                'course__category', 
                'course__instructor__id',        # Include instructor ID
                'course__instructor__first_name', # Include instructor first name
                'course__instructor__last_name'  # Make sure these fields exist in the related Course model
            )

            # Check if any courses are found
            if not completed_courses.exists():
                return Response({"message": "No completed courses found."}, status=status.HTTP_404_NOT_FOUND)

            # Convert the QuerySet to a list and return the response
            return Response({"completed_courses": list(completed_courses)}, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)




@api_view(['POST'])
def complete_lesson(request, lesson_id, user_id):
    try:
        # Fetch the lesson and user based on the provided IDs
        lesson = Lesson.objects.get(id=lesson_id)
        user = HealthProviderUser.objects.get(id=user_id)  # Changed to HealthProviderUser
        
        # Create or get the user's progress for this lesson
        progress, created = UserLessonProgress.objects.get_or_create(user=user, lesson=lesson)
        
        # Mark the lesson as completed
        progress.is_completed = True
        progress.save()

        # Respond with success
        return Response({'status': 'Lesson marked as complete'})
    
    except (Lesson.DoesNotExist, HealthProviderUser.DoesNotExist):  # Changed to HealthProviderUser
        return Response({'error': 'Lesson or User not found'}, status=404)

@api_view(['POST'])
def complete_quiz(request, quiz_id, user_id):
    try:
        quiz = Quiz.objects.get(id=quiz_id)
        user = HealthProviderUser.objects.get(id=user_id)  # Changed to HealthProviderUser
        progress, created = UserQuizProgress.objects.get_or_create(user=user, quiz=quiz)
        progress.is_completed = True
        progress.save()
        return Response({'status': 'success'})
    except (Quiz.DoesNotExist, HealthProviderUser.DoesNotExist):  # Changed to HealthProviderUser
        return Response({'error': 'Quiz or User not found'}, status=404)

@api_view(['POST'])
def complete_exam(request, exam_id, user_id):
    try:
        exam = Exam.objects.get(id=exam_id)
        user = HealthProviderUser.objects.get(id=user_id)  # Changed to HealthProviderUser
        progress, created = UserExamProgress.objects.get_or_create(user=user, exam=exam)
        progress.is_completed = True
        progress.save()
        return Response({'status': 'success'})
    except (Exam.DoesNotExist, HealthProviderUser.DoesNotExist):  # Changed to HealthProviderUser
        return Response({'error': 'Exam or User not found'}, status=404)

@api_view(['GET'])
def get_user_course_progress(request, course_id, user_id):
    try:
        course = Course.objects.get(id=course_id)
        user = HealthProviderUser.objects.get(id=user_id)  # Changed to HealthProviderUser

        # Calculate lesson progress
        total_lessons = course.lessons.count()
        completed_lessons = course.lessons.filter(userlessonprogress__user=user, userlessonprogress__is_completed=True).count()
        lesson_progress = (completed_lessons / total_lessons * 100) if total_lessons > 0 else 0

        # Calculate quiz progress
        total_quizzes = course.quizzes.count()
        completed_quizzes = course.quizzes.filter(userquizprogress__user=user, userquizprogress__is_completed=True).count()
        quiz_progress = (completed_quizzes / total_quizzes * 100) if total_quizzes > 0 else 0

        # Calculate exam progress
        total_exams = course.exams.count()
        completed_exams = course.exams.filter(userexamprogress__user=user, userexamprogress__is_completed=True).count()
        exam_progress = (completed_exams / total_exams * 100) if total_exams > 0 else 0

        # Calculate total progress (equal weightage to all components)
        total_progress = (lesson_progress + quiz_progress + exam_progress) / 3

        return Response({
            'lessonProgress': round(lesson_progress, 2),
            'quizProgress': round(quiz_progress, 2),
            'examProgress': round(exam_progress, 2),
            'totalProgress': round(total_progress, 2)
        })

    except Course.DoesNotExist:
        return Response({'error': 'Course not found'}, status=404)
    except HealthProviderUser.DoesNotExist:
        return Response({'error': 'User not found'}, status=404)

@api_view(['POST'])
def take_exam(request, exam_id, user_id):
    try:
        # Fetch the exam and user
        exam = Exam.objects.get(id=exam_id)
        user = HealthProviderUser.objects.get(id=user_id)

        # Create or get the user's exam progress entry
        progress, created = UserExamProgress.objects.get_or_create(user=user, exam=exam)

        # If the exam is already completed, return a message
        if progress.is_completed:
            return Response({'status': 'Exam already completed'}, status=status.HTTP_400_BAD_REQUEST)
        
        # Update progress to 'started' or 'in progress'
        progress.is_completed = False
        progress.save()

        # Fetch questions for the exam and their answers (choices)
        questions = exam.questions.all()  # Get all questions related to the exam
        question_data = []
        for question in questions:
            choices = question.answers.all()  # Get the choices related to this question
            question_data.append({
                'question_id': question.id,
                'question_text': question.text,
                'choices': [{'id': choice.id, 'text': choice.text} for choice in choices]
            })

        return Response({
            'status': 'Exam started successfully',
            'questions': question_data
        })

    except (Exam.DoesNotExist, HealthProviderUser.DoesNotExist):
        return Response({'error': 'Exam or User not found'}, status=status.HTTP_404_NOT_FOUND)

@api_view(['POST'])
def retake_exam(request, exam_id, user_id):
    try:
        # Fetch the exam and user
        exam = Exam.objects.get(id=exam_id)
        user = HealthProviderUser.objects.get(id=user_id)

        # Check user's exam progress
        try:
            progress = UserExamProgress.objects.get(user=user, exam=exam)
        except UserExamProgress.DoesNotExist:
            return Response({'error': 'Exam not taken yet, cannot retake.'}, status=status.HTTP_400_BAD_REQUEST)

        # Ensure the exam was completed
        if not progress.is_completed:
            return Response({'error': 'Exam not completed yet, cannot retake.'}, status=status.HTTP_400_BAD_REQUEST)

        # Check if the user scored less than 80%
        user_answers = ExamUserAnswer.objects.filter(user=user, exam=exam)
        total_questions = user_answers.count()
        correct_answers = user_answers.filter(is_correct=True).count()
        score = (correct_answers / total_questions * 100) if total_questions > 0 else 0

        if score >= 80:
            return Response({'status': 'You have already passed the exam and cannot retake it.'}, status=status.HTTP_400_BAD_REQUEST)

        # Reset exam progress for retake
        progress.is_completed = False
        progress.save()

        # Delete previous answers for this user and exam
        ExamUserAnswer.objects.filter(user=user, exam=exam).delete()

        return Response({'status': 'Exam reset successfully. You can now retake the exam.'}, status=status.HTTP_200_OK)

    except (Exam.DoesNotExist, HealthProviderUser.DoesNotExist):
        return Response({'error': 'Exam or User not found'}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response({'error': f'An unexpected error occurred: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['POST'])
def submit_exam(request, exam_id, user_id):
    try:
        # Check if the exam exists
        try:
            exam = Exam.objects.get(id=exam_id)
        except Exam.DoesNotExist:
            return Response({'error': 'Exam not found'}, status=status.HTTP_404_NOT_FOUND)

        # Check if the user exists
        try:
            user = HealthProviderUser.objects.get(id=user_id)
        except HealthProviderUser.DoesNotExist:
            return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)

        # Get or create the user's exam progress
        progress, created = UserExamProgress.objects.get_or_create(user=user, exam=exam)

        # If the exam is already completed for this user, return an appropriate message
        if not created and progress.is_completed:
            return Response({'status': 'Exam already completed'}, status=status.HTTP_400_BAD_REQUEST)

        # Get answers from the request data
        answers = request.data.get('answers', [])
        
        # Initialize score counters
        total_questions = 0
        correct_answers = 0
        
        # Loop through answers and save user's responses
        for answer in answers:
            question_id = answer.get('question_id')
            choice_id = answer.get('choice_id')

            # Check if the question exists
            try:
                question = ExamQuestion.objects.get(id=question_id)
            except ExamQuestion.DoesNotExist:
                return Response({'error': f'Question with ID {question_id} not found'}, status=status.HTTP_404_NOT_FOUND)

            # Check if the answer choice exists for the question
            try:
                selected_answer = ExamAnswer.objects.get(id=choice_id, question=question)
            except ExamAnswer.DoesNotExist:
                return Response({'error': f'Answer with ID {choice_id} for Question ID {question_id} not found'}, status=status.HTTP_404_NOT_FOUND)

            # Save or update the user's answer
            user_answer, _ = ExamUserAnswer.objects.update_or_create(
                user=user,
                exam=exam,
                question=question,
                defaults={
                    'selected_answer': selected_answer,
                    'is_correct': selected_answer.is_correct
                }
            )

            # Track score
            total_questions += 1
            if selected_answer.is_correct:
                correct_answers += 1

        # Calculate score as a percentage
        score = (correct_answers / total_questions * 100) if total_questions > 0 else 0

        # Mark the exam as completed only after all answers are saved
        progress.is_completed = True
        progress.save()

        return Response({
            'status': 'Exam submitted successfully',
            'score': round(score, 2),
            'total_questions': total_questions,
            'correct_answers': correct_answers
        })

    except Exception as e:
        # Catch unexpected errors and log for further debugging
        return Response({'error': f'An unexpected error occurred: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
def get_grades(request, user_id, course_id):
    """
    Retrieve grades for a specific user and course.
    """
    try:
        # Filter grades by user_id and course_id
        grades = Grade.objects.filter(user_id=user_id, course_id=course_id)

        # If no grades are found, return a 404 error
        if not grades.exists():
            return Response({'error': 'No grades found for the specified user and course'}, status=status.HTTP_404_NOT_FOUND)

        # Serialize the grades data using GradeSerializer
        serializer = GradeSerializer(grades, many=True)

        return Response({'grades': serializer.data}, status=status.HTTP_200_OK)

    except Exception as e:
        # Handle unexpected errors
        return Response({'error': f'An unexpected error occurred: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
def get_user_certificate(request, exam_id, user_id):
    try:
        # Fetch the exam and user
        exam = Exam.objects.get(id=exam_id)
        user = HealthProviderUser.objects.get(id=user_id)
        
        # Get the related course from the exam
        course = exam.course

        # Calculate the user's score for the exam
        total_questions = exam.questions.count()
        correct_answers = ExamUserAnswer.objects.filter(
            user=user, 
            exam=exam, 
            is_correct=True
        ).count()
        
        # Calculate the percentage score
        score_percentage = (correct_answers / total_questions * 100) if total_questions > 0 else 0
        
        # Check if the user qualifies for a certificate (80% or higher)
        if score_percentage >= 80:
            # Check if a certificate has already been issued
            certificate, created = Certificate.objects.get_or_create(
                user=user, 
                exam=exam, 
                defaults={'issued_date': timezone.now()}
            )
            
            if created:
                message = 'Certificate issued successfully.'
            else:
                message = 'Certificate already exists.'

            # Return detailed certificate information
            return Response({
                'status': message,
                'certificate': {
                    'user': {
                        'registration_number': user.registration_number,
                        'name': f"{user.first_name} {user.last_name}", 
                        'email': user.email,
                    },
                    'exam': exam.title,
                    'course': {
                        'title': course.title,
                        'description': course.description,
                        'cpd': course.cpd,
                    },
                    'issued_date': certificate.issued_date,
                    'score_percentage': round(score_percentage, 2)
                }
            })

        else:
            return Response({
                'status': 'Failed',
                'message': 'Score below 80%, certificate not issued.',
                'score_percentage': round(score_percentage, 2)
            }, status=400)

    except (Exam.DoesNotExist, HealthProviderUser.DoesNotExist):
        return Response({'error': 'Exam or User not found'}, status=404)
    except Course.DoesNotExist:
        return Response({'error': 'Course not found'}, status=404)


@api_view(['GET'])
def get_emergency_courses(request):
    """
    Get all emergency courses with associated files.
    """
    try:
        emergencies = Emergency.objects.all()
        serializer = EmergencySerializer(emergencies, many=True)  # Serialize the list of emergencies
        return Response({'emergencies': serializer.data}, status=status.HTTP_200_OK)

    except Exception as e:
        return Response({'error': f'An unexpected error occurred: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
@api_view(['GET'])
def get_single_emergency(request, emergency_id):
    """
    Get details of a single emergency course with associated files.
    """
    try:
        # Fetch the emergency course using the provided ID
        emergency = Emergency.objects.get(id=emergency_id)

        # Serialize the emergency data
        serializer = EmergencySerializer(emergency)

        # Return the serialized data wrapped in a Response object
        return Response(serializer.data, status=status.HTTP_200_OK)

    except Emergency.DoesNotExist:
        return Response({'error': 'Emergency course not found'}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response({'error': f'An unexpected error occurred: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
       
@api_view(['GET'])
def get_course_enrollments(request, course_id):
    try:
        # Fetch enrollments for the given course
        enrollments = Enrollment.objects.filter(course_id=course_id)
        if not enrollments.exists():
            return Response({'message': 'No enrollments found for this course.'}, status=404)
        
        serializer = EnrollmentSerializer(enrollments, many=True)
        return Response(serializer.data)
    except Exception as e:
        return Response({'error': str(e)}, status=500)
    
@api_view(['GET'])
def get_courses_in_progress(request, user_id):
    """
    Get all courses where the user is enrolled with status 'in_progress'.
    """
    try:
        # Filter enrollments for the user with status 'in_progress'
        enrollments_in_progress = Enrollment.objects.filter(user_id=user_id, completion_status='in_progress')
        
        # Get course details for each enrollment
        courses_in_progress = []
        for enrollment in enrollments_in_progress:
            course = enrollment.course
            instructor = course.instructor
            courses_in_progress.append({
                'course_id': course.id,
                'course_title': course.title,
                'course_description': course.description,
                'course_image': course.course_image.url if course.course_image else None,  # Handle missing image
                'instructor': {
                    'id': instructor.id,
                    'first_name': instructor.first_name,
                    'last_name': instructor.last_name,
                    'email': instructor.email,  # Add more fields if necessary
                },
            })

        # Return the courses the user is enrolled in with 'in_progress' status
        return Response({
            'user_id': user_id,
            'courses_in_progress': courses_in_progress
        })

    except Enrollment.DoesNotExist:
        return Response({'error': 'No enrollments found for the user.'}, status=404)
    except Exception as e:
        return Response({'error': str(e)}, status=500)


