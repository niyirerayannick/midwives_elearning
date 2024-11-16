from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import (
    ExamAnswer, ExamQuestion, HealthProviderUser, Category, Skill, Course, Lesson, Quiz, Question, Answer,
    Exam, Certificate, Enrollment, Progress, Grade, Notification, Update, 
    Comment, Like, ExamUserAnswer, QuizUserAnswer
)
from .models import Emergency, EmergencyFile

@admin.register(Emergency)
class EmergencyAdmin(admin.ModelAdmin):
    list_display = ['title', 'description', 'created_at']
    search_fields = ['title', 'description']

@admin.register(EmergencyFile)
class EmergencyFileAdmin(admin.ModelAdmin):
    list_display = ['emergency', 'file_type', 'description']
    search_fields = ['emergency__title', 'file_type']

@admin.register(ExamQuestion)
class ExamQuestionAdmin(admin.ModelAdmin):
    list_display = ('text', 'exam', 'is_multiple_choice')


@admin.register(ExamAnswer)
class ExamAnswerAdmin(admin.ModelAdmin):
    list_display = ('text', 'question', 'is_correct')


class HealthProviderUserAdmin(BaseUserAdmin):
    fieldsets = (
        (None, {'fields': ('registration_number', 'password')}),
        ('Personal info', {'fields': ('first_name', 'last_name', 'email', 'telephone', 'date_of_birth', 'profile_image')}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Role Info', {'fields': ('role',)}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('registration_number', 'password1', 'password2', 'role', 'email')}
        ),
    )
    list_display = ('registration_number', 'first_name', 'last_name', 'email', 'role', 'is_staff')
    search_fields = ('registration_number', 'first_name', 'last_name', 'email')
    ordering = ('registration_number',)

admin.site.register(HealthProviderUser, HealthProviderUserAdmin)

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'description')
    search_fields = ('name',)

@admin.register(Skill)
class SkillAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)

@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ('title', 'instructor', 'created_at', 'cpd')
    list_filter = ('category', 'instructor')
    search_fields = ('title', 'description')
    filter_horizontal = ('skills',)

@admin.register(Lesson)
class LessonAdmin(admin.ModelAdmin):
    list_display = ('title', 'course', 'created_at')
    list_filter = ('course',)
    search_fields = ('title',)

@admin.register(Quiz)
class QuizAdmin(admin.ModelAdmin):
    list_display = ('title', 'course', 'total_marks')
    list_filter = ('course',)
    search_fields = ('title',)

@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ('text', 'quiz', 'is_multiple_choice')
    list_filter = ('quiz',)
    search_fields = ('text',)

@admin.register(Answer)
class AnswerAdmin(admin.ModelAdmin):
    list_display = ('text', 'question', 'is_correct')
    list_filter = ('question',)
    search_fields = ('text',)

@admin.register(Exam)
class ExamAdmin(admin.ModelAdmin):
    list_display = ('title', 'course', 'total_marks')
    list_filter = ('course',)
    search_fields = ('title',)


@admin.register(Enrollment)
class EnrollmentAdmin(admin.ModelAdmin):
    list_display = ('user', 'course', 'date_enrolled')
    list_filter = ('course', 'user')
    search_fields = ('user__registration_number', 'course__title')

@admin.register(Progress)
class ProgressAdmin(admin.ModelAdmin):
    list_display = ('user', 'course', 'total_lessons')
    list_filter = ('course',)
    search_fields = ('user__registration_number', 'course__title')

@admin.register(Grade)
class GradeAdmin(admin.ModelAdmin):
    list_display = ('user', 'course', 'score', 'total_score')
    list_filter = ('course',)
    search_fields = ('user__registration_number', 'course__title')

@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ('user', 'message', 'created_at', 'is_read')
    list_filter = ('is_read',)
    search_fields = ('user__registration_number', 'message')

@admin.register(Update)
class UpdateAdmin(admin.ModelAdmin):
    list_display = ('title', 'author', 'created_at', 'updated_at')
    search_fields = ('title', 'author__registration_number')

@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ('update', 'author', 'created_at')
    search_fields = ('author__registration_number', 'update__title')

@admin.register(Like)
class LikeAdmin(admin.ModelAdmin):
    list_display = ('update', 'user', 'created_at')
    search_fields = ('user__registration_number', 'update__title')

@admin.register(ExamUserAnswer)
class ExamUserAnswerAdmin(admin.ModelAdmin):
    list_display = ('user', 'exam', 'question', 'selected_answer', 'is_correct')
    search_fields = ('user__registration_number', 'exam__title', 'question__text')

@admin.register(QuizUserAnswer)
class QuizUserAnswerAdmin(admin.ModelAdmin):
    list_display = ('user', 'quiz', 'question', 'selected_answer', 'is_correct')
    search_fields = ('user__registration_number', 'quiz__title', 'question__text')
