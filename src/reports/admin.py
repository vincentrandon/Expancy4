from django.contrib import admin

# Register your models here.
from reports.models import Report, ReportResults


class CustomReportResults(admin.TabularInline):
    model = ReportResults

class CustomReportAdminView(admin.ModelAdmin):
    list_display = ['title', 'company']
    list_filter = ['company']
    inlines = [CustomReportResults]
    model = Report


admin.site.register(Report, CustomReportAdminView)