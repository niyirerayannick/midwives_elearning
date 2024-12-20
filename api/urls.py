from django.urls import path
from .views import (
    CategoryDetailView,
    CategoryListCreateView,
    CertificateListView,
    ChangePasswordView,
    CommentListCreateView,
    CommentRetrieveUpdateDestroyView,
    CompleteLessonAPIView,
    CompletedCoursesView,
    CourseCreateView,
    CourseDeleteView,
    CourseEnrollAPIView,
    CourseProgressView,
    CourseSearchView,
    CourseUpdateView,
    CourseEnrollAPIView,
    CoursesInProgressView,
    ExamListCreateView,
    ExamRetrieveUpdateDeleteView,
    GetUserGrades,
    LessonDetailView,
    LikeUpdateView,
    PasswordResetConfirmView,
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
    SendOtpForPasswordResetView,
    SkillListCreateView,
    SkillRetrieveUpdateDestroyView,
    TakeExamAPIView,
    TakeQuizAPIView,
    UpdateDetailView,
    UpdateListView,
    UserCertificateListView,
    UserEnrolledCoursesAPIView,
    UserProfileView,
    VerifyOtpView,
)
from api import views


urlpatterns = [
    # Auth
    path('auth/login/', RegistrationNumberAuthToken.as_view(), name='login'),
    path('auth/register/', AdminUserCreateView.as_view(), name='register'),
    path('auth/change-password/', ChangePasswordView.as_view(), name='change-password'),
    path('auth/profile/<int:user_id>/', UserProfileView.as_view(), name='user-profile'),
    path('auth/send-otp/', SendOtpForPasswordResetView.as_view(), name='send-otp'),
    path('auth/verify-otp/', VerifyOtpView.as_view(), name='verify-otp'),
    path('auth/reset-password/', PasswordResetConfirmView.as_view(), name='reset-password'),

    path('emergency/', views.get_emergency_courses, name='get_emergency_courses'),
    path('emergency/<int:emergency_id>/', views.get_single_emergency, name='get_single_emergency'),
    # Course-related endpoints
    path('courses/', CourseListView.as_view(), name='course-list'),
    path('courses/<int:pk>/', CourseDetailView.as_view(), name='course-detail'),
    path('courses/create/', CourseCreateView.as_view(), name='course-create'),
    path('courses/<int:pk>/update/', CourseUpdateView.as_view(), name='course-update'),
    path('courses/<int:pk>/delete/', CourseDeleteView.as_view(), name='course-delete'),
    path('courses/<int:course_id>/enroll/', CourseEnrollAPIView.as_view(), name='course-enroll'),
    path('courses/user/<int:user_id>/enrollments/', UserEnrolledCoursesAPIView.as_view(), name='user-enrolled-courses'),
    # path('courses/{exam_id}/users/{user_id}/complete/', views.mark_exam_completed, name='user-completed-courses'),
    path('exams/<int:exam_id>/users/<int:user_id>/complete/', views.mark_exam_completed, name='mark-exam-completed'),
    path('courses/<int:course_id>/courseprogress/mark-completed/', CourseProgressView.as_view(), name='courseprogress-mark-completed'),
    path('courses/search/', CourseSearchView.as_view(), name='course-search'),
    path('courses/categories/', CategoryListCreateView.as_view(), name='category-list-create'),
    path('courses/categories/<int:pk>/', CategoryDetailView.as_view(), name='category-detail'),
    path('courses/<int:course_id>/quizzes/', views.get_quiz_by_course, name='get_quiz_by_course'),
    path('courses/<int:course_id>/exams/', views.get_exam_by_course, name='get_exam_by_course'),
    path('courses/user/certificates/', CertificateListView.as_view(), name='certificate-list'),
    path('courses/completed-courses/<int:user_id>/', CompletedCoursesView.as_view(), name='completed-courses'),
    path('courses/in-progress-courses/<int:user_id>/', CoursesInProgressView.as_view(), name='in-progress-courses'),
    # path('courses/<int:user_id>/grade/', views.get_user_grades, name='user-course-grade'),
    path('courses/grades/<int:user_id>/', GetUserGrades.as_view(), name='get_user_grades'),
    path('courses/<int:course_id>/users/<int:user_id>/grades/', views.get_course_grades, name='user-course-grade'),
    path('courses/<int:course_id>/enrollments/', views.get_course_enrollments, name='course-enrollments'),
    # path('courses/users/<int:user_id>/in-progress-courses/', views.get_in_progress_courses, name='in-progress-courses'),
    path('courses/in-progress/<int:user_id>/', views.get_courses_in_progress, name='get-courses-in-progress'),
    # path('courses/completed/<int:user_id>/', views.get_courses_completed, name='get_courses_completed'),
    # CRUD for Skillscompleted-courses
    path('skills/', SkillListCreateView.as_view(), name='skill_list_create'),
    path('skills/<int:pk>/', SkillRetrieveUpdateDestroyView.as_view(), name='skill_detail'),    
     # Lesson-related endpoints
    path('courses/<int:course_id>/lessons/', LessonListView.as_view(), name='lesson-list'),
    path('lessons/create/', LessonCreateView.as_view(), name='lesson-create'),  # Added if needed
    path('lessons/<int:id>/', LessonDetailView.as_view(), name='lesson-detail'),
    path('lessons/<int:pk>/update/', LessonUpdateView.as_view(), name='lesson-update'),  # Added if needed
    path('lessons/<int:pk>/delete/', LessonDeleteView.as_view(), name='lesson-delete'),  # Added if needed
    path('lessons/<int:lesson_id>/complete/<int:user_id>/', views.complete_lesson, name='complete_lesson'),
    path('notifications/', NotificationView.as_view(), name='notification-list'),
    # Quiz-related endpoints (uncomment if needed)
    path('quizzes/', QuizListView.as_view(), name='quiz-list'),  # List all quizzes
    path('quizzes/create/', QuizCreateView.as_view(), name='quiz-create'),  # Create a new quiz
    path('quizzes/<int:pk>/', QuizDetailView.as_view(), name='quiz-detail'),  # Retrieve quiz details by ID
    path('quizzes/<int:quiz_id>/take/', TakeQuizAPIView.as_view(), name='take-quiz'),
    path('quizzes/<int:quiz_id>/retake/', TakeQuizAPIView.as_view(), name='retake-quiz'),  # New endpoint for retaking the quiz
    path('quizzes/<int:pk>/update/', QuizUpdateView.as_view(), name='quiz-update'),  # Update a quiz
    path('quizzes/<int:pk>/delete/', QuizDeleteView.as_view(), name='quiz-delete'),  # Delete a quiz
    path('quizzes/<int:quiz_id>/<int:user_id>/complete/', views.complete_quiz, name='complete_quiz'),

    path('exams/', ExamListCreateView.as_view(), name='exam-list-create'),
    path('exams/<int:pk>/', ExamRetrieveUpdateDeleteView.as_view(), name='exam-detail-update-delete'),
    # path('exams/<int:exam_id>/take/', views.TakeExamAPIView.as_view(), name='take_exam'),
    # path('exams/<int:exam_id>/retake/', views.TakeExamAPIView.as_view(), name='retake_exam'),
    path('exams/completing /exam/<int:exam_id>/complete/', views.complete_exam, name='complete_exam'),
    path('exams/user/<int:user_id>/certificates/', UserCertificateListView.as_view(), name='user-certificates'),
    path('exams/<int:exam_id>/take/<int:user_id>/', views.take_exam, name='take_exam'),
    path('exams/<int:exam_id>/retake_exam/<int:user_id>/', views.retake_exam, name='retake_exam'),
    path('exams/<int:exam_id>/submit/<int:user_id>/', views.submit_exam, name='submit_exam'),
    path('exams/<int:exam_id>/certificate/<int:user_id>/', views.get_user_certificate, name='get_user_certificate'),
    path('updates/', UpdateListView.as_view(), name='update-list'),               # List all updates or create a new one
    path('updates/<int:pk>/', UpdateDetailView.as_view(), name='update-detail'),  # Retrieve, update, or delete a specific update
    path('updates/<int:update_id>/comments/', CommentListCreateView.as_view(), name='comment_list_create'),  # List and create comments
    path('updates/<int:update_id>/comments/<int:pk>/', CommentRetrieveUpdateDestroyView.as_view(), name='comment_detail'),  # Retrieve, update, delete a comment
    # Like or unlike an update
    path('updates/<int:update_id>/like/', LikeUpdateView.as_view(), name='like_update'),
    # Existing paths for completing lessons, quizzes, and exams
    # New path for checking user progress in a course
    # path('yannick/course/<int:course_id>/progress/<int:user_id>/', views.get_course_progress, name='check_user_progress'),
    path('completing /course/<int:course_id>/progress/<int:user_id>/', views.get_user_course_progress, name='check_user_progress'),
]
