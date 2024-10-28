from django.urls import path
from .views import (
    CategoryDetailView,
    CategoryListCreateView,
    ChangePasswordView,
    CompleteLessonAPIView,
    CourseCreateView,
    CourseDeleteView,
    CourseEnrollAPIView,
    CourseProgressView,
    CourseSearchView,
    CourseUpdateView,
    CourseEnrollAPIView,
    LessonDetailView,
    QuizDetailView,
    RegistrationNumberAuthToken,
    AdminUserCreateView,
    CourseListView,
    CourseDetailView,
    LessonListView,
    NotificationView,
    LessonCreateView,  # Uncommented if needed
    LessonUpdateView,  # Uncommented if needed
    LessonDeleteView,  # Uncommented if needed
    QuizListView,     # Uncommented if needed
    QuizCreateView,   # Uncommented if needed
    QuizUpdateView,   # Uncommented if needed
    QuizDeleteView,
    TakeQuizAPIView,
    UpdateDetailView,
    UpdateListView,
    UserEnrolledCoursesAPIView,
    UserGradeListView,
)

urlpatterns = [
    # Auth
    path('auth/login/', RegistrationNumberAuthToken.as_view(), name='login'),
    path('auth/register/', AdminUserCreateView.as_view(), name='register'),
    path('auth/change-password/', ChangePasswordView.as_view(), name='change-password'),

    # Course-related endpoints
    path('courses/', CourseListView.as_view(), name='course-list'),
    path('courses/<int:pk>/', CourseDetailView.as_view(), name='course-detail'),
    path('courses/create/', CourseCreateView.as_view(), name='course-create'),
    path('courses/<int:pk>/update/', CourseUpdateView.as_view(), name='course-update'),
    path('courses/<int:pk>/delete/', CourseDeleteView.as_view(), name='course-delete'),
    path('courses/<int:course_id>/enroll/', CourseEnrollAPIView.as_view(), name='course-enroll'),
    path('courses/user/<int:user_id>/enrollments/', UserEnrolledCoursesAPIView.as_view(), name='user-enrolled-courses'),
    path('courses/<int:course_id>/courseprogress/mark-completed/', CourseProgressView.as_view(), name='courseprogress-mark-completed'),
    path('courses/grades/', UserGradeListView.as_view(), name='user-grades'),
    path('courses/search/', CourseSearchView.as_view(), name='course-search'),
    path('courses/categories/', CategoryListCreateView.as_view(), name='category-list-create'),
    path('courses/categories/<int:pk>/', CategoryDetailView.as_view(), name='category-detail'),
     # Lesson-related endpoints
    path('courses/<int:course_id>/lessons/', LessonListView.as_view(), name='lesson-list'),
    path('lessons/create/', LessonCreateView.as_view(), name='lesson-create'),  # Added if needed
    path('lessons/<int:id>/', LessonDetailView.as_view(), name='lesson-detail'),
    path('lessons/<int:pk>/update/', LessonUpdateView.as_view(), name='lesson-update'),  # Added if needed
    path('lessons/<int:pk>/delete/', LessonDeleteView.as_view(), name='lesson-delete'),  # Added if needed

    path('notifications/', NotificationView.as_view(), name='notification-list'),

    # Quiz-related endpoints (uncomment if needed)
    path('quizzes/', QuizListView.as_view(), name='quiz-list'),  # List all quizzes
    path('quizzes/create/', QuizCreateView.as_view(), name='quiz-create'),  # Create a new quiz
    path('quizzes/<int:pk>/', QuizDetailView.as_view(), name='quiz-detail'),  # Retrieve quiz details by ID
    path('quizzes/<int:quiz_id>/take/', TakeQuizAPIView.as_view(), name='take-quiz'),
    path('quizzes/<int:pk>/update/', QuizUpdateView.as_view(), name='quiz-update'),  # Update a quiz
    path('quizzes/<int:pk>/delete/', QuizDeleteView.as_view(), name='quiz-delete'),  # Delete a quiz
    
    path('updates/', UpdateListView.as_view(), name='update-list'),               # List all updates or create a new one
    path('updates/<int:pk>/', UpdateDetailView.as_view(), name='update-detail'),  # Retrieve, update, or delete a specific update
]