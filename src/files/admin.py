from django.contrib import admin

# Register your models here.
from django.utils.html import format_html

from files.models import CompanyFile, CompanyFileResult, TransporterFileResults, TransporterFile

''' COMPANY FILES -> RESULTS '''
class CustomCompanyFileResults(admin.TabularInline):

    model = CompanyFileResult

''' COMPANY FILES '''
class CustomCompanyFile(admin.ModelAdmin):

    list_display = ['name', 'company']
    list_filter = ['company']
    inlines = [CustomCompanyFileResults]
    model = CompanyFile

admin.site.register(CompanyFile, CustomCompanyFile)


''' TRANSPORTER FILE -> RESULTS '''
class CustomTransporterFileResults(admin.TabularInline):

        model = TransporterFileResults

''' TRANSPORTER FILES '''

class CustomTransporterFile(admin.ModelAdmin):


        list_display = ['name', 'transporter']
        list_filter = ['transporter']
        inlines = [CustomTransporterFileResults]
        model = TransporterFile




admin.site.register(TransporterFile, CustomTransporterFile)

