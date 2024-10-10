from django.contrib.auth.admin import UserAdmin
from .models import HealthProviderUser, Course, Lesson, Quiz, Question, Answer, Exam, Certificate, Enrollment, Progress, Notification
from django.contrib import admin

# HealthProviderUserAdmin
class HealthProviderUserAdmin(UserAdmin):
    model = HealthProviderUser

    # Fields to display in the admin list view
    list_display = ('registration_number', 'first_name', 'last_name', 'email', 'role', 'is_staff', 'is_active')

    # Fields to use for search
    search_fields = ('registration_number', 'first_name', 'last_name', 'email')

    # Filters for role and staff status
    list_filter = ('role', 'is_staff', 'is_active')

    # Fields to display in the form when adding/editing users
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        ('Personal Info', {'fields': ('first_name', 'last_name', 'email', 'telephone', 'date_of_birth')}),
        ('Role Info', {'fields': ('role', 'registration_number')}),  # registration_number added here
        ('Permissions', {'fields': ('is_staff', 'is_active', 'is_superuser', 'groups', 'user_permissions')}),
        ('Important dates', {'fields': ('last_login', 'date_joined')}),
    )

    # Fields to display when creating a new user
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'password1', 'password2', 'first_name', 'last_name', 'email', 'role', 'registration_number'),
        }),
    )

    ordering = ('registration_number',)

# Register the custom user model with the admin
admin.site.register(HealthProviderUser, HealthProviderUserAdmin)


# Register the Course model
class CourseAdmin(admin.ModelAdmin):
    list_display = ['id', 'title', 'instructor', 'created_at']
    search_fields = ['title', 'instructor__first_name', 'instructor__last_name']
    list_filter = ['instructor']

admin.site.register(Course, CourseAdmin)


# Register the Lesson model
class LessonAdmin(admin.ModelAdmin):
    list_display = ['id', 'course', 'title', 'created_at']
    search_fields = ['title', 'course__title']
    list_filter = ['course', 'created_at']

admin.site.register(Lesson, LessonAdmin)


# Register the Quiz model
class QuizAdmin(admin.ModelAdmin):
    list_display = ['id', 'course', 'title', 'total_marks']
    search_fields = ['title', 'course__title']
    list_filter = ['course']

admin.site.register(Quiz, QuizAdmin)


# Register the Question model
class QuestionAdmin(admin.ModelAdmin):
    list_display = ['id', 'quiz', 'text', 'is_multiple_choice']
    search_fields = ['text', 'quiz__title']
    list_filter = ['is_multiple_choice']

admin.site.register(Question, QuestionAdmin)


# Register the Answer model
class AnswerAdmin(admin.ModelAdmin):
    list_display = ['id', 'question', 'text', 'is_correct']
    search_fields = ['text', 'question__text']

admin.site.register(Answer, AnswerAdmin)


# Register the Exam model
class ExamAdmin(admin.ModelAdmin):
    list_display = ['id', 'course', 'title', 'total_marks']
    search_fields = ['title', 'course__title']
    list_filter = ['course']

admin.site.register(Exam, ExamAdmin)


# Register the Certificate model
class CertificateAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'course', 'date_issued']
    search_fields = ['user__username', 'course__title']

admin.site.register(Certificate, CertificateAdmin)


# Register the Enrollment model
class EnrollmentAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'course', 'date_enrolled']
    search_fields = ['user__username', 'course__title']
    list_filter = ['date_enrolled']

admin.site.register(Enrollment, EnrollmentAdmin)


# Register the Progress model
class ProgressAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'course', 'completed_lessons', 'total_lessons']
    search_fields = ['user__username', 'course__title']
    list_filter = ['course']

admin.site.register(Progress, ProgressAdmin)


# Register the Notification model
class NotificationAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'message', 'created_at', 'is_read']
    search_fields = ['user__username', 'message']
    list_filter = ['created_at', 'is_read']

admin.site.register(Notification, NotificationAdmin)
