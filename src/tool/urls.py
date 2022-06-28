from django.urls import path
from django.views.generic import TemplateView

from reports.views import create_report, display_all_reports, display_single_report, display_chart_transporter_costs, \
    download_report
from supplements.views import see_supplements_per_company, edit_transporter
from tool.views import index

app_name = "tool"

urlpatterns = [
    path('', index, name="index"),
    #Transporters (Supplement)
    path('transporters/', see_supplements_per_company, name="transporters"),
    path('transporters/<str:slug>/edit', edit_transporter, name="edit-transporter"),
    #Reports
    path('reports/create-report/', create_report, name="create-report"),
    path('reports/', display_all_reports, name="reports"),
    path('reports/<slug:slug>', display_single_report, name="single-report"),
    path('reports/download-report/', download_report, name="download-report"),
    #Charts
    path('charts/', display_chart_transporter_costs, name="chart-transporters")
    ]