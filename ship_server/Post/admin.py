from django.contrib import admin
from .models import Question, Answer, Notice


class AnswerInline(admin.TabularInline):
    model = Answer


class QuestionAdmin(admin.ModelAdmin):
    list_display = (
        'id', 'writer', 'title', 'content', 'date', 'status'
    )
    inlines = [AnswerInline, ]


class AnswerAdmin(admin.ModelAdmin):
    list_display = (
        'id', 'q_id', 'date', 'answer'
    )


class NoticeAdmin(admin.ModelAdmin):
    list_display = (
        'id', 'title', 'content', 'types', 'date',
    )


admin.site.register(Question, QuestionAdmin)
admin.site.register(Answer, AnswerAdmin)
admin.site.register(Notice, NoticeAdmin)
