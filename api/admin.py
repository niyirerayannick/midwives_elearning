from django.contrib import admin
from django.utils.html import format_html
from .models import (
    HealthProviderUser, Category, Course, Lesson, Quiz, Question, Answer, Update,
    UserAnswer, Exam, Certificate, Enrollment, Progress, Grade, Notification
)
from django.contrib.auth.admin import UserAdmin

class HealthProviderUserAdmin(UserAdmin):
    model = HealthProviderUser

    # Fields to display in the admin list view
    list_display = (
        'registration_number', 'first_name', 'last_name', 'email', 
        'telephone', 'date_of_birth', 'role', 'is_staff', 'is_active'
    )

    # Fields to use for search
    search_fields = ('registration_number', 'first_name', 'last_name', 'email')

    # Filters for role and staff status
    list_filter = ('role', 'is_staff', 'is_active')

    # Display all fields in the form when adding/editing users
    fieldsets = (
        (None, {'fields': ('password',)}),  # No username field as per model
        ('Personal Info', {'fields': ('first_name', 'last_name', 'email', 'telephone', 'date_of_birth')}),
        ('Role Info', {'fields': ('role', 'registration_number')}),  # registration_number added here
        ('Permissions', {'fields': ('is_staff', 'is_active', 'is_superuser', 'groups', 'user_permissions')}),
        ('Important dates', {'fields': ('last_login', 'date_joined')}),
    )

    # Fields to display when creating a new user
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('password1', 'password2', 'first_name', 'last_name', 'email', 'telephone', 'date_of_birth', 'role', 'registration_number'),
        }),
    )

    ordering = ('registration_number',)

# Register the custom user model with the admin
admin.site.register(HealthProviderUser, HealthProviderUserAdmin)

# Customize Course model in the admin panel
@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ('title', 'instructor', 'created_at', 'cpd')
    list_filter = ('category', 'instructor', 'created_at')
    search_fields = ('title', 'description')
    autocomplete_fields = ['instructor']
    readonly_fields = ['created_at']

# Customize Lesson model in the admin panel
@admin.register(Lesson)
class LessonAdmin(admin.ModelAdmin):
    list_display = ('title', 'course', 'created_at')
    search_fields = ('title', 'course__title')
    list_filter = ('course',)
    readonly_fields = ['created_at']

# Customize Quiz model in the admin panel
@admin.register(Quiz)
class QuizAdmin(admin.ModelAdmin):
    list_display = ('title', 'course', 'total_marks')
    list_filter = ('course',)
    search_fields = ('title', 'course__title')

# Customize Question model in the admin panel
@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ('text', 'quiz', 'is_multiple_choice')
    list_filter = ('quiz', 'is_multiple_choice')
    search_fields = ('text', 'quiz__title')

# Customize Answer model in the admin panel
@admin.register(Answer)
class AnswerAdmin(admin.ModelAdmin):
    list_display = ('text', 'question', 'is_correct')
    list_filter = ('is_correct', 'question__quiz')
    search_fields = ('text', 'question__text')

# Customize Certificate model in the admin panel
@admin.register(Certificate)
class CertificateAdmin(admin.ModelAdmin):
    list_display = ('user', 'course', 'date_issued')
    list_filter = ('course', 'date_issued')
    search_fields = ('user__registration_number', 'course__title')

# Customize Enrollment model in the admin panel
@admin.register(Enrollment)
class EnrollmentAdmin(admin.ModelAdmin):
    list_display = ('user', 'course', 'date_enrolled')
    list_filter = ('course', 'date_enrolled')
    search_fields = ('user__registration_number', 'course__title')

# Customize Progress model in the admin panel
@admin.register(Progress)
class ProgressAdmin(admin.ModelAdmin):
    list_display = ('user', 'course', 'total_lessons')
    search_fields = ('user__registration_number', 'course__title')

# Customize Grade model in the admin panel
@admin.register(Grade)
class GradeAdmin(admin.ModelAdmin):
    list_display = ('user', 'course', 'score', 'total_score')
    list_filter = ('course',)
    search_fields = ('user__registration_number', 'course__title')

# Customize Notification model in the admin panel
@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ('user', 'message', 'created_at', 'is_read')
    list_filter = ('is_read', 'created_at')
    search_fields = ('user__registration_number', 'message')

# Customize Category model in the admin panel
@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)

class UpdateAdmin(admin.ModelAdmin):
    list_display = ('title', 'author', 'created_at', 'updated_at')  # Fields to display in the list view
    search_fields = ('title', 'content')  # Fields to search in the admin
    prepopulated_fields = {'title': ('content',)}  # Automatically fill the title field based on the content (optional)

admin.site.register(Update, UpdateAdmin)