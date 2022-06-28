from django.contrib import admin

# Register your models here.
from supplements.models import Supplement, Weight, TransporterImplementation, WeightPrices


class AdminTransporterImplementation(admin.TabularInline):
    model = TransporterImplementation

class CustomSupplementAdminView(admin.ModelAdmin):

    list_display = ['company', 'transporter']
    list_filter = ['company']
    inlines = [AdminTransporterImplementation]
    model = Supplement

admin.site.register(Supplement, CustomSupplementAdminView)

class WeightPricesAdminView(admin.TabularInline):
    model = WeightPrices

class WeightAdminView(admin.ModelAdmin):

    list_display = ['company', 'transporter']
    list_filter = ['company']
    inlines = [WeightPricesAdminView]
    model = Weight

admin.site.register(Weight, WeightAdminView)