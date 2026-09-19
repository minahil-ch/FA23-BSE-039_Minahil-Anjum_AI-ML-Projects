from django.contrib import admin
from .models import Candidate


@admin.register(Candidate)
class CandidateAdmin(admin.ModelAdmin):
    list_display = ("candidate_id", "full_name", "email", "status",
                     "preferred_department", "experience_years", "application_date")
    list_filter = ("status", "preferred_department", "gender")
    search_fields = ("first_name", "last_name", "email", "candidate_id")
    actions = ["mark_selected", "mark_rejected"]

    def full_name(self, obj):
        return obj.full_name

    @admin.action(description="Mark selected candidates as SELECTED")
    def mark_selected(self, request, queryset):
        queryset.update(status=Candidate.Status.SELECTED)

    @admin.action(description="Mark selected candidates as REJECTED")
    def mark_rejected(self, request, queryset):
        queryset.update(status=Candidate.Status.REJECTED)
