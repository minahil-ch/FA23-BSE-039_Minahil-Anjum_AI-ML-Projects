"""Admin configuration for datasets."""

from django.contrib import admin

from .models import CleaningHistory, CleaningJob, Dataset, Report


@admin.register(Dataset)
class DatasetAdmin(admin.ModelAdmin):
    list_display = ('name', 'user', 'file_type', 'status', 'row_count', 'column_count', 'uploaded_at')
    list_filter = ('status', 'file_type', 'uploaded_at')
    search_fields = ('name', 'user__username', 'user__email')
    readonly_fields = ('id', 'uploaded_at', 'updated_at', 'analysis_result')
    ordering = ('-uploaded_at',)


class CleaningHistoryInline(admin.TabularInline):
    model = CleaningHistory
    extra = 0
    readonly_fields = ('operation', 'parameters', 'rows_affected', 'description', 'applied_at')


@admin.register(CleaningJob)
class CleaningJobAdmin(admin.ModelAdmin):
    list_display = ('id', 'dataset', 'user', 'status', 'progress', 'started_at', 'completed_at')
    list_filter = ('status', 'started_at')
    search_fields = ('dataset__name', 'user__username')
    readonly_fields = ('id', 'started_at', 'completed_at', 'before_stats', 'after_stats')
    inlines = [CleaningHistoryInline]


@admin.register(CleaningHistory)
class CleaningHistoryAdmin(admin.ModelAdmin):
    list_display = ('operation', 'job', 'rows_affected', 'applied_at')
    list_filter = ('operation', 'applied_at')
    search_fields = ('operation', 'job__dataset__name')
    readonly_fields = ('id', 'applied_at')


@admin.register(Report)
class ReportAdmin(admin.ModelAdmin):
    list_display = ('title', 'user', 'dataset', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('title', 'user__username', 'dataset__name')
    readonly_fields = ('id', 'created_at', 'summary', 'comparison')
