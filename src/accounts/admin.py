from django.contrib import admin
from django.utils.html import format_html

from accounts.models import User, Company, CompanyDetailsIntegration, Brand, Transporter

''' USERS '''
class CustomUserAdmin(admin.ModelAdmin):

    def change_button(self, obj):
        return format_html('<a class="btn" href="/admin/accounts/user/{}/change/">Edit</a>', obj.id)

    list_display = ['email', 'first_name', 'last_name', 'change_button']
    #list_filter = ['email']
    model = User

admin.site.register(User, CustomUserAdmin)


''' COMPANIES -> DETAILS INTEGRATION '''

class CustomCompanyDetailsIntegrationAdmin(admin.TabularInline):
    list_display = ['company']
    list_filter = ['company']
    model = CompanyDetailsIntegration

''' COMPANIES '''

class CustomCompanyAdmin(admin.ModelAdmin):
    list_display = ['name']
    inlines = [CustomCompanyDetailsIntegrationAdmin]
    model = Company

admin.site.register(Company, CustomCompanyAdmin)

''' BRANDS '''

class CustomBrandAdmin(admin.ModelAdmin):

    list_display = ['name', 'company']
    list_filter = ['company']
    model = Brand

admin.site.register(Brand, CustomBrandAdmin)

''' TRANSPORTERS '''

class CustomTransporterAdmin(admin.ModelAdmin):

    list_display = ['name']
    model = Transporter

admin.site.register(Transporter, CustomTransporterAdmin)
