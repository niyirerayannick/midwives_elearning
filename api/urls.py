from django.urls import path
from .views import (
    ChangePasswordView,
    CompleteLessonAPIView,
    CourseCreateView,
    CourseDeleteView,
    CourseEnrollAPIView,
    CourseUpdateView,
    CourseEnrollAPIView,
    RegistrationNumberAuthToken,
    AdminUserCreateView,
    CourseListView,
    CourseDetailView,
    LessonListView,
    ProgressView,
    NotificationView,
    LessonCreateView,  # Uncommented if needed
    LessonUpdateView,  # Uncommented if needed
    LessonDeleteView,  # Uncommented if needed
    QuizListView,     # Uncommented if needed
    QuizCreateView,   # Uncommented if needed
    QuizUpdateView,   # Uncommented if needed
    QuizDeleteView,
    UserEnrolledCoursesAPIView,
    UserProgressAPIView    # Uncommented if needed

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
    path('courses/<int:course_id>/lessons/<int:lesson_id>/complete/', CompleteLessonAPIView.as_view(), name='complete-lesson'),
    path('courses/users/<int:user_id>/progress/<int:course_id>/', UserProgressAPIView.as_view(), name='user-progress'),

    # Lesson-related endpoints
    path('courses/<int:course_id>/lessons/', LessonListView.as_view(), name='lesson-list'),
    path('lessons/create/', LessonCreateView.as_view(), name='lesson-create'),  # Added if needed
    path('lessons/<int:pk>/update/', LessonUpdateView.as_view(), name='lesson-update'),  # Added if needed
    path('lessons/<int:pk>/delete/', LessonDeleteView.as_view(), name='lesson-delete'),  # Added if needed

    # path('courses/<int:course_id>/progress/', ProgressView.as_view(), name='course-progress'),
    path('courses/progress/<int:user_id>/<int:course_id>/', ProgressView.as_view(), name='user-progress'),
    path('notifications/', NotificationView.as_view(), name='notification-list'),

    # Quiz-related endpoints (uncomment if needed)
    path('quizzes/', QuizListView.as_view(), name='quiz-list'),  # Added if needed
    path('quizzes/create/', QuizCreateView.as_view(), name='quiz-create'),  # Added if needed
    path('quizzes/<int:pk>/update/', QuizUpdateView.as_view(), name='quiz-update'),  # Added if needed
    path('quizzes/<int:pk>/delete/', QuizDeleteView.as_view(), name='quiz-delete')  # Added if needed
]
